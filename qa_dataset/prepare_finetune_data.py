"""
Converts our qa_dataset (question/answer pairs) into the chat-format training data that
Unsloth's SFTTrainer expects for fine-tuning: one JSON object per line, each with a
"messages" list (system + user + assistant), matching exactly how the model will actually
be used at inference time via query.py.

This step needs no model, no GPU, no internet - pure text reformatting. Safe to run anywhere.

Usage:
    python3 prepare_finetune_data.py
"""
import json
from pathlib import Path

QA_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = QA_DIR / "train_data.jsonl"

SYSTEM_PROMPT = (
    "You are GrainGuard, an offline advisor for post-harvest grain storage and aflatoxin "
    "prevention, built for smallholder farmers and extension agents in Nigeria. Give "
    "concrete, specific, practical advice grounded in established agricultural guidance. "
    "For anything involving chemical treatments or fumigants, never describe these as a "
    "simple home task - recommend contacting a licensed service instead."
)


def load_all_qa_files():
    """Loads every farmer_scenarios*.jsonl file in this folder, so new batches added later
    get picked up automatically without editing this script."""
    entries = []
    for path in sorted(QA_DIR.glob("farmer_scenarios*.jsonl")):
        # Skip the combined file if present, to avoid double-counting entries that also
        # exist in the individual v1/v2 files it was built from.
        if "combined" in path.name:
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    return entries


def main():
    entries = load_all_qa_files()
    print(f"Loaded {len(entries)} Q&A pairs")

    training_rows = []
    for item in entries:
        training_rows.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item["question"]},
                {"role": "assistant", "content": item["answer"]},
            ]
        })

    with open(OUTPUT_PATH, "w") as f:
        for row in training_rows:
            f.write(json.dumps(row) + "\n")

    print(f"Wrote {len(training_rows)} training examples to {OUTPUT_PATH}")
    print(
        f"\nNote: {len(training_rows)} examples is still well below the few-hundred minimum "
        "generally recommended for LoRA fine-tuning to show a real, reliable effect. This "
        "file is ready to use as-is for an early experimental run, but growing the dataset "
        "further before a final training run is worth doing if time allows."
    )


if __name__ == "__main__":
    main()
