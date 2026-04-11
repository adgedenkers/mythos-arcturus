"""
SDIP Chunker Engine
Splits documents into addressable chunks based on content type.

Usage:
    from sdip_chunker import chunk_file
    chunks = chunk_file('/path/to/file.md')
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

from config import (
    MAX_CHUNK_WORDS, MIN_CHUNK_WORDS, SMALL_FILE_THRESHOLD,
    SUPPORTED_FORMATS, BINARY_FORMATS,
)


@dataclass
class Chunk:
    """A single addressable section of a document."""
    chunk_index: int
    content_text: str
    word_count: int
    parent_heading: Optional[str] = None

    def to_dict(self):
        return asdict(self)


def chunk_file(filepath: str | Path) -> list[Chunk]:
    """
    Read a file and split it into chunks.
    Returns a list of Chunk objects.
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    suffix = filepath.suffix.lower()

    # Read content based on format
    if suffix in ('.docx',):
        content = _read_docx(filepath)
        return _chunk_docx(content)
    elif suffix in ('.json',):
        return _chunk_json(filepath)
    elif suffix in ('.html', '.htm'):
        content = _read_text(filepath)
        return _chunk_html(content)
    elif suffix in ('.py', '.js', '.ts', '.sh', '.bash'):
        content = _read_text(filepath)
        return _chunk_code(content, suffix)
    elif suffix in SUPPORTED_FORMATS or suffix in ('.md', '.markdown', '.txt', '.text'):
        content = _read_text(filepath)
        return _chunk_markdown(content)
    else:
        # Attempt plain text for anything else
        try:
            content = _read_text(filepath)
            return _chunk_markdown(content)
        except Exception:
            return []


def _read_text(filepath: Path) -> str:
    """Read a text file, handling encoding issues."""
    for encoding in ('utf-8', 'latin-1', 'cp1252'):
        try:
            return filepath.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    # Last resort — lossy read
    return filepath.read_bytes().decode('utf-8', errors='replace')


def _read_docx(filepath: Path) -> list[dict]:
    """
    Read a .docx file and return a list of {heading, text} sections.
    Requires python-docx.
    """
    try:
        from docx import Document
    except ImportError:
        # Fall back to treating as unreadable
        return [{'heading': None, 'text': f'[DOCX file — python-docx not available: {filepath.name}]'}]

    doc = Document(str(filepath))
    sections = []
    current_heading = None
    current_text = []

    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            # Save previous section
            if current_text:
                sections.append({
                    'heading': current_heading,
                    'text': '\n'.join(current_text)
                })
                current_text = []
            current_heading = para.text.strip()
        else:
            text = para.text.strip()
            if text:
                current_text.append(text)

    # Final section
    if current_text:
        sections.append({
            'heading': current_heading,
            'text': '\n'.join(current_text)
        })

    return sections


# ── Chunking Strategies ────────────────────────────────────────

def _chunk_markdown(content: str) -> list[Chunk]:
    """
    Split markdown content into chunks.
    Strategy: headers first, then paragraph boundaries, then sentence splitting for long blocks.
    """
    content = content.strip()
    if not content:
        return []

    total_words = len(content.split())

    # Small file → single chunk
    if total_words <= SMALL_FILE_THRESHOLD:
        heading = _extract_first_heading(content)
        return [Chunk(
            chunk_index=0,
            content_text=content,
            word_count=total_words,
            parent_heading=heading,
        )]

    # Try splitting on headers
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    header_matches = list(header_pattern.finditer(content))

    if header_matches:
        return _split_by_headers(content, header_matches)

    # No headers — split on paragraph boundaries
    return _split_by_paragraphs(content)


def _split_by_headers(content: str, header_matches: list) -> list[Chunk]:
    """Split content at header boundaries."""
    chunks = []

    # Content before first header (preamble)
    if header_matches[0].start() > 0:
        preamble = content[:header_matches[0].start()].strip()
        if preamble and len(preamble.split()) >= MIN_CHUNK_WORDS:
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=preamble,
                word_count=len(preamble.split()),
                parent_heading=None,
            ))

    # Each header section
    for i, match in enumerate(header_matches):
        heading = match.group(2).strip()
        start = match.start()
        end = header_matches[i + 1].start() if i + 1 < len(header_matches) else len(content)
        section_text = content[start:end].strip()
        word_count = len(section_text.split())

        if word_count < MIN_CHUNK_WORDS:
            # Too short — merge with next or skip
            if chunks:
                prev = chunks[-1]
                merged = prev.content_text + '\n\n' + section_text
                chunks[-1] = Chunk(
                    chunk_index=prev.chunk_index,
                    content_text=merged,
                    word_count=len(merged.split()),
                    parent_heading=prev.parent_heading,
                )
            continue

        if word_count > MAX_CHUNK_WORDS:
            # Long section — sub-split by paragraphs within it
            sub_chunks = _split_by_paragraphs(section_text, parent_heading=heading)
            for sc in sub_chunks:
                sc.chunk_index = len(chunks)
                chunks.append(sc)
        else:
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=section_text,
                word_count=word_count,
                parent_heading=heading,
            ))

    # Re-index
    for i, c in enumerate(chunks):
        c.chunk_index = i

    return chunks


