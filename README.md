# IELTS Reading Lab

A static web app for practising IELTS-style reading tests, designed to run on GitHub Pages with no build step and no backend.

**[Try it live](https://arlian.github.io/ielts-reading-lab)**

- **480 passages** across CEFR levels A1–C2 (80 per level, 20 domains)
- **12,000 questions** in 5 IELTS question types: multiple choice, true/false/not given, matching information, sentence completion, short answer
- Per-test countdown timer based on the recommended time
- Instant scoring with explanations and click-to-highlight evidence in the passage
- Progress (best scores, attempts, unfinished drafts) saved in the browser via `localStorage`
- Light/dark theme

All content is original synthetic educational material — not official IELTS content.

## Run locally

Any static file server works (the app uses `fetch()`, so opening `index.html` directly from disk will not):

```bash
python3 -m http.server 8000
# then open http://localhost:8000
``
