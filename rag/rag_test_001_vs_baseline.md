# RAG test 001 — same question as baseline_test_001, with retrieval

**Date**: 2026-07-11
**Setup**: qwen3:4b-instruct via Ollama, query.py pipeline, 3 chunks retrieved (top scores
0.697, 0.697, 0.694) from storage_insect_pests.md, pics_bags_usage.md,
storage_methods_comparison.md
**Question**: identical to baseline_test_001 - "small holes in stored maize kernels, dust at
the bottom of the bag"

## Retrieval quality
Correctly surfaced storage_insect_pests.md as the top match - the exact file containing the
weevil-to-aflatoxin connection the baseline completely missed. Retrieval is working as
intended.

## Fixed compared to baseline
1. **Aflatoxin connection now present** - "increases the risk of fungal growth and aflatoxin
   contamination" directly reflects storage_insect_pests.md's core point that insect damage
   compounds mould risk. This was the single biggest gap in the baseline.
2. **No longer recommends washing the grain itself.** It does suggest washing the empty
   container before reuse, which is reasonable practice and not contradicted by any source -
   a meaningfully different (and correct) recommendation from baseline's "wash the maize."
3. **No invented folk remedy.** The cinnamon/clove oil suggestion from baseline is gone
   entirely for grain treatment.
4. **Exact sourced moisture figure** - "below 13.5% for maize" matches
   moisture_and_drying.md's table precisely, versus baseline's vaguer "below 13%."
5. Correctly stated PICS bags don't fix wet grain, and correctly advised against mixing with
   older stored grain - both traceable directly to source chunks.

## Not fully fixed - logged honestly
Recommended fumigating the storage container with "phosphine or carbon dioxide" if infestation
is severe. **This is not in any of our sourced material.** It's a more defensible invention
than the baseline's cinnamon oil (these are real industrial fumigants), but it's still the
model reaching outside the retrieved context despite the system prompt explicitly instructing
it not to. This tells us RAG substantially reduces ungrounded generation here, but doesn't
eliminate it completely - worth keeping in mind rather than assuming grounding is airtight.

## What this means for next steps
The core value case for GrainGuard - closing the reasoning gap between insect damage and
aflatoxin risk - is now demonstrably working, with real evidence (this file) rather than just
a claim. The fumigant slip suggests it may be worth either tightening the system prompt further,
or explicitly adding a chunk about container cleaning/fumigation options to the knowledge base
so the model has something grounded to draw from instead of improvising.
