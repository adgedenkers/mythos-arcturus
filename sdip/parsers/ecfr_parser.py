#!/usr/bin/env python3
"""
eCFR XML Parser for SDIP
Parses bulk eCFR XML (e.g., Title 38) into individual section files
suitable for SDIP ingestion.

Each DIV8 (section) becomes a separate .txt file with:
  - Full hierarchical context (Title > Chapter > Part > Subpart > Section)
  - Section text from all <P> tags
  - Authority and source citations
  - Cross-reference preservation
  - Amendment history

Usage:
    python3 ecfr_parser.py /path/to/ECFR-title38.xml /path/to/output_dir
    python3 ecfr_parser.py /path/to/ECFR-title38.xml /path/to/output_dir --stats
    python3 ecfr_parser.py /path/to/ECFR-title38.xml /path/to/output_dir --dry-run
"""

import sys
import os
import re
import argparse
from pathlib import Path
from collections import defaultdict

try:
    from lxml import etree
except ImportError:
    print("ERROR: lxml required. Install: pip install lxml --break-system-packages")
    sys.exit(1)


# ── DIV hierarchy ──────────────────────────────────────────────
# eCFR XML nesting:
#   DIV1 = Title
#   DIV2 = Subtitle (rare)
#   DIV3 = Chapter
#   DIV4 = Subchapter (rare)
#   DIV5 = Part
#   DIV6 = Subpart
#   DIV7 = Subject Group (rare)
#   DIV8 = Section (atomic unit)
#   DIV9 = Appendix

DIV_LABELS = {
    'DIV1': 'Title',
    'DIV2': 'Subtitle',
    'DIV3': 'Chapter',
    'DIV4': 'Subchapter',
    'DIV5': 'Part',
    'DIV6': 'Subpart',
    'DIV7': 'Subject Group',
    'DIV8': 'Section',
    'DIV9': 'Appendix',
}


def clean_text(text):
    """Clean whitespace from extracted text."""
    if text is None:
        return ''
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_all_text(elem):
    """Extract all text content from an element, including tail text of children."""
    return clean_text(''.join(elem.itertext()))


def extract_paragraphs(elem):
    """
    Extract text from all <P> tags within an element (non-recursive into sub-DIVs).
    Also captures <FP>, <EXTRACT>, <GPOTABLE> text.
    """
    paragraphs = []
    
    for child in elem:
        tag = child.tag
        
        # Skip nested DIV elements (they'll be processed separately)
        if tag.startswith('DIV'):
            continue
        
        if tag in ('P', 'FP', 'EXTRACT', 'NOTE'):
            text = extract_all_text(child)
            if text:
                paragraphs.append(text)
        elif tag == 'GPOTABLE':
            # Extract table content as text
            rows = []
            for row in child.iter('ROW'):
                cells = [extract_all_text(ent) for ent in row.iter('ENT')]
                if any(cells):
                    rows.append(' | '.join(cells))
            if rows:
                # Get column headers if present
                headers = []
                for boxhd in child.iter('BOXHD'):
                    for hed in boxhd.iter('CHED'):
                        h = extract_all_text(hed)
                        if h:
                            headers.append(h)
                if headers:
                    paragraphs.append(' | '.join(headers))
                    paragraphs.append('-' * 40)
                paragraphs.extend(rows)
        elif tag == 'CITA':
            text = extract_all_text(child)
            if text:
                paragraphs.append(f"[Citation: {text}]")
        elif tag == 'AUTH':
            text = extract_all_text(child)
            if text:
                paragraphs.append(f"[Authority: {text}]")
        elif tag == 'SOURCE':
            text = extract_all_text(child)
            if text:
                paragraphs.append(f"[Source: {text}]")
        elif tag == 'SECAUTH':
            text = extract_all_text(child)
            if text:
                paragraphs.append(f"[Section Authority: {text}]")
        elif tag == 'CONTENTS':
            # Table of contents — skip, not useful for search
            pass
        elif tag == 'CFRTOC':
            # CFR table of contents — skip
            pass
        elif tag in ('HEAD', 'AMDDATE', 'PTHD', 'CHAPTI', 'SECHD', 'RESERVED'):
            # Handled elsewhere or not needed in body
            pass
        else:
            # Catch-all: extract any text
            text = extract_all_text(child)
            if text and len(text) > 5:
                paragraphs.append(text)
    
    return paragraphs


def get_heading(elem):
    """Extract the heading text from a DIV element."""
    head = elem.find('HEAD')
    if head is not None:
        return clean_text(extract_all_text(head))
    return None


