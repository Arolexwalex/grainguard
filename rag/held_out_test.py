"""
Runs the GENUINELY held-out test set (questions never seen during fine-tuning) through the
RAG pipeline. Unlike batch_test.py (which uses farmer_scenarios_v1.jsonl - a subset of our
own training data), this is what actually measures whether the fine-tuned model generalizes,
rather than just recites memorized training answers.

Run this on YOUR laptop, same setup as batch_test.py.

Usage:
    python3 held_out_test.py

Requires: pip install requests numpy --break-system-packages
"""
import json
import time
from pathlib import Path

from query import retrieve, generate_answer

TEST_PATH = Path(__file__).resolve().parent.parent / "qa_dataset" / "held_out_test_set.jsonl"
INDEX_PATH = Path(__file__).resolve().parent / "index.json"
OUTPUT_PATH = Path(__file__).resolve().parent / "held_out_test_results.jsonl"


def main():
    if not INDEX_PATH.exists():
        print(f"No index found at {INDEX_PATH}. Run build_index.py first.")
        return

    with open(INDEX_PATH) as f:
        index = json.load(f)

    questions = []
    with open(TEST_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))

    print(f"Loaded {len(questions)} HELD-OUT questions (never used in fine-tuning)")
    print(f"Index has {len(index)} chunks\n")

    results = []
    retrieval_hits = 0

    for i, item in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {item['id']} ({item['topic']})")
        start = time.time()

        retrieved = retrieve(item["question"], index)
        retrieved_sources = list({c["source_file"] for _, c in retrieved})

        expected = set(item["expected_source_files"])
        got = set(retrieved_sources)
        hit = bool(expected & got)
        if hit:
            retrieval_hits += 1

        answer = generate_answer(item["question"], retrieved)
        elapsed = round(time.time() - start, 1)

        print(f"    question: {item['question']}")
        print(f"    expected: {sorted(expected)}")
        print(f"    retrieved: {sorted(got)}")
        print(f"    match: {'YES' if hit else 'NO'} | {elapsed}s")
        print(f"    ANSWER: {answer}\n")

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
    print(f"Full results saved to {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
