---
title: NewsAI
emoji: 📰
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# News AI Space

Set `GROQ_API_KEY` in the Space secrets. The summarizer discovers the models
available to that key and selects a chat model automatically. An optional
`GROQ_MODEL` value is used when that model is available; otherwise, the
summarizer falls back to an available model.
