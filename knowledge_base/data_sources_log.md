# Data sources log

## Primary sources used to build knowledge_base/ (distilled, not reproduced verbatim)
1. IITA — *Farmers' Guide to Management of Aflatoxins in Maize and Groundnuts in Africa* (2017,
   West Africa training manual). Covers aflatoxin biology, risk factors, Aflasafe biocontrol.
2. Ghana MoFA / CSIR-SARI — *Appropriate Postharvest Practices for Improved Grain Storage*
   (2017). Covers moisture testing, drying, mould/aflatoxin management, PICS bag steps.
3. NSPRI (Nigerian Stored Products Research Institute) — official site and institutional
   profile. Covers Nigeria-specific storage structures (maize crib, solar dryer, hermetic
   containers) and their local-language, community-based extension approach.

## Candidate open datasets for fine-tuning / format reference
These aren't Nigeria-specific but are useful either as raw material to filter/adapt, or as a
template for how to structure our own Q&A pairs:

- **KisanVaani/agriculture-qa-english-only** (Hugging Face) — a general agriculture Q&A pairs
  dataset, curated from agricultural forums and FAQs. Not African-specific (leans Indian
  agriculture) but useful for seeing question phrasing patterns and answer structure/length.
- **Tasfiul/Agricultural-dataset** (Hugging Face, ~175k Q&A rows) — similar general-purpose
  agricultural Q&A corpus, referenced in an existing open-source RAG project (Agri-Llama on
  GitHub) that pairs Llama-2 with FAISS for agricultural question answering — worth reviewing
  as an architecture reference even though the underlying data isn't local to our use case.
- **Lacuna Fund agriculture datasets** — a program specifically funding African agricultural ML
  datasets. One listed project collects local-language speech/text data intended to support
  automatic response systems for agricultural advisories aimed at smallholder farmers — closely
  aligned with what we're building, worth investigating directly on lacunafund.org for access
  terms and whether it covers Nigerian languages (Hausa is the natural fit given maize/groundnut
  are concentrated in Nigeria's Hausa-speaking north).

## Local-language resources found (this round)
- **NaijaVoices** (via Lacuna Fund, 2025) — a major open dataset: 1,867 hours of speech and
  roughly 1.9 million transcribed instances across Hausa, Igbo, and Yorùbá, from over 5,000
  speakers. Notably, the project deliberately included agriculture as one of its covered topic
  areas. This is the single most promising lead for giving our model real exposure to how
  Nigerian farmers actually talk, not just clean written English. Worth checking directly for
  agriculture-tagged subsets.
- **AFRIDOC-MT** — a document-level machine translation dataset from English into five African
  languages including Hausa and Yorùbá. Useful if we want to translate our English knowledge
  base and Q&A pairs into Hausa rather than sourcing/writing Hausa content from scratch.
- **Nigerian Twitter Sentiment Corpus** (Hausa, Igbo, Nigerian-Pidgin, Yorùbá; Bayero University
  / Masakhane) — sentiment-labelled, not directly usable for our Q&A task, but confirms strong
  existing NLP tooling and corpora for these languages that a fine-tuning pipeline could draw on.

## Hausa agricultural terms — starter list (UNVERIFIED, flagged for native-speaker review)
No verified glossary source was found in this search pass. The terms below are common
general-knowledge Hausa words for these crops and are included only as a starting point — they
should be confirmed with a native Hausa speaker or the NaijaVoices dataset before being used in
any user-facing text, since agricultural register and regional dialect variation matter here:
- masara — maize
- gyada — groundnut
- dawa — guinea corn/sorghum
- hatsi — grain (general term)

Technical terms (moisture content, mould, weevil, hermetic storage) were not confidently
sourced in Hausa this round and should not be guessed at — this is a gap to close with a native
speaker, not something to improvise past.

## Still to source
- A direct copy of NSPRI's own "Guide on Post Harvest Handling of Maize" (referenced often in
  literature, direct link not yet found)
- Verified Hausa (and ideally Yoruba/Igbo) technical vocabulary for storage/aflatoxin concepts
- Any FAO Nigeria country-office postharvest publications
- Real farmer-phrased questions (forums, past extension agent FAQ logs) to make our synthetic
  Q&A set sound like how people actually ask, not how a textbook writes
