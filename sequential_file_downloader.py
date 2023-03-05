import os
import requests
import time
import re

while True:
  # Get the URL template from the user
  url_template = input("Enter the URL template: ")

  # Validate the URL template
  if not re.match(r'^https?://.*?(\d+)[a-zA-Z0-9_\-]*\.[a-zA-Z0-9_\-\.]+$', url_template):
    print("Error: Invalid URL template. The URL should be correct and contain numerical characters in the file name.\nExample: https://www.example.com/files/file_1.jpg")
    continue

  # Exit the loop if a valid URL template is entered
  break

# Get the download directory from the user (default is "downloads" if left blank)
while True:
  download_dir = input("Enter the download directory (leave blank for default option \"downloads\", note that if the directory or file already exists it will be overwritten): ") or "downloads"

  # Validate the download directory name
  if not re.match(r'^[\w\- ]+$', download_dir):
    print("Error: Invalid directory name. Please enter a valid directory name.\nThe directory name should only contain alphanumeric characters, hyphens, and spaces.")
    continue

  # Exit the loop if a valid directory name is entered
  break

def calculate_download_speed(start_time, end_time, downloaded_bytes):
    download_time = end_time - start_time
    download_speed = downloaded_bytes / download_time / 1024 # KB/s
    return download_speed

def download_file(url):
    # Get the file name and extension from the URL
    file_name = url.split('/')[-1]
    extension = file_name.split('.')[-1]
    num = file_name.split('.')[0]

    # Create the file path
    file_path = os.path.join(download_dir, file_name)

    # Start the download and measure the time
    start_time = time.time()
    try:
        response = requests.get(url, stream=True)
    except requests.exceptions.RequestException:
        print("Connection error: Please check your internet connection.")
        return None
    end_time = time.time()

    # If the download is successful
    if response.status_code == 200:
        # Save the file to the download directory
        with open(file_path, "wb") as f:
            downloaded_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_bytes += len(chunk)

            # Calculate the file size and download time
            file_size = os.path.getsize(file_path) / (1024.0 * 1024) # MB
            download_time = end_time - start_time # seconds
            download_speed = calculate_download_speed(start_time, end_time, downloaded_bytes)

            # Print the information to the screen
            print(f"{file_name} ({file_size:.2f} MB) downloaded in {download_time:.2f} seconds. Download speed: {download_speed:.2f} KB/s")

            # Increment the number and create a new URL
            new_url = url.replace(file_name, str(int(num)+1)+'.'+extension)
            return new_url
    else:

    # If the download is unsuccessful, interpret the error code and print it to the screen
      error_message = {
        "404": "File not found",
        "403": "Access denied",
        "500": "Server error"
    }.get(str(response.status_code), f"Unknown error: {response.status_code}")

    print(f"{url} could not be downloaded. {error_message}")
   
    return None

# Let's create the download directory or access the directory with the same name if it already exists
os.makedirs(os.path.abspath(download_dir), exist_ok=True)

# Let's continue downloading files from the URL template until all the files are downloaded or an error occurs
while url_template:
  url_template = download_file(url_template)