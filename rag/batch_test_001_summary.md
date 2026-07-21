# Batch test 001 — all 16 Q&A questions through the RAG pipeline

**Date**: 2026-07-11
**Setup**: qwen3:4b-instruct via Ollama, 29-chunk index (8 knowledge base files), TOP_K=3

## Retrieval accuracy: 15/16
Strong result on a dataset we wrote ourselves without hand-tuning the embeddings to match.

**The one miss — qa013 (humid zone / slow drying question)**
Expected `aflatoxin_risk_factors.md` and `nigeria_specific_technologies.md` (specifically the
solar dryer section), but retrieval only pulled `moisture_and_drying.md`. Likely cause: the
solar dryer content is one small, specific section inside nigeria_specific_technologies.md,
competing for retrieval rank against an entire file whose sole subject is drying. The general
file's broader semantic overlap with "drying" seems to be crowding out the more specific,
regionally-relevant answer.

**Next thing to try**: raise TOP_K from 3 to 4 or 5 in query.py and re-run this specific
question, to see if the solar dryer chunk shows up just outside the current cutoff. This is
a cheap experiment before considering anything more structural (like re-writing that chunk's
heading to include drying-related keywords more explicitly).

## Timing: the bigger finding
Response times across the 16 questions:
| Metric | Value |
|---|---|
| Fastest | 56.6s |
| Slowest | 208.6s |
| Average | ~119s (about 2 minutes per question) |

This is full end-to-end pipeline time (embedding the question, retrieving chunks, generating
the answer) - not just retrieval, which is near-instant at our scale (29 chunks).

**Why this matters more than the retrieval miss**: the Africa Deep Tech Challenge scoring
explicitly weights performance (30%) and efficiency (20%). A ~2 minute average response time
would be a real liability in live judging or a demo, even with excellent answer content. This
is worth treating as a priority alongside content quality, not an afterthought.

## Things worth testing to address the speed problem
1. **Check if "thinking mode" is active.** Qwen3 can reason step-by-step (slower, more
   thorough) or answer directly (faster). If thinking mode is on by default, forcing
   non-thinking mode for straightforward lookups could cut response time substantially.
2. **Shorten the requested answer length.** The system prompt currently doesn't constrain
   answer length - the model has been producing fairly long, structured markdown responses.
   Asking for a tighter, more conversational answer length could speed generation
   meaningfully without losing the grounding.
3. **Benchmark against the Phi-4-mini-instruct fallback** noted in MODEL_CHOICE.md - it was
   flagged specifically for CPU speed, so this is the moment to actually test whether it's
   faster on this hardware while still answering acceptably.
4. **Run llama-bench** (built and verified back in Step 4) for a clean tokens/sec number,
   isolated from the RAG pipeline overhead, to separate "the model is slow" from "our
   pipeline adds overhead."
