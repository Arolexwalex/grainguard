# Submission prep

## The story this project tells (use this for the report + demo video)
1. **The gap**: post-harvest storage/aflatoxin knowledge already exists and works (Aflasafe,
   PICS bags) — the bottleneck is reaching farmers offline, at the moment they need it, not
   inventing new agronomy.
2. **The evidence, not just the claim**: we tested the base model before touching anything
   (baseline_test_001_manual.md) and found it gives dangerous advice (wash the grain) and
   invents unsourced remedies (cinnamon oil).
3. **The fix, measured**: RAG grounding fixed the core reasoning gap - the model now connects
   insect damage to aflatoxin risk, which it didn't before (rag_test_001_vs_baseline.md).
4. **Honest tradeoffs, tested not assumed**: we benchmarked a faster model (llama3.2:1b) and
   rejected it with real evidence - it was 2x faster but inverted a safety threshold and
   fabricated a citation (MODEL_COMPARISON_DECISION.md). This shows engineering judgment, not
   just a spec-sheet model pick.
5. **Real hardware numbers, not estimates**: ~100-120s average response time on qwen3:4b, CPU
   only, 8GB RAM - measured, not projected.

## 2-minute demo video script (draft)
- **0:00-0:20** — the problem: extension agent scarcity (1:10,000), aflatoxin invisible to the
  eye, physical solutions exist but don't reach farmers offline
- **0:20-0:50** — show the baseline failure live: ask base qwen3 the weevil question, show it
  recommend washing the grain and inventing a cinnamon remedy
- **0:50-1:30** — show query.py running the same question through GrainGuard: retrieved
  sources on screen, then the grounded answer connecting insect damage to aflatoxin risk
  correctly
- **1:30-1:50** — briefly show the model comparison decision - "we tested a faster model and
  rejected it, here's why" (screenshot of MODEL_COMPARISON_DECISION.md's error examples)
- **1:50-2:00** — close on the offline, zero-cost, CPU-only framing and the local relevance
  (Nigeria-specific sources: NSPRI, NaijaVoices for future local-language support)

## Submission checklist (from what we know of ADTC requirements)
- [ ] Open GitHub repo using their report template (need to check exact template format on
      the DevPost/official page)
- [ ] Written report covering problem definition, constraints, design decisions - most of this
      can be assembled directly from README.md, MODEL_CHOICE.md, and
      MODEL_COMPARISON_DECISION.md, which already contain this reasoning
- [ ] GGUF model weights judges can download and run locally via LM Studio or Ollama/Open WebUI
      - need to confirm whether base qwen3:4b-instruct (unmodified) is acceptable to submit, or
      whether a fine-tuned/quantized custom version is expected/preferred
- [ ] 2-minute demo video (script drafted above)
- [ ] Confirm the actual Gate 1 deadline directly on the official page - conflicting dates
      were found earlier (July 24 vs August 25)
- [ ] Double-check team registration status on DevPost

## Honest gaps to decide on before submitting
- We have RAG working well (15/16 retrieval, demonstrated quality improvement) but have NOT
  done any fine-tuning - qa_dataset only has 16 examples, well short of what's needed. Worth
  deciding explicitly: submit as RAG-only (honest, working, well-documented), or invest time
  expanding the dataset for real fine-tuning before the deadline.
- Cassava is out of scope (README already states this clearly) - fine to leave as a stated
  future direction rather than a gap to apologize for.
- No Hausa/local-language support yet, despite NaijaVoices being identified as a strong lead -
  also fine to name explicitly as a next step rather than pretend it's done.