def sanitize_filename(text, max_len=80):
    """Convert a heading into a safe filename component."""
    if not text:
        return 'untitled'
    # Remove section symbols and numbers for cleaner names
    text = re.sub(r'[§\u00a7]', 'sec', text)
    # Keep alphanumeric, spaces, hyphens
    text = re.sub(r'[^\w\s\-]', '', text)
    text = re.sub(r'\s+', '_', text).strip('_')
    text = text[:max_len]
    return text.lower()


def build_section_path(context):
    """Build a directory path from the hierarchical context."""
    parts = []
    if context.get('chapter_n'):
        parts.append(f"chapter_{context['chapter_n'].lower().replace(' ', '_')}")
    if context.get('part_n'):
        parts.append(f"part_{context['part_n']}")
    if context.get('subpart_n'):
        parts.append(f"subpart_{context['subpart_n'].lower()}")
    return os.path.join(*parts) if parts else ''


def parse_ecfr_xml(xml_path, output_dir, dry_run=False):
    """
    Parse eCFR XML and write individual section files.
    
    Returns stats dict.
    """
    xml_path = Path(xml_path)
    output_dir = Path(output_dir)
    
    if not xml_path.exists():
        print(f"✗ XML file not found: {xml_path}")
        sys.exit(1)
    
    print(f"Parsing: {xml_path}")
    print(f"Output:  {output_dir}")
    
    # Parse XML
    parser = etree.XMLParser(recover=True, encoding='utf-8')
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()
    
    stats = {
        'sections': 0,
        'appendices': 0,
        'parts': 0,
        'chapters': 0,
        'skipped_empty': 0,
        'total_words': 0,
        'files_written': 0,
        'cross_refs': 0,
    }
    
    # Find the title element
    title_div = root.find('.//DIV1')
    if title_div is None:
        # Try without namespace
        for elem in root.iter():
            if elem.tag == 'DIV1':
                title_div = elem
                break
    
    if title_div is None:
        print("✗ No DIV1 (Title) element found in XML")
        sys.exit(1)
    
    title_heading = get_heading(title_div) or 'Unknown Title'
    title_n = title_div.get('N', '?')
    print(f"Title: {title_heading}")
    
    # Walk the hierarchy
    for chapter in title_div.iter('DIV3'):
        chapter_heading = get_heading(chapter) or 'Unknown Chapter'
        chapter_n = chapter.get('N', '?')
        stats['chapters'] += 1
        
        for part in chapter.iter('DIV5'):
            part_heading = get_heading(part) or 'Unknown Part'
            part_n = part.get('N', '?')
            stats['parts'] += 1
            
            # Get part-level auth/source
            part_auth = ''
            part_source = ''
            for child in part:
                if child.tag == 'AUTH':
                    part_auth = extract_all_text(child)
                elif child.tag == 'SOURCE':
                    part_source = extract_all_text(child)
                elif child.tag.startswith('DIV'):
                    break  # stop once we hit nested DIVs
            
            # Track current subpart context
            current_subpart_heading = None
            current_subpart_n = None
            
            # Process all direct children and nested elements
            for elem in part.iter():
                if elem.tag == 'DIV6':
                    # Subpart
                    current_subpart_heading = get_heading(elem)
                    current_subpart_n = elem.get('N', '?')
                
                elif elem.tag == 'DIV8':
                    # Section — this is the money
                    section_heading = get_heading(elem) or 'Untitled Section'
                    section_n = elem.get('N', '?')
                    node_id = elem.get('NODE', '')
                    
                    # Extract section text
                    paragraphs = extract_paragraphs(elem)
                    
                    if not paragraphs:
                        # Check if it's a reserved section
                        head_text = section_heading.lower()
                        if 'reserved' in head_text:
                            stats['skipped_empty'] += 1
                            continue
                        # Some sections have text directly in HEAD only
                        stats['skipped_empty'] += 1
                        continue
                    
                    # Build the document
                    context = {
                        'title_n': title_n,
                        'title': title_heading,
                        'chapter_n': chapter_n,
                        'chapter': chapter_heading,
                        'part_n': part_n,
                        'part': part_heading,
                        'subpart_n': current_subpart_n,
                        'subpart': current_subpart_heading,
                        'section_n': section_n,
                        'section': section_heading,
                        'node_id': node_id,
                    }
                    
                    doc_text = format_section_document(
                        context, paragraphs, part_auth, part_source
                    )
                    
                    word_count = len(doc_text.split())
                    stats['total_words'] += word_count
                    stats['sections'] += 1
                    
                    # Count cross-references
                    xrefs = len(re.findall(
                        r'(?:\d+\s+(?:CFR|U\.S\.C\.)|§\s*\d+)', doc_text
                    ))
                    stats['cross_refs'] += xrefs
                    
                    # Build output path
                    rel_dir = build_section_path(context)
                    sec_name = sanitize_filename(section_heading)
                    filename = f"{sec_name}.txt"
                    
                    out_path = output_dir / rel_dir / filename
                    
                    if dry_run:
                        print(f"  [DRY] {out_path.relative_to(output_dir)} ({word_count}w, {xrefs} xrefs)")
                    else:
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        out_path.write_text(doc_text, encoding='utf-8')
                        stats['files_written'] += 1
                
                elif elem.tag == 'DIV9':
                    # Appendix
                    appendix_heading = get_heading(elem) or 'Untitled Appendix'
                    appendix_n = elem.get('N', '?')
                    node_id = elem.get('NODE', '')
                    
                    paragraphs = extract_paragraphs(elem)
                    if not paragraphs:
                        stats['skipped_empty'] += 1
                        continue
                    
                    context = {
                        'title_n': title_n,
                        'title': title_heading,
                        'chapter_n': chapter_n,
                        'chapter': chapter_heading,
                        'part_n': part_n,
                        'part': part_heading,
                        'subpart_n': current_subpart_n,
                        'subpart': current_subpart_heading,
                        'section_n': appendix_n,
                        'section': appendix_heading,
                        'node_id': node_id,
                    }
                    
                    doc_text = format_section_document(
                        context, paragraphs, part_auth, part_source
                    )
                    
                    word_count = len(doc_text.split())
                    stats['total_words'] += word_count
                    stats['appendices'] += 1
                    
                    rel_dir = build_section_path(context)
                    app_name = sanitize_filename(appendix_heading)
                    filename = f"appendix_{app_name}.txt"
                    
                    out_path = output_dir / rel_dir / filename
                    
                    if dry_run:
                        print(f"  [DRY] {out_path.relative_to(output_dir)} ({word_count}w)")
                    else:
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        out_path.write_text(doc_text, encoding='utf-8')
                        stats['files_written'] += 1
    
    return stats


