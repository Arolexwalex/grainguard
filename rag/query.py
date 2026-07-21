"""
The actual GrainGuard RAG pipeline: given a question, find the most relevant knowledge base
chunks, then hand them to the model as grounding material before it answers.

This is the piece that should fix what we saw in the baseline test: instead of letting the
model invent an answer from its own general training (which gave us the wrong "wash the
grain" advice and an unsourced cinnamon remedy), we force it to answer using only what's
actually in our sourced knowledge_base/ files.

Run this on YOUR laptop, after build_index.py has been run successfully.

Usage:
    python3 query.py "small holes in stored maize kernels, dust at the bottom of the bag"

Requires: pip install requests numpy --break-system-packages
"""
import json
import sys
from pathlib import Path

import numpy as np
import requests

INDEX_PATH = Path(__file__).resolve().parent / "index.json"
OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "qwen3:4b-instruct"
TOP_K = 5  # how many chunks to retrieve per question

SYSTEM_PROMPT = """You are GrainGuard, an offline advisor for post-harvest grain storage and \
aflatoxin prevention, built for smallholder farmers and extension agents in Nigeria.

ABSOLUTE RULE, STATED FIRST BECAUSE IT IS MOST IMPORTANT: hermetic/airtight storage (PICS \
bags, sealed drums, etc.) NEVER substitutes for drying, under any framing, with no \
exceptions. These containers seal in whatever moisture the grain already has - they do not \
remove moisture. If asked whether hermetic storage can help with grain that isn't fully \
dried, isn't dried by a deadline, or in any similar framing, the answer is always: no, dry \
first, then store. Do not soften this rule or imply a hermetic bag "still works" for wet \
grain, even as a lesser recommendation.

Answer ONLY using the CONTEXT provided below. If the context doesn't contain enough \
information to answer confidently, say so plainly rather than guessing or using outside \
knowledge. Give concrete, specific, practical advice. Do not invent remedies, products, or \
techniques that are not in the context.

Keep answers focused and conversational - a few short paragraphs or a short list, not a long \
structured report with many headers and sections. Aim for roughly 120-180 words unless the \
question genuinely involves weighing several risk factors together, in which case a bit more \
room is fine.

For anything involving chemical treatments, fumigants, or pesticides: never describe these as \
a simple home task. If the context indicates a treatment requires certified applicators or \
protective equipment, say so explicitly and recommend contacting a local agricultural \
extension office or licensed service instead of self-administering it."""


def embed_text(text):
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve(question, index, top_k=TOP_K):
    q_embedding = embed_text(question)
    scored = []
    for chunk in index:
        score = cosine_similarity(q_embedding, chunk["embedding"])
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


def generate_answer(question, retrieved_chunks):
    context_block = "\n\n---\n\n".join(
        f"[Source: {c['source_file']} - {c['heading']}]\n{c['text']}"
        for _, c in retrieved_chunks
    )
    user_message = f"CONTEXT:\n{context_block}\n\nQUESTION: {question}"

    resp = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "think": False,
            "stream": False,
            "options": {"num_predict": 280},
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 query.py "your question here"')
        return

    question = " ".join(sys.argv[1:])

    if not INDEX_PATH.exists():
        print(f"No index found at {INDEX_PATH}. Run build_index.py first.")
        return

    with open(INDEX_PATH) as f:
        index = json.load(f)

    print(f"Question: {question}\n")
    print("Retrieving relevant knowledge...")
    retrieved = retrieve(question, index)

    print("\nRetrieved chunks (this is the transparency check - do these actually look")
    print("relevant? If not, that tells us something about our chunking or embeddings):")
    for score, chunk in retrieved:
        print(f"  [{score:.3f}] {chunk['source_file']} - {chunk['heading']}")

    print("\nGenerating grounded answer...\n")
    answer = generate_answer(question, retrieved)
    print("=" * 60)
    print(answer)
    print("=" * 60)


if __name__ == "__main__":
    main()
