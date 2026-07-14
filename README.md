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
```

## Deploy to GitHub Pages

1. Push this repository to GitHub.
2. In the repository, go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to *Deploy from a branch*, pick the `main` branch and the `/ (root)` folder, then save.
4. Your site will be published at `https://<username>.github.io/<repo>/` within a minute or two.

No configuration is needed — all asset and data paths are relative, so the app works under any subpath.

## Adding new tests with an LLM

Content generation is split from the JSON format so any model can focus purely on writing quality:

1. Open `prompts/generate_test_prompt.md`, edit the topic/level table, and send the prompt to your model (Copilot, GPT, Claude, …). It writes passages and questions in a simple markdown format — no rigid schema to follow.
2. Save the model's reply to a file, e.g. `batch1.md`.
3. Run the importer:

   ```bash
   python3 tools/import_tests.py batch1.md          # convert + add to the site
   python3 tools/import_tests.py --dry-run batch1.md  # validate only
   ```

The importer parses the markdown, verifies every evidence quote against the passage (auto-correcting wrong paragraph numbers), checks that gap-fill/short answers appear verbatim in the text, assigns topic IDs, writes the JSON files into `data/<LEVEL>/`, and updates `data/manifest.json`. Tests with unfixable problems are skipped and reported.

## Project structure

```
index.html        App shell
css/styles.css    Styles (light + dark theme)
js/app.js         SPA logic: router, library, test runner, grading, storage
data/             Test content (manifest.json + one JSON file per topic)
prompts/          LLM prompt for generating new passages and tests
tools/            import_tests.py — converts model output into site data
```

## Data format

See `data/README.md` and `data/schema.json`. Each topic file contains a 5-section passage, 25 questions with type/skill/difficulty/evidence metadata, and an answer key with explanations. `data/manifest.json` indexes all topics with level, domain, title, and file path.
