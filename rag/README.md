# RAG pipeline

This is what makes GrainGuard answer from *our* sourced knowledge instead of the model's own
(sometimes wrong) general training - directly addressing what baseline_test_001_manual.md
found.

## The three pieces, in plain terms

1. **`chunk_knowledge_base.py`** - splits our knowledge_base/*.md files into small, topic-sized
   pieces. Already run - see `chunks.json` (26 chunks from our 7 files). Pure text processing,
   no model needed, so I ran this already in my own environment.

2. **`build_index.py`** - turns every chunk into an embedding (a list of numbers capturing its
   meaning) using Ollama's `nomic-embed-text` model, and saves the result as `index.json`. This
   needs YOUR Ollama server, so you run this one.

3. **`query.py`** - the actual pipeline: takes a question, embeds it the same way, finds the
   3 most similar chunks by comparing the numbers (cosine similarity - a standard way to
   measure how close two meanings are), then hands those chunks to qwen3-4b-instruct as
   required context before it's allowed to answer.

## How this fixes what we saw in the baseline
The system prompt in `query.py` explicitly instructs the model to answer **only** from the
provided context and to say so if the context is insufficient, rather than fill gaps from its
own training. That's the direct fix for the cinnamon-oil remedy it invented - if "cinnamon oil"
isn't in our sourced material (it isn't), the model shouldn't be able to produce it anymore.

## Running it on your laptop

```bash
# One-time setup
ollama pull nomic-embed-text
pip install requests numpy --break-system-packages

# Build the index (only needs re-running if knowledge_base/ content changes)
cd rag
python3 build_index.py

# Ask it something
python3 query.py "small holes in stored maize kernels, dust at the bottom of the bag"
```

## What to actually check when you run it
The script prints which chunks got retrieved *before* showing the answer, with a similarity
score for each. This matters - if you ask about weevils and it retrieves the PICS bag chunk
instead of storage_insect_pests.md, that tells us something needs tuning (maybe TOP_K, maybe
how we wrote the chunk headings) before we trust the final answers.

## Known limitations of this v1 pipeline
- **In-memory search, no real vector database.** At 26 chunks this is instant and completely
  fine. If the knowledge base grows to thousands of chunks, this brute-force comparison would
  get slow and a proper vector index (e.g. a simple FAISS index) would be worth switching to -
  not needed yet at our scale.
- **No re-ranking or hybrid search.** More advanced RAG setups combine keyword search with
  embedding search, or re-rank retrieved chunks with a second pass. Worth considering later if
  retrieval quality needs improvement, but adds complexity we don't need to start with.
- **Fixed TOP_K = 3.** Some questions might need more context (multi-factor risk questions)
  and some need less. Worth testing whether this number is actually right once you've run a
  few real queries.
- **Not yet tested against qa_dataset/farmer_scenarios_v1.jsonl as a batch.** Right now this
  is a single-question CLI tool - the natural next step is running all 16 of our Q&A dataset
  questions through it and comparing retrieved sources against the source_files we
  already tagged each one with, to catch retrieval mismatches systematically rather than one
  at a time.
