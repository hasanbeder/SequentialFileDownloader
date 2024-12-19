<h1 align="center" style="border-bottom: none">
    ⭐️ Sequential File Downloader ⭐️ <br>
    <p align="center">
        <img src="sample.png" alt="Download Sample" width="600px"/>
    </p>
</h1>

A powerful and efficient Python tool for downloading sequential files in parallel. Perfect for downloading numbered files like images, documents, or any other sequential content.

<p align="center">
    <a href="#english">English</a> •
    <a href="#turkish">Türkçe</a>
</p>

<h2 id="english">English</h2>

## 🚀 Features

- ⚡️ **Parallel Downloads**: Download multiple files simultaneously
- 📦 **Memory Efficient**: Smart batch processing to handle large sequences
- 🔄 **Auto Sequence**: Automatically generates sequential URLs
- 📊 **Progress Tracking**: Real-time progress bars for each download
- 💡 **Smart Detection**: Automatically detects when sequence ends
- 🛡️ **Error Handling**: Robust error management and recovery
- 📝 **Detailed Stats**: Download speed, size, and time statistics

## 💡 Use Case Example

Imagine you're browsing an e-book site and want to download a book. The site has images of the book, and you've copied the link to the first image:

```
https://example.com/book/page_1.jpg
https://example.com/book/page_2.jpg
https://example.com/book/page_3.jpg
...
```

Instead of downloading each image manually, Sequential File Downloader will handle everything automatically!

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SequentialFileDownloader.git
cd SequentialFileDownloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

1. Run the script:
```bash
python sequential_file_downloader.py
```

2. Enter the URL template when prompted
3. Choose download directory (optional)
4. Specify number of files (or press Enter for unlimited)

## ⚙️ Configuration

```python
downloader = FileDownloader(
    timeout=30,        # Connection timeout
    chunk_size=8192,   # Download chunk size
    max_workers=3,     # Parallel downloads
    batch_size=100     # Files per batch
)
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.

---

<h2 id="turkish">Türkçe</h2>

## 🚀 Özellikler

- ⚡️ **Paralel İndirme**: Birden fazla dosyayı aynı anda indir
- 📦 **Bellek Dostu**: Akıllı grup işleme ile büyük serileri yönet
- 🔄 **Otomatik Sıralama**: Sıralı URL'leri otomatik oluştur
- 📊 **İlerleme Takibi**: Her indirme için gerçek zamanlı ilerleme çubuğu
- 💡 **Akıllı Algılama**: Seri sonunu otomatik tespit
- 🛡️ **Hata Yönetimi**: Güçlü hata yönetimi ve kurtarma
- 📝 **Detaylı İstatistik**: İndirme hızı, boyut ve süre bilgisi

## 💡 Kullanım Senaryosu

Bir e-kitap sitesinde geziniyorsunuz ve bir kitap indirmek istiyorsunuz. Sitenin kitap sayfalarının görüntüleri var ve ilk görüntünün linkini kopyaladınız:

```
https://example.com/book/sayfa_1.jpg
https://example.com/book/sayfa_2.jpg
https://example.com/book/sayfa_3.jpg
...
```

Her görüntüyü tek tek indirmek yerine, Sequential File Downloader her şeyi otomatik olarak halledecek!

## 🔧 Kurulum

1. Repo'yu klonlayın:
```bash
git clone https://github.com/kullaniciadi/SequentialFileDownloader.git
cd SequentialFileDownloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Kullanım

1. Scripti çalıştırın:
```bash
python sequential_file_downloader.py
```

2. İstendiğinde URL şablonunu girin
3. İndirme dizinini seçin (isteğe bağlı)
4. Dosya sayısını belirtin (veya sınırsız için Enter'a basın)

## ⚙️ Yapılandırma

```python
downloader = FileDownloader(
    timeout=30,        # Bağlantı zaman aşımı
    chunk_size=8192,   # İndirme parça boyutu
    max_workers=3,     # Paralel indirme sayısı
    batch_size=100     # Grup başına dosya sayısı
)
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Pull Request göndermekten çekinmeyin.

## 📝 License / Lisans

MIT License / MIT Lisansı
