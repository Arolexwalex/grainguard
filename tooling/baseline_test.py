"""
Baseline tester for GrainGuard.

Run this AFTER you have either llama-server or Ollama running locally with Qwen3-4B loaded.
It sends every question from qa_dataset/farmer_scenarios_v1.jsonl to your local model,
with no RAG and no fine-tuning applied, and saves the raw answers.

This "before" baseline is what lets us later prove, with actual evidence, whether fine-tuning
and RAG improved the model's answers - not just assume they did.

Usage:
    python3 baseline_test.py --backend llama-server --model qwen3-4b
    python3 baseline_test.py --backend ollama --model qwen3:4b-instruct

Requires: pip install requests --break-system-packages
"""
import argparse
import json
import time
from pathlib import Path

import requests

QA_PATH = Path(__file__).resolve().parent.parent / "qa_dataset" / "farmer_scenarios_v1.jsonl"
OUTPUT_PATH = Path(__file__).resolve().parent / "baseline_results.jsonl"

SYSTEM_PROMPT = (
    "You are GrainGuard, an offline advisor for post-harvest grain storage and aflatoxin "
    "prevention, built for smallholder farmers and extension agents in Nigeria. Give concrete, "
    "specific, practical advice."
)


def load_questions():
    questions = []
    with open(QA_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                questions.append(json.loads(line))
    return questions


def query_llama_server(question, model, host="http://localhost:8080"):
    resp = requests.post(
        f"{host}/v1/chat/completions",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "temperature": 0.3,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def query_ollama(question, model, host="http://localhost:11434"):
    resp = requests.post(
        f"{host}/api/chat",
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            "stream": False,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["llama-server", "ollama"], required=True)
    parser.add_argument("--model", required=True, help="Model name as loaded by your server")
    parser.add_argument("--host", default=None, help="Override default host:port")
    args = parser.parse_args()

    questions = load_questions()
    print(f"Loaded {len(questions)} questions from {QA_PATH}")

    results = []
    for i, item in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {item['id']} ({item['topic']})...")
        start = time.time()
        try:
            if args.backend == "llama-server":
                host = args.host or "http://localhost:8080"
                answer = query_llama_server(item["question"], args.model, host)
            else:
                host = args.host or "http://localhost:11434"
                answer = query_ollama(item["question"], args.model, host)
            elapsed = round(time.time() - start, 2)
            results.append({
                "id": item["id"],
                "topic": item["topic"],
                "question": item["question"],
                "expected_source_files": item["source_files"],
                "model_answer": answer,
                "seconds": elapsed,
            })
            print(f"    -> {elapsed}s")
        except Exception as e:
            print(f"    !! FAILED: {e}")
            results.append({
                "id": item["id"],
                "topic": item["topic"],
                "question": item["question"],
                "error": str(e),
            })

    with open(OUTPUT_PATH, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    ok = sum(1 for r in results if "model_answer" in r)
    print(f"\nDone. {ok}/{len(results)} succeeded. Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
