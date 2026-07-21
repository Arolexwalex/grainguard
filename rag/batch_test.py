"""
Runs ALL questions from qa_dataset/farmer_scenarios_v1.jsonl through the RAG pipeline in one
go, and checks whether retrieval pulled the source_files we already tagged each question with.

This turns "we tested it on one question and it looked good" into a systematic check across
every question we've written so far - much stronger evidence for a submission, and it catches
retrieval problems we'd otherwise only find by accident.

Run this on YOUR laptop, after build_index.py has been run (re-run it first if you've added
container_cleaning_and_fumigation_safety.md - the knowledge base grew from 26 to 29 chunks).

Usage:
    python3 batch_test.py

Requires: pip install requests numpy --break-system-packages
"""
import json
import time
from pathlib import Path

from query import retrieve, generate_answer

QA_PATH = Path(__file__).resolve().parent.parent / "qa_dataset" / "farmer_scenarios_v1.jsonl"
INDEX_PATH = Path(__file__).resolve().parent / "index.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "batch_test_results.jsonl"


def main():
    if not INDEX_PATH.exists():
        print(f"No index found at {INDEX_PATH}. Run build_index.py first.")
        return

    with open(INDEX_PATH) as f:
        index = json.load(f)

    questions = []
    with open(QA_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    print(f"Loaded {len(questions)} questions, index has {len(index)} chunks\n")

    results = []
    retrieval_hits = 0

    for i, item in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {item['id']} ({item['topic']})")
        start = time.time()

        retrieved = retrieve(item["question"], index)
        retrieved_sources = list({c["source_file"] for _, c in retrieved})

        # Did retrieval pull at least one of the source files we tagged this question with?
        expected = set(item["source_files"])
        got = set(retrieved_sources)
        hit = bool(expected & got)
        if hit:
            retrieval_hits += 1

        answer = generate_answer(item["question"], retrieved)
        elapsed = round(time.time() - start, 1)

        print(f"    expected: {sorted(expected)}")
        print(f"    retrieved: {sorted(got)}")
        print(f"    match: {'YES' if hit else 'NO -- worth a look'} | {elapsed}s\n")

        results.append({
            "id": item["id"],
            "topic": item["topic"],
            "question": item["question"],
            "expected_source_files": sorted(expected),
            "retrieved_source_files": sorted(got),
            "retrieval_match": hit,
            "model_answer": answer,
            "seconds": elapsed,
        })

    with open(OUTPUT_PATH, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print("=" * 60)
    print(f"Retrieval matched expected source for {retrieval_hits}/{len(questions)} questions")
    print(f"Full results (including model answers) saved to {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
