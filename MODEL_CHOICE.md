# Base model choice

## Decision: Qwen3-4B-Instruct (with Qwen3.5-4B as an upgrade path)

## Why this one, not the others
Four things mattered for GrainGuard specifically, and this is where Qwen3-4B won on balance:

1. **License clarity.** Apache 2.0 — no usage restrictions, no approval thresholds, nothing to
   explain in a public hackathon submission. Some competitors (Gemma) carry usage
   restrictions above certain scale that don't affect us practically, but Apache 2.0 is simply
   one less thing to have to explain to judges.
2. **Fits the hardware with real headroom.** At Q4_K_M quantization, a 4B model needs roughly
   2.5-3GB of RAM to run — comfortable on an 8GB machine that also has to run the OS and our
   RAG pipeline alongside it. Going up to 7-8B models is explicitly flagged across multiple 2026
   sources as "not a comfortable daily experience" on CPU-only 8GB machines - too tight a
   margin for a live demo.
3. **Dual-mode reasoning fits our actual task.** Qwen3 can switch between a "thinking" mode
   (explicit step-by-step reasoning, meant for logic-heavy problems) and a "non-thinking" mode
   (fast, direct answers) within the same model. This maps unusually well onto GrainGuard's two
   query types: a simple lookup ("what's safe moisture for maize?") doesn't need thinking mode
   and should answer fast, while a multi-factor risk assessment ("late harvest + insect holes +
   humid season, what do I do?") benefits from explicit reasoning through several risk factors
   together - exactly the kind of question we flagged back in Step 1 as what makes this problem
   hard.
4. **Best available multilingual foundation.** Qwen3 claims support across 100+ languages;
   Qwen3.5 claims 201. Neither was trained with any specific guarantee of strong Hausa or Yoruba
   quality, and that claim should be tested empirically rather than trusted blindly - but among
   small open models it's the strongest starting point, and it's the foundation our LoRA
   fine-tuning on NaijaVoices-derived data will build on top of.

## Runner-up considered: Phi-4-mini-instruct (3.8B)
Consistently rated as the fastest CPU-only performer in 2026 sources (~28 tokens/sec on a
modern CPU) and slightly smaller footprint. If live demo speed turns out to be a bottleneck
during hardware testing (Step in our plan: "test on target hardware"), this is the fallback to
benchmark against Qwen3-4B before submission.

## Comparison summary
| Model | Params | License | Approx RAM (Q4_K_M) | Why not chosen as primary |
|---|---|---|---|---|
| Qwen3-4B-Instruct | 4B | Apache 2.0 | ~2.5-3GB | (chosen) |
| Phi-4-mini-instruct | 3.8B | MIT | ~3.5GB | Faster, but weaker multilingual story |
| Llama 3.2 3B-Instruct | 3B | Meta community license | ~2-3GB | Great tooling, but license has usage terms to track and multilingual coverage is narrower |
| Gemma 3/4 4B | 4B | Gemma license | ~3GB | Strong multilingual reputation, but usage-scale restrictions in license |

## What's next once this is downloaded
1. Pull via Ollama (`ollama pull qwen3:4b-instruct`) or download the official GGUF from
   Hugging Face (`Qwen/Qwen3-4B-GGUF`) for direct llama.cpp use — the challenge's judging
   sandbox uses one of these two paths, so we should test both.
2. Confirm it loads and responds on a machine matching the 8GB RAM / no-GPU constraint before
   investing time in fine-tuning on top of it.
3. Establish a baseline: ask it a handful of our qa_dataset questions *before* any fine-tuning,
   so we can actually measure whether fine-tuning + RAG improved things later.

*Sources: Ollama model library (qwen3:4b, qwen3.5:4b listings); Hugging Face Qwen3-4B-GGUF and
Qwen3-VL-4B-Instruct-GGUF model cards; multiple independent 2026 local-LLM benchmarking
roundups (Popular AI, Local AI Master, SitePoint, Pristren, AIThinkerLab) cross-checked against
each other for the 8GB CPU-only tier consensus.*
