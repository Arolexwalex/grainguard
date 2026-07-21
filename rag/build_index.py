"""
Builds a searchable index by asking Ollama to turn every chunk into an embedding
(a list of numbers that captures its meaning).

Run this on YOUR laptop, not in Claude's sandbox - it needs your local Ollama server running.

Prerequisites:
    1. Ollama running (it starts automatically after install, or run: ollama serve)
    2. The embedding model pulled:  ollama pull nomic-embed-text
       (this is a small, fast model made specifically for turning text into embeddings -
       different job from qwen3, which generates conversational answers)

Usage:
    python3 build_index.py

Output: index.json - every chunk plus its embedding vector, ready for searching.
Requires: pip install requests --break-system-packages
"""
import json
import time
from pathlib import Path

import requests

CHUNKS_PATH = Path(__file__).resolve().parent / "chunks.json"
INDEX_PATH = Path(__file__).resolve().parent / "index.json"
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"


def embed_text(text):
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def main():
    with open(CHUNKS_PATH) as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_PATH}")

    # Quick check that Ollama and the embedding model are actually reachable before we
    # commit to embedding all 26+ chunks one by one.
    try:
        embed_text("test")
    except Exception as e:
        print(f"Could not reach Ollama's embedding endpoint: {e}")
        print(f"Check that Ollama is running and you've run: ollama pull {EMBED_MODEL}")
        return

    indexed = []
    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}/{len(chunks)}] Embedding {chunk['id']} ({chunk['source_file']})...")
        # Embed the heading together with the text so the chunk's topic context
        # influences its position in meaning-space, not just its raw body text.
        text_to_embed = f"{chunk['heading']}\n{chunk['text']}"
        embedding = embed_text(text_to_embed)
        indexed.append({**chunk, "embedding": embedding})
        time.sleep(0.05)  # be gentle on the local server

    with open(INDEX_PATH, "w") as f:
        json.dump(indexed, f)

    print(f"\nDone. Index with {len(indexed)} embedded chunks saved to {INDEX_PATH}")


if __name__ == "__main__":
    main()
