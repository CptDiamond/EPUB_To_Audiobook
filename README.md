# 📚 EPUB to Audiobook Converter

An ultra-fast, asynchronous Python command-line utility that extracts chapters from `.epub` e-books and compiles them into beautifully voiced, high-quality `.mp3` audiobooks using **Edge TTS** and **FFmpeg**.

## ✨ Key Features
- **High-Speed Asynchronous Processing:** Uses `asyncio` parallel task workers to download chapter chunks simultaneously, maximizing network performance.
- **Smart Formatting Detection:** Automatically isolates code blocks and strips unwanted HTML/navigation data for clean narration.
- **Fault-Tolerant Streaming:** Features built-in automatic request retries to handle server-side drops seamlessly.

## 🚀 Prerequisites
This project requires **FFmpeg** to handle the stitching and generation of MP3 files.
- **Windows:** Download from [Gyan.dev](https://gyan.dev) and add its `/bin` directory to your System Environment Path.
- **Mac:** Run `brew install ffmpeg`
- **Linux:** Run `sudo apt install ffmpeg`

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd epub-to-audiobook
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 How To Use

Run the converter by pointing it to your target EPUB file:
```bash
python make_audiobook.py "path/to/your/book.epub"
```

### Advanced Options
You can configure custom saving paths, voice variants, or adjustments to narration speeds:
```bash
python make_audiobook.py "book.epub" --out "my_audio_folder" --voice "en-US-JennyNeural" --rate "+10%"
```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
