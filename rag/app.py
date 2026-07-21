"""
A simple local chat interface for GrainGuard, built for demo/screen-recording purposes
(LinkedIn post, competition demo video). This is a thin UI layer over the exact same
retrieve() and generate_answer() functions in query.py - no separate logic, so what you
see here is genuinely what the system does, not a mockup.

Runs entirely on your own machine. No hosting, no internet required beyond the initial
`pip install`.

Setup:
    pip install gradio --break-system-packages

Usage:
    python3 app.py

Then open the local URL it prints (usually http://127.0.0.1:7860) in your browser.
"""
import json
from pathlib import Path

import gradio as gr

from query import retrieve, generate_answer

INDEX_PATH = Path(__file__).resolve().parent / "index.json"

# Load the index once at startup rather than per-question, since it doesn't change
# between questions in a single session.
if not INDEX_PATH.exists():
    raise SystemExit(
        f"No index found at {INDEX_PATH}. Run build_index.py first, then try again."
    )

with open(INDEX_PATH) as f:
    INDEX = json.load(f)


def respond(message, history):
    """Called each time the user submits a question in the chat UI."""
    retrieved = retrieve(message, INDEX)

    # Build a short, readable summary of what was retrieved, so the demo visibly shows
    # the RAG mechanism working - this is the part that makes the video interesting to a
    # technical audience, not just a chat bubble appearing.
    sources_summary = "\n".join(
        f"- **{chunk['source_file']}** — {chunk['heading']} (relevance: {score:.2f})"
        for score, chunk in retrieved
    )

    answer = generate_answer(message, retrieved)

    full_response = (
        f"**Sources consulted:**\n{sources_summary}\n\n---\n\n{answer}"
    )
    return full_response


demo = gr.ChatInterface(
    fn=respond,
    title="GrainGuard — Offline Post-Harvest Storage Advisor",
    description=(
        "Ask about maize or groundnut storage, moisture, aflatoxin risk, or PICS bags. "
        "Runs entirely offline on this machine — no internet connection is used to "
        "answer, only the local knowledge base and local model."
    ),
    examples=[
        "I see small holes in my stored maize kernels and dust at the bottom of the bag. What is this?",
        "Why can't I just seal wet grain in a PICS bag and let the bag dry it out over time?",
        "What is the safe moisture level for storing groundnut?",
    ],
)

if __name__ == "__main__":
    demo.launch()