def _split_by_paragraphs(content: str, parent_heading: str = None) -> list[Chunk]:
    """Split content on double newlines (paragraph boundaries)."""
    paragraphs = re.split(r'\n\s*\n', content)
    chunks = []
    current_text = []
    current_words = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_words = len(para.split())

        # If this single paragraph exceeds max, split by sentences
        if para_words > MAX_CHUNK_WORDS:
            # Flush current accumulation
            if current_text:
                combined = '\n\n'.join(current_text)
                chunks.append(Chunk(
                    chunk_index=len(chunks),
                    content_text=combined,
                    word_count=current_words,
                    parent_heading=parent_heading,
                ))
                current_text = []
                current_words = 0

            # Split the long paragraph by sentences
            sentence_chunks = _split_by_sentences(para, parent_heading)
            for sc in sentence_chunks:
                sc.chunk_index = len(chunks)
                chunks.append(sc)
            continue

        # Accumulate paragraphs up to MAX_CHUNK_WORDS
        if current_words + para_words > MAX_CHUNK_WORDS and current_text:
            combined = '\n\n'.join(current_text)
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=combined,
                word_count=current_words,
                parent_heading=parent_heading,
            ))
            current_text = []
            current_words = 0

        current_text.append(para)
        current_words += para_words

    # Flush remaining
    if current_text:
        combined = '\n\n'.join(current_text)
        if current_words >= MIN_CHUNK_WORDS:
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=combined,
                word_count=current_words,
                parent_heading=parent_heading,
            ))
        elif chunks:
            # Merge tiny remainder into previous chunk
            prev = chunks[-1]
            merged = prev.content_text + '\n\n' + combined
            chunks[-1] = Chunk(
                chunk_index=prev.chunk_index,
                content_text=merged,
                word_count=len(merged.split()),
                parent_heading=prev.parent_heading,
            )

    # Re-index
    for i, c in enumerate(chunks):
        c.chunk_index = i

    return chunks


def _split_by_sentences(text: str, parent_heading: str = None) -> list[Chunk]:
    """Split a long text block at sentence boundaries."""
    # Simple sentence splitter — handles .?! followed by space+uppercase
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    chunks = []
    current_sentences = []
    current_words = 0

    for sent in sentences:
        sent_words = len(sent.split())
        if current_words + sent_words > MAX_CHUNK_WORDS and current_sentences:
            combined = ' '.join(current_sentences)
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=combined,
                word_count=current_words,
                parent_heading=parent_heading,
            ))
            current_sentences = []
            current_words = 0

        current_sentences.append(sent)
        current_words += sent_words

    if current_sentences:
        combined = ' '.join(current_sentences)
        if current_words >= MIN_CHUNK_WORDS or not chunks:
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=combined,
                word_count=current_words,
                parent_heading=parent_heading,
            ))
        elif chunks:
            prev = chunks[-1]
            merged = prev.content_text + ' ' + combined
            chunks[-1] = Chunk(
                chunk_index=prev.chunk_index,
                content_text=merged,
                word_count=len(merged.split()),
                parent_heading=prev.parent_heading,
            )

    return chunks


def _chunk_json(filepath: Path) -> list[Chunk]:
    """Split JSON files — top-level keys become chunks."""
    try:
        raw = filepath.read_text(encoding='utf-8')
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Treat as plain text
        content = _read_text(filepath)
        return _chunk_markdown(content)

    if isinstance(data, dict):
        chunks = []
        for key, value in data.items():
            text = json.dumps({key: value}, indent=2, default=str)
            word_count = len(text.split())
            if word_count >= MIN_CHUNK_WORDS:
                chunks.append(Chunk(
                    chunk_index=len(chunks),
                    content_text=text,
                    word_count=word_count,
                    parent_heading=key,
                ))
        if not chunks:
            # All keys too small — single chunk
            text = json.dumps(data, indent=2, default=str)
            return [Chunk(chunk_index=0, content_text=text, word_count=len(text.split()))]
        return chunks
    elif isinstance(data, list):
        # Array — single chunk (or split if huge)
        text = json.dumps(data, indent=2, default=str)
        word_count = len(text.split())
        if word_count <= SMALL_FILE_THRESHOLD:
            return [Chunk(chunk_index=0, content_text=text, word_count=word_count)]
        # Split array items into groups
        chunks = []
        current_items = []
        current_words = 0
        for item in data:
            item_text = json.dumps(item, indent=2, default=str)
            item_words = len(item_text.split())
            if current_words + item_words > MAX_CHUNK_WORDS and current_items:
                text = json.dumps(current_items, indent=2, default=str)
                chunks.append(Chunk(
                    chunk_index=len(chunks),
                    content_text=text,
                    word_count=current_words,
                ))
                current_items = []
                current_words = 0
            current_items.append(item)
            current_words += item_words
        if current_items:
            text = json.dumps(current_items, indent=2, default=str)
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=text,
                word_count=current_words,
            ))
        return chunks
    else:
        text = json.dumps(data, indent=2, default=str)
        return [Chunk(chunk_index=0, content_text=text, word_count=len(text.split()))]


