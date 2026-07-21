# Fine-tuning plan — free, using Google Colab

## Why not fine-tune on the laptop itself
Fine-tuning (even efficient LoRA fine-tuning) needs a GPU to be practical - on an 8GB CPU-only
laptop it would be extremely slow, likely hours per epoch even on a tiny dataset. The
laptop's job is running the final model (inference), not training it. Training happens
somewhere else, for free, then the result comes back to the laptop as a normal GGUF file -
same as how Qwen3-4B itself got to your laptop via Ollama.

## The free path: Google Colab + Unsloth
Unsloth (an open-source fine-tuning library) publishes a ready-made, free notebook
specifically for our exact model:

**https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_(4B)-Instruct.ipynb**

This runs on Google Colab's free tier, which includes a T4 GPU at no cost - no payment, no
sign-up beyond a Google account. Unsloth handles LoRA fine-tuning efficiently (small trainable
fraction of the model, much less memory than full fine-tuning) and can export the result
directly to GGUF, ready for Ollama - the exact format this whole project already uses.

## What's ready now
- `qa_dataset/prepare_finetune_data.py` - converts our Q&A pairs into the chat-format training
  data the notebook expects (system + user + assistant messages, matching exactly how the
  model is actually prompted in query.py). Already run - see `qa_dataset/train_data.jsonl`
  (36 examples).

## Steps to actually run this (on Google Colab, in your browser, no local setup)
1. Open the notebook link above, sign in with a Google account
2. Runtime -> Change runtime type -> select GPU (T4)
3. Run the setup/install cells as provided
4. Where the notebook loads its example dataset, replace it with our
   `qa_dataset/train_data.jsonl` instead - upload it directly into the Colab session (there's
   normally a file upload option, or you can mount Google Drive)
5. Run the training cells - with only 36 examples this should be fast (likely minutes, not
   hours) since it's a small dataset, though the effect on the model may be modest given the
   dataset's current size
6. Use the notebook's built-in GGUF export step to save the fine-tuned result
7. Download the resulting GGUF file and bring it back to the laptop

## Bringing the fine-tuned model back to Ollama
Once you have the GGUF file downloaded, create a simple Modelfile (a plain text file, no
extension needed) next to it:
```
FROM ./grainguard-qwen3-4b.gguf
PARAMETER temperature 0.3
SYSTEM """You are GrainGuard, an offline advisor for post-harvest grain storage and aflatoxin prevention, built for smallholder farmers and extension agents in Nigeria."""
```
Then register it with Ollama:
```
ollama create grainguard -f Modelfile
```
After that, `grainguard` becomes a normal local model name, usable everywhere `qwen3:4b-instruct`
was used before - including directly in `query.py` by changing `CHAT_MODEL`.

## Honest expectations for this first run
36 examples is a real, working seed dataset, but still short of the "few hundred" generally
recommended for LoRA to reliably change model behavior. This first fine-tuning run is worth
doing to prove the whole pipeline works end-to-end (data -> Colab -> GGUF -> Ollama), but the
realistic plan is: run it now to validate the mechanics, then grow train_data.jsonl further
(more Q&A pairs) before a final training run closer to submission, if time allows. A working,
proven pipeline with a modest dataset is more valuable to show in a submission than an
untested plan with a bigger one.
