# 📚 EPUB to Audiobook Converter

An ultra-fast, asynchronous Python command-line utility that extracts chapters from `.epub` e-books and compiles them into beautifully voiced, high-quality `.mp3` audiobooks using **Edge TTS** and **FFmpeg**.

## ✨ Key Features
- **High-Speed Asynchronous Processing:** Uses `asyncio` parallel task workers to download chapter chunks simultaneously, maximizing network performance.
- **Smart Formatting Detection:** Automatically isolates code blocks and strips unwanted HTML/navigation data for clean narration.
- **Fault-Tolerant Streaming:** Features built-in automatic request retries to handle server-side drops seamlessly.

## 🚀 Prerequisites
This project requires **FFmpeg** to handle the stitching and generation of MP3 files.
- **Windows:** Download from [Gyan.dev](https://gyan.dev) and add its `/bin` directory to your System Environment Path.
How to install FFmpeg on Windows:

1. Download FFmpeg: Go to the Gyan.dev FFmpeg build page and download ffmpeg-git-full.7z (or the release essentials zip).
2. Extract it: Extract the folder to a permanent place on your computer, for example: C:\ffmpeg.
3. Add to Environment Path:
	• Open the Windows Start Menu, search for "Edit the system environment variables" and open it.
	• Click the Environment Variables... button at the bottom right.
	• Under System variables, select Path and click Edit....
	• Click New and add the path to the bin folder where you extracted it (e.g., C:\ffmpeg\bin).
	• Click OK on all windows to save.
4. Restart PyCharm/Terminal: You must completely restart your IDE terminal or command prompt for Windows to detect the new Path variable.

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
