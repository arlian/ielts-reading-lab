# Prompt: generate IELTS reading passages + tests (batch, JSON output)

Workflow: edit the batch list at the top of the prompt → send to the model → save its whole reply
to a file (e.g. `batch1.json`) → run `python3 tools/import_tests.py batch1.json` to convert,
validate, and add everything to the site.

Send everything between the `---` lines:

---

You are a senior IELTS materials writer. Your only goal is QUALITY: write reading passages that feel like real articles from The Economist, National Geographic, or BBC Future — grounded in specific, verifiable context.

Every passage must include:
- Specific dates, years, or time references (e.g. "In 2019", "Since 1985")
- Named places, institutions, people, or organizations (e.g. "Tokyo", "MIT", "Dr. Sarah Chen", "Airbnb")
- Concrete numbers, statistics, or measurements (e.g. "47% of respondents", "€2.3 million", "12,000 users")
- Real-world examples, case studies, or scenarios that make the topic tangible
- Practical applications or consequences, not just theory

Never write generic filler, abstract theory without examples, or hypothetical scenarios without grounding.

Write one complete practice test for EACH row below:

| # | Level | Domain | Subject |
|---|-------|--------|---------|
| 1 | B1 | Environment | How a small Danish island became energy self-sufficient |
| 2 | B2 | Psychology | Why forgetting is essential to memory |
| 3 | C1 | Economics | The hidden economics of container shipping |

(Levels: A1 350–450 words, very simple sentences · A2 450–600, everyday language · B1 600–750, some abstract ideas · B2 750–900, argument and counter-argument · C1 900–1050, nuanced academic prose · C2 1000–1200, dense and sophisticated. Vocabulary and grammar must genuinely match the level.)

Each test: a 5-paragraph passage (each paragraph gets a short heading) followed by 15 questions — 3 of each type: MC (multiple choice, 4 options), TFNG (true/false/not given), MATCH (which paragraph contains…), GAP (gap-fill), SHORT (short answer). Question order follows the passage. Make distractors plausible, TFNG statements paraphrased (include at least one NOT GIVEN that is tempting but truly unverifiable), and GAP/SHORT answers must be words copied EXACTLY from the passage (max 3 words) with no ambiguity.

Output ONE JSON object and nothing else (no commentary, no markdown fences), in exactly this shape.

EXAMPLE (shows the required level of detail and context):

{
  "tests": [
    {
      "level": "B2",
      "domain": "Psychology",
      "title": "The Jaipur Memory Project: retraining people to forget safely",
      "passage": [
        { "heading": "A clinic in India tackles trauma", "text": "In 2014, Dr. Rajesh Patel established a clinic in Jaipur, India, specialising in post-traumatic stress disorder (PTSD) among refugees and accident survivors. His team found that 73% of patients experienced debilitating flashbacks that prevented them from working or sleeping. Unlike most trauma clinics, Patel's approach was based not on reinforcing memories but on weakening them — a controversial technique called reconsolidation therapy. After each patient recalled a traumatic event in a safe setting, they took a beta-blocker to suppress the emotional response while sleeping. Over twelve weeks, most patients reported a 60% reduction in flashback intensity." },
        { "heading": "Turning wind into ownership", "text": "..." },
        { "heading": "...", "text": "..." },
        { "heading": "...", "text": "..." },
        { "heading": "...", "text": "..." }
      ],
      "questions": [
        {
          "type": "MC",
          "question": "What started Samsø's renewable energy project?",
          "options": ["Winning a government competition in 1997", "An order from the European Union", "A shortage of heating oil", "Foreign investment"],
          "answer": "A",
          "evidence": { "paragraph": 1, "quote": "won a government competition" },
          "why": "Paragraph 1 states the project began when the island won a 1997 government competition; the other options are never mentioned as the trigger."
        },
        {
          "type": "TFNG",
          "statement": "Every turbine on the island is owned by private companies.",
          "answer": "FALSE",
          "evidence": { "paragraph": 2, "quote": "many turbines are owned collectively by residents" },
          "why": "Paragraph 2 says many turbines are collectively owned by residents, which contradicts the statement."
        },
        {
          "type": "MATCH",
          "question": "Which paragraph describes opposition from local farmers?",
          "answer": 3,
          "evidence": { "paragraph": 3, "quote": "several farmers initially refused" },
          "why": "Only paragraph 3 discusses farmer resistance."
        },
        {
          "type": "GAP",
          "question": "The island now exports its surplus electricity to the ____.",
          "limit": "TWO WORDS",
          "answer": "Danish mainland",
          "evidence": { "paragraph": 5, "quote": "exports its surplus electricity to the Danish mainland" },
          "why": "The phrase appears verbatim in paragraph 5."
        },
        {
          "type": "SHORT",
          "question": "What year did the project begin?",
          "limit": "ONE WORD",
          "answer": "1997",
          "evidence": { "paragraph": 1, "quote": "In 1997, the Danish island" },
          "why": "Paragraph 1 gives the starting year directly."
        }
      ]
    }
  ]
}

Three hard rules, because grading is automatic:
1. Every evidence "quote" must be copied character-for-character from the "text" of the paragraph it names (a short snippet, 4–12 words).
2. GAP and SHORT answers must appear verbatim in the passage.
3. MC answers are a single letter ("A"–"D"); TFNG answers are exactly "TRUE", "FALSE", or "NOT GIVEN"; MATCH answers are a paragraph number 1–5.

---

## Tips

- Swap the table rows for any topics/levels you want; 3–5 tests per request is the sweet spot.
- If the model's reply gets cut off, say "continue" and merge the pieces into one valid JSON file.
- It is fine if the model wraps the JSON in a ```json fence — the importer strips it.
- The importer also still accepts the older markdown batch format, so old files keep working.
- `tools/import_tests.py` checks every evidence quote and answer, reports problems, assigns topic
  IDs, writes the site JSON files, and updates `data/manifest.json` — nothing manual to do.