def _chunk_html(content: str) -> list[Chunk]:
    """Split HTML by section-level tags, fall back to markdown splitting on raw text."""
    # Strip tags for text extraction, then chunk as markdown
    text = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    if not text:
        return []

    return _chunk_markdown(text)


def _chunk_code(content: str, suffix: str) -> list[Chunk]:
    """
    Split code files at function/class boundaries.
    Falls back to line-based chunking if no clear boundaries found.
    """
    content = content.strip()
    if not content:
        return []

    total_words = len(content.split())
    if total_words <= SMALL_FILE_THRESHOLD:
        return [Chunk(chunk_index=0, content_text=content, word_count=total_words)]

    # Python: split on def/class at indent level 0
    if suffix in ('.py',):
        return _chunk_python(content)

    # Shell: split on function definitions
    if suffix in ('.sh', '.bash'):
        return _chunk_shell(content)

    # JS/TS: split on function/class/export at top level
    if suffix in ('.js', '.ts'):
        return _chunk_js(content)

    # Default: chunk as text
    return _chunk_markdown(content)


def _chunk_python(content: str) -> list[Chunk]:
    """Split Python files on top-level def/class boundaries."""
    pattern = re.compile(r'^(?=(?:def |class |async def ))', re.MULTILINE)
    return _split_on_pattern(content, pattern)


def _chunk_shell(content: str) -> list[Chunk]:
    """Split shell scripts on function boundaries."""
    pattern = re.compile(r'^(?=\w+\s*\(\)\s*\{)', re.MULTILINE)
    return _split_on_pattern(content, pattern)


def _chunk_js(content: str) -> list[Chunk]:
    """Split JS/TS on function/class/export boundaries."""
    pattern = re.compile(r'^(?=(?:function |class |export |const |let |var )\w)', re.MULTILINE)
    return _split_on_pattern(content, pattern)


def _split_on_pattern(content: str, pattern) -> list[Chunk]:
    """Generic splitter using a regex pattern for boundaries."""
    matches = list(pattern.finditer(content))

    if not matches or len(matches) < 2:
        return _chunk_markdown(content)

    chunks = []

    # Preamble before first match
    if matches[0].start() > 0:
        preamble = content[:matches[0].start()].strip()
        if preamble and len(preamble.split()) >= MIN_CHUNK_WORDS:
            chunks.append(Chunk(
                chunk_index=0,
                content_text=preamble,
                word_count=len(preamble.split()),
                parent_heading='(preamble)',
            ))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section = content[start:end].strip()
        if not section:
            continue

        # Extract name from first line
        first_line = section.split('\n')[0].strip()
        heading = first_line[:80] if first_line else None

        chunks.append(Chunk(
            chunk_index=len(chunks),
            content_text=section,
            word_count=len(section.split()),
            parent_heading=heading,
        ))

    # Re-index
    for i, c in enumerate(chunks):
        c.chunk_index = i

    return chunks


def _chunk_docx(sections: list[dict]) -> list[Chunk]:
    """Chunk already-parsed docx sections."""
    if not sections:
        return []

    chunks = []
    for sec in sections:
        text = sec.get('text', '').strip()
        if not text:
            continue
        word_count = len(text.split())
        heading = sec.get('heading')

        if word_count > MAX_CHUNK_WORDS:
            sub_chunks = _split_by_paragraphs(text, parent_heading=heading)
            for sc in sub_chunks:
                sc.chunk_index = len(chunks)
                chunks.append(sc)
        elif word_count >= MIN_CHUNK_WORDS:
            chunks.append(Chunk(
                chunk_index=len(chunks),
                content_text=text,
                word_count=word_count,
                parent_heading=heading,
            ))

    # Re-index
    for i, c in enumerate(chunks):
        c.chunk_index = i

    return chunks


# ── Helpers ────────────────────────────────────────────────────

def _extract_first_heading(content: str) -> Optional[str]:
    """Extract the first markdown heading from content."""
    match = re.search(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else None


# ── CLI ────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: sdip_chunker.py <filepath> [--json]")
        sys.exit(1)

    filepath = sys.argv[1]
    output_json = '--json' in sys.argv

    try:
        chunks = chunk_file(filepath)
        if output_json:
            print(json.dumps([c.to_dict() for c in chunks], indent=2))
        else:
            print(f"File: {filepath}")
            print(f"Chunks: {len(chunks)}")
            print(f"Total words: {sum(c.word_count for c in chunks)}")
            print("---")
            for c in chunks:
                heading = f" [{c.parent_heading}]" if c.parent_heading else ""
                preview = c.content_text[:100].replace('\n', ' ')
                print(f"  [{c.chunk_index}]{heading} ({c.word_count}w): {preview}...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
