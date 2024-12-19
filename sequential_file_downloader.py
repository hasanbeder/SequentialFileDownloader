import os
import requests
import time
import re
from tqdm import tqdm
import concurrent.futures
from typing import List, Optional, Dict, Generator, Tuple
from dataclasses import dataclass
from queue import Queue
import threading
from urllib.parse import urlparse, unquote
import logging

@dataclass
class DownloadResult:
    """Class to store download result information"""
    success: bool
    url: str
    file_name: str
    file_size: float = 0
    download_time: float = 0
    download_speed: float = 0
    error_message: str = ""

class URLParser:
    """Class to handle URL parsing and validation"""
    @staticmethod
    def parse_url(url: str) -> Tuple[bool, str, Optional[str], Optional[str], Optional[int]]:
        """
        Parse and validate URL
        Returns: (is_valid, error_message, file_name, extension, number)
        """
        try:
            # Basic URL validation
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False, "Invalid URL format", None, None, None

            # Get filename from URL
            path = unquote(parsed.path)
            if not path or path.endswith('/'):
                return False, "URL must contain a filename", None, None, None

            file_name = os.path.basename(path)
            if not file_name:
                return False, "Could not extract filename from URL", None, None, None

            # Split filename and validate
            parts = file_name.rsplit('.', 1)
            if len(parts) != 2:
                return False, "Filename must have an extension", None, None, None

            name, extension = parts
            
            # Find the number in the filename
            number_match = re.search(r'(\d+)', name)
            if not number_match:
                return False, "Filename must contain a number", None, None, None

            try:
                number = int(number_match.group(1))
                return True, "", file_name, extension, number
            except ValueError:
                return False, "Could not parse number in filename", None, None, None

        except Exception as e:
            return False, f"URL parsing error: {str(e)}", None, None, None

