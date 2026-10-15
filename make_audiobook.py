import argparse
import asyncio
import os
import re
import tempfile
from pathlib import Path

import edge_tts
from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
from edge_tts.constants import DEFAULT_VOICE
from pydub import AudioSegment

DEFAULT_VOICE = "en-US-JennyNeural"

# Limit concurrent network requests so Microsoft doesn't block your IP
SEMAPHORE_LIMIT = 5
sem = asyncio.Semaphore(SEMAPHORE_LIMIT)


def safe_filename(name: str, max_len: int = 80) -> str:
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", "-", name.strip())
    return name[:max_len] or "chapter"


def looks_like_code(text: str) -> bool:
    stripped = text.strip()

    code_starters = (
        "import ", "from ", "def ", "class ", "async ", "await ", "return ",
        "if ", "elif ", "else:", "for ", "while ", "try ", "except ", "@ ", "# ", "print("
    )

    if stripped.startswith(code_starters):
        return True

    code_patterns = [
        r"\w+\s*=\s*.+",
        r"\w+\(.+\)",
        r"^\s*[\{\}\[\]\(\)]",
        r":\s*$",
        r"->",
        r"==|!=|<=|>=",
    ]

    if "\n" in stripped and any(re.search(p, stripped, re.MULTILINE) for p in code_patterns):
        return True

    return False


def extract_text_blocks_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav"]):
        tag.decompose()

    body = soup.body or soup
    blocks = []

    def walk(node):
        for child in node.children:
            if not getattr(child, "name", None):
                continue

            tag_name = child.name.lower()

            if tag_name in ["pre", "code"]:
                code_text = child.get_text("\n", strip=True)
                if code_text:
                    blocks.append("The following is code.")
                    blocks.append(code_text)
                    continue

            if tag_name in ["h1", "h2", "h3", "h4", "p", "li", "blockquote"]:
                text = child.get_text(" ", strip=True)
                if text:
                    if looks_like_code(text):
                        blocks.append("The following is code.")
                    blocks.append(text)
                continue

            walk(child)

    walk(body)
    return blocks


def get_chapter_title(html: str, fallback: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    heading = soup.find(["h1", "h2", "h3"])
    if heading:
        title = heading.get_text(" ", strip=True)
        if title:
            return title

    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(" ", strip=True)
        if title:
            return title

    return fallback


def extract_chapters(epub_path: str):
    book = epub.read_epub(epub_path)
    chapters = []

    for index, item_ref in enumerate(book.spine, start=1):
        if isinstance(item_ref, tuple) or isinstance(item_ref, list):
            item_id = item_ref[0]
        else:
            item_id = item_ref

        item = book.get_item_with_id(item_id)

        if not item or item.get_type() != ITEM_DOCUMENT:
            continue

        html = item.get_content().decode("utf-8", errors="ignore")
        blocks = extract_text_blocks_from_html(html)

        if not blocks:
            continue

        title = get_chapter_title(html, f"Chapter {index}")
        text = "\n\n".join(blocks)

        chapters.append({
            "index": len(chapters) + 1,
            "title": title,
            "text": text,
        })

    return chapters


def split_text(text: str, max_chars: int = 2000):
    paragraphs = re.split(r"\n\s*\n", text)
    chunks = []
    current = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(current) + len(paragraph) + 2 <= max_chars:
            current += ("\n\n" if current else "") + paragraph
        else:
            if current:
                chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return chunks


async def fetch_chunk_with_retry(chunk: str, temp_mp3: Path, voice: str, rate: str, chunk_index: int):
    """Worker task that handles safety limits and retries for a single chunk."""
    async with sem:  # Ensures we don't smash the server with too many requests at once
        max_retries = 3
        for attempt in range(max_retries):
            try:
                communicate = edge_tts.Communicate(text=chunk, voice=voice, rate=rate)
                await communicate.save(str(temp_mp3))
                return  # Success
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                else:
                    raise e


async def synthesize_mp3(text: str, output_path: Path, voice: str, rate: str):
    chunks = split_text(text)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        mp3_parts = []
        tasks = []

        # Create tasks for all chunks so they can download simultaneously
        for i, chunk in enumerate(chunks, start=1):
            temp_mp3 = temp_dir / f"part_{i:03d}.mp3"
            mp3_parts.append(temp_mp3)

            tasks.append(
                fetch_chunk_with_retry(chunk, temp_mp3, voice, rate, i)
            )

        # Run all chunk downloads in parallel
        await asyncio.gather(*tasks)

        # Stitch them together sequentially (pydub part)
        combined = AudioSegment.empty()
        for mp3 in mp3_parts:
            combined += AudioSegment.from_mp3(mp3)

        combined.export(output_path, format="mp3")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("epub_file", help="Path to the EPUB file")
    parser.add_argument("--out", default="audiobook_mp3", help="Output folder")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help="TTS voice")
    parser.add_argument("--rate", default="+0%", help="Speech rate, e.g. -10%, +10%")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    chapters = extract_chapters(args.epub_file)

    print(f"Found {len(chapters)} chapters/sections. Starting parallel generation...")

    for chapter in chapters:
        chapter_num = chapter["index"]
        title = chapter["title"]
        filename = f"{chapter_num:03d}_{safe_filename(title)}.mp3"
        output_path = out_dir / filename

        print(f"Generating: {output_path} (Parallel chunks processing...)")
        await synthesize_mp3(
            text=chapter["text"],
            output_path=output_path,
            voice=args.voice,
            rate=args.rate,
        )

    print("Done. MP3 audiobook chapters created.")


if __name__ == "__main__":
    asyncio.run(main())
