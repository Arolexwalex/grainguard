# Farmer scenario Q&A dataset

`farmer_scenarios_v1.jsonl` — 16 question-and-answer pairs, one JSON object per line.

## Why this exists (two jobs, one dataset)
1. **Fine-tuning material** — teaches the base model the tone, reasoning style, and level of
   detail we want: acknowledge the specific scenario, give a concrete recommendation, and
   explain the *why* briefly rather than just stating a rule. Real fine-tuning will need many
   more examples than this (aim for at least a few hundred), but this v1 batch sets the pattern.
2. **RAG test queries** — the same questions double as test cases for the retrieval pipeline
   later: if we ask the RAG system "small holes in stored maize kernels, what is this?" it
   should retrieve storage_insect_pests.md, not aflatoxin_risk_factors.md alone. Having the
   `source_files` field on each entry lets us check that later automatically.

## Format
```json
{
  "id": "qa001",
  "topic": "moisture_check",
  "question": "farmer-phrased question, deliberately informal/Pidgin-inflected in places",
  "answer": "grounded, specific answer drawing on knowledge_base/ content",
  "source_files": ["which knowledge_base file(s) this answer is grounded in"]
}
```

## Design choices worth knowing about
- **Question phrasing is intentionally mixed** — some formal English, some Pidgin-inflected,
  some in the voice of an extension agent rather than a farmer. Real users won't all phrase
  things the same way, and a model fine-tuned only on textbook-clean questions tends to perform
  worse on messier real input.
- **Answers always name the reasoning, not just the rule.** E.g. qa007 doesn't just say "use a
  PICS bag" - it explains why holes lead to mould risk too. This matters because post-harvest
  decisions often require weighing multiple factors together, not looking up one fact.
- **Every answer traces back to a specific knowledge base file.** No answer here is invented
  from general LLM knowledge - each one paraphrases something already sourced and logged in
  knowledge_base/data_sources_log.md.

## Known limitations of v1 (to fix before real fine-tuning)
- Only 16 examples — far too few to fine-tune on directly, this is a seed batch to validate the
  format and tone
- No cassava examples yet (out of current scope, see README.md)
- No verified Hausa-language examples yet (blocked on the terminology gap logged in
  data_sources_log.md)
- Written by an AI drawing on secondary sources, not yet reviewed by an agronomist or actual
  extension agent — worth getting real domain-expert eyes on this before it goes into a
  submission