class FileDownloader:
    def __init__(self, timeout=30, chunk_size=8192, max_workers=3, batch_size=100):
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.download_dir = "downloads"
        self.url_template = None
        self.progress_bars: Dict[str, tqdm] = {}
        self.progress_lock = threading.Lock()
        self.url_parser = URLParser()

    def get_url_template(self):
        """Get and validate URL template from user"""
        while True:
            url_template = input("Enter the URL template: ").strip()
            is_valid, error_msg, _, _, _ = self.url_parser.parse_url(url_template)
            
            if not is_valid:
                print(f"Error: {error_msg}")
                print("Example: https://www.example.com/files/file_1.jpg")
                continue
            
            self.url_template = url_template
            break

    def get_download_directory(self):
        """Get and validate download directory from user"""
        while True:
            download_dir = input('Enter the download directory (leave blank for default option "downloads"): ') or "downloads"
            if not re.match(r'^[\w\- ]+$', download_dir):
                print("Error: Invalid directory name. Please enter a valid directory name.\nThe directory name should only contain alphanumeric characters, hyphens, and spaces.")
                continue
            self.download_dir = download_dir
            break

    def get_max_files(self) -> int:
        """Get the number of files to download"""
        while True:
            try:
                num = input("Enter the number of files to download (or press Enter for unlimited): ").strip()
                if not num:
                    return float('inf')
                num = int(num)
                if num <= 0:
                    print("Please enter a positive number")
                    continue
                return num
            except ValueError:
                print("Please enter a valid number")

    def setup_download_directory(self):
        """Create download directory if it doesn't exist"""
        os.makedirs(os.path.abspath(self.download_dir), exist_ok=True)

    def calculate_download_speed(self, start_time, end_time, downloaded_bytes):
        """Calculate download speed in KB/s"""
        download_time = end_time - start_time
        return downloaded_bytes / download_time / 1024  # KB/s

    def generate_url_batch(self, start_number: int, batch_size: int) -> Generator[str, None, None]:
        """Generate URLs in batches to save memory"""
        is_valid, _, file_name, extension, number = self.url_parser.parse_url(self.url_template)
        if not is_valid:
            return

        # Find the position of the number in the filename
        number_pos = file_name.find(str(number))
        if number_pos == -1:
            return

        # Generate URLs one at a time
        for i in range(batch_size):
            current_number = start_number + i
            new_file_name = (
                file_name[:number_pos] + 
                str(current_number) + 
                file_name[number_pos + len(str(number)):]
            )
            yield self.url_template.replace(file_name, new_file_name)

    def download_file(self, url: str) -> DownloadResult:
        """Download a single file"""
        try:
            file_name = url.split('/')[-1]
            file_path = os.path.join(self.download_dir, file_name)
            start_time = time.time()

            try:
                response = requests.get(url, stream=True, timeout=self.timeout)
            except requests.exceptions.RequestException as e:
                return DownloadResult(
                    success=False,
                    url=url,
                    file_name=file_name,
                    error_message=f"Connection error: {str(e)}"
                )

            if response.status_code == 200:
                try:
                    total_size = int(response.headers.get('content-length', 0))
                    
                    with self.progress_lock:
                        progress_bar = tqdm(
                            total=total_size,
                            unit='iB',
                            unit_scale=True,
                            desc=f'Downloading {file_name}'
                        )
                        self.progress_bars[file_name] = progress_bar

                    with open(file_path, "wb") as f:
                        downloaded_bytes = 0
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                size = len(chunk)
                                f.write(chunk)
                                with self.progress_lock:
                                    progress_bar.update(size)
                                downloaded_bytes += size

                    with self.progress_lock:
                        progress_bar.close()
                        self.progress_bars.pop(file_name, None)

                    end_time = time.time()
                    file_size = os.path.getsize(file_path) / (1024.0 * 1024)  # MB
                    download_time = end_time - start_time
                    download_speed = self.calculate_download_speed(start_time, end_time, downloaded_bytes)

                    return DownloadResult(
                        success=True,
                        url=url,
                        file_name=file_name,
                        file_size=file_size,
                        download_time=download_time,
                        download_speed=download_speed
                    )

                except IOError as e:
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
                    return DownloadResult(
                        success=False,
                        url=url,
                        file_name=file_name,
                        error_message=f"Failed to write file: {str(e)}"
                    )
            else:
                error_message = self._get_error_message(response.status_code)
                return DownloadResult(
                    success=False,
                    url=url,
                    file_name=file_name,
                    error_message=error_message
                )

        except Exception as e:
            return DownloadResult(
                success=False,
                url=url,
                file_name=file_name,
                error_message=f"Unexpected error: {str(e)}"
            )

    def download_batch(self, start_number: int, batch_size: int) -> Tuple[int, int, bool]:
        """Download a batch of files and return (successful, failed, should_continue)"""
        successful_downloads = 0
        failed_downloads = 0
        consecutive_failures = 0

        # Create URL generator for this batch
        urls = self.generate_url_batch(start_number, batch_size)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit jobs as generator yields URLs
            future_to_url = {}
            for url in urls:
                future = executor.submit(self.download_file, url)
                future_to_url[future] = url

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                self._print_download_summary(result)

                if result.success:
                    successful_downloads += 1
                    consecutive_failures = 0
                else:
                    failed_downloads += 1
                    consecutive_failures += 1
                    if consecutive_failures >= 3:
                        return successful_downloads, failed_downloads, False

        return successful_downloads, failed_downloads, True

    def start_downloading(self):
        """Start the parallel download process"""
        self.get_url_template()
        self.get_download_directory()
        max_files = self.get_max_files()
        self.setup_download_directory()

        total_successful = 0
        total_failed = 0
        current_number = int(self.url_parser.parse_url(self.url_template)[4])
        
        while total_successful < max_files if max_files != float('inf') else True:
            # Calculate batch size for this iteration
            remaining = max_files - total_successful if max_files != float('inf') else self.batch_size
            current_batch_size = min(self.batch_size, remaining)

            print(f"\nStarting batch download (files {current_number} to {current_number + current_batch_size - 1})...")
            
            successful, failed, should_continue = self.download_batch(current_number, current_batch_size)
            
            total_successful += successful
            total_failed += failed
            current_number += current_batch_size

            print(f"\nBatch Complete!")
            print(f"Successful downloads: {successful}")
            print(f"Failed downloads: {failed}")
            
            if not should_continue:
                print("\nStopping: Too many consecutive failures")
                break

        print(f"\nDownload Complete!")
        print(f"Total successful downloads: {total_successful}")
        print(f"Total failed downloads: {total_failed}")
        print(f"Total files processed: {total_successful + total_failed}")

    def _print_download_summary(self, result: DownloadResult):
        """Print download summary"""
        if result.success:
            print(f"\nDownload Summary for {result.file_name}:")
            print(f"Size: {result.file_size:.2f} MB")
            print(f"Time: {result.download_time:.2f} seconds")
            print(f"Speed: {result.download_speed:.2f} KB/s")
        else:
            print(f"\nDownload Failed for {result.file_name}:")
            print(f"Error: {result.error_message}")

    def _get_error_message(self, status_code):
        """Get error message for HTTP status code"""
        error_messages = {
            "400": "Bad request",
            "401": "Unauthorized access",
            "403": "Access forbidden",
            "404": "File not found",
            "408": "Request timeout",
            "429": "Too many requests",
            "500": "Internal server error",
            "502": "Bad gateway",
            "503": "Service unavailable",
            "504": "Gateway timeout"
        }
        return error_messages.get(str(status_code), f"Unknown error: {status_code}")

def main():
    downloader = FileDownloader(max_workers=3)  # 3 paralel indirme
    downloader.start_downloading()

if __name__ == "__main__":
    main()