def format_section_document(context, paragraphs, part_auth='', part_source=''):
    """
    Format a single CFR section into a readable, searchable document.
    
    The output preserves full hierarchical context so that when SDIP
    chunks and indexes it, the topic graph can connect sections across
    parts and chapters.
    """
    lines = []
    
    # Header block with full context
    lines.append(f"TITLE {context['title_n']}: {context['title']}")
    lines.append(f"CHAPTER {context['chapter_n']}: {context['chapter']}")
    lines.append(f"PART {context['part_n']}: {context['part']}")
    if context.get('subpart'):
        lines.append(f"SUBPART {context['subpart_n']}: {context['subpart']}")
    lines.append(f"SECTION: {context['section']}")
    if context.get('node_id'):
        lines.append(f"NODE: {context['node_id']}")
    lines.append('')
    lines.append('=' * 60)
    lines.append('')
    
    # Section body
    for para in paragraphs:
        lines.append(para)
        lines.append('')
    
    # Part-level authority and source (if present)
    if part_auth:
        lines.append(f"[Part Authority: {part_auth}]")
        lines.append('')
    if part_source:
        lines.append(f"[Part Source: {part_source}]")
        lines.append('')
    
    return '\n'.join(lines)


def show_stats(stats):
    """Print ingestion statistics."""
    print(f"\n{'=' * 50}")
    print(f"eCFR Parse Results")
    print(f"{'=' * 50}")
    print(f"  Chapters:         {stats['chapters']}")
    print(f"  Parts:            {stats['parts']}")
    print(f"  Sections:         {stats['sections']}")
    print(f"  Appendices:       {stats['appendices']}")
    print(f"  Skipped (empty):  {stats['skipped_empty']}")
    print(f"  Files written:    {stats['files_written']}")
    print(f"  Total words:      {stats['total_words']:,}")
    print(f"  Cross-references: {stats['cross_refs']:,}")
    total_docs = stats['sections'] + stats['appendices']
    if total_docs > 0:
        print(f"  Avg words/doc:    {stats['total_words'] // total_docs}")
    print(f"{'=' * 50}")


def main():
    parser = argparse.ArgumentParser(
        description='eCFR XML Parser for SDIP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ecfr_parser.py ECFR-title38.xml ./title38_sections
  python3 ecfr_parser.py ECFR-title38.xml ./title38_sections --dry-run
  python3 ecfr_parser.py ECFR-title38.xml ./title38_sections --stats
        """
    )
    parser.add_argument('xml_file', help='Path to eCFR XML file')
    parser.add_argument('output_dir', help='Directory to write section files')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be written without writing')
    parser.add_argument('--stats', action='store_true',
                        help='Show detailed statistics after parsing')
    
    args = parser.parse_args()
    
    stats = parse_ecfr_xml(args.xml_file, args.output_dir, dry_run=args.dry_run)
    show_stats(stats)


if __name__ == '__main__':
    main()
