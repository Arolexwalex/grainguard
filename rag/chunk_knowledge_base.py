"""
Chunks every markdown file in knowledge_base/ into smaller pieces, split on ## headings.

Why chunk at all: an 8GB laptop can't afford to stuff every knowledge base file into the
model's context on every question - that wastes memory and slows down responses. Instead we
break each file into topic-sized pieces (one per ## heading) so retrieval can pull just the
2-3 most relevant pieces for a given question.

Run this from the rag/ folder:
    python3 chunk_knowledge_base.py

Output: chunks.json - a list of {id, source_file, heading, text} objects.
No external dependencies - this step is pure text processing, no model calls.
"""
import json
import re
from pathlib import Path

KB_DIR = Path(__file__).resolve().parent.parent / "knowledge_base"
OUTPUT_PATH = Path(__file__).resolve().parent / "chunks.json"


def chunk_markdown_file(filepath):
    """Split a markdown file into chunks on ## headings. The file's own # title (if any)
    gets prepended to every chunk as context, since a chunk like 'Filling and sealing
    sequence' is meaningless without knowing it's about PICS bags."""
    text = filepath.read_text()
    lines = text.split("\n")

    doc_title = None
    chunks = []
    current_heading = None
    current_lines = []

    def flush():
        if current_heading and current_lines:
            body = "\n".join(current_lines).strip()
            if body:
                prefix = f"{doc_title} - " if doc_title else ""
                chunks.append({
                    "heading": f"{prefix}{current_heading}",
                    "text": body,
                })

    for line in lines:
        if line.startswith("# ") and doc_title is None:
            doc_title = line[2:].strip()
        elif line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    flush()

    return chunks


def main():
    all_chunks = []
    chunk_id = 0

    md_files = sorted(KB_DIR.glob("*.md"))
    print(f"Found {len(md_files)} knowledge base files in {KB_DIR}")

    for filepath in md_files:
        file_chunks = chunk_markdown_file(filepath)
        print(f"  {filepath.name}: {len(file_chunks)} chunks")
        for c in file_chunks:
            all_chunks.append({
                "id": f"chunk_{chunk_id:03d}",
                "source_file": filepath.name,
                "heading": c["heading"],
                "text": c["text"],
            })
            chunk_id += 1

    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_chunks, f, indent=2)

    print(f"\nTotal: {len(all_chunks)} chunks written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
