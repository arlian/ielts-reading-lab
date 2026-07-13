# Prompt: generate IELTS reading passages + tests (batch, JSON output)

Workflow: edit the batch list → send to the model → save the JSON reply → run `python3 tools/import_tests.py batch.json`

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
| 1 | A1 | Arts | A community art center opens in town |
| 2 | A1 | Business | A small shop teaches poor women to start businesses |
| 3 | A1 | Cooking | A restaurant teaches healthy eating to children |

(Levels: A1 350–450 words, very simple sentences · A2 450–600, everyday language · B1 600–750, some abstract ideas · B2 750–900, argument and counter-argument · C1 900–1050, nuanced academic prose · C2 1000–1200, dense and sophisticated. Vocabulary and grammar must genuinely match the level.)

Each test: a 5-paragraph passage (each paragraph gets a short heading) followed by 5 questions — 1 of each type: MC (multiple choice, 4 options), TFNG (true/false/not given), MATCH (which paragraph), GAP (gap-fill), SHORT (short answer). Make distractors plausible, TFNG statements paraphrased (include at least one NOT GIVEN that is tempting but truly unverifiable), and GAP/SHORT answers must be words copied EXACTLY from the passage (max 3 words) with no ambiguity.

Output ONE JSON object and nothing else (no commentary, no markdown fences):

{
  "tests": [
    {
      "level": "A1",
      "domain": "Arts",
      "title": "A community art center opens in town",
      "passage": [
        { "heading": "A building with no purpose", "text": "In 2015, an old building sits empty in a poor neighborhood. It was a school long ago. Now nobody uses it. The walls are gray. The windows are broken. The neighborhood needs something to make it alive." },
        { "heading": "An artist's dream", "text": "A woman named Maria is an artist. She loves to paint. She walks past the empty building every day. She thinks about how to use it. She talks to neighbors. They say yes, we want this. Maria decides to open an art center here." },
        { "heading": "Making the center beautiful", "text": "In 2016, Maria and neighbors clean the building. They remove trash. They fix the windows. They paint the walls with bright colors. Children help paint. They paint pictures of animals and flowers. The building becomes beautiful. Everyone feels proud." },
        { "heading": "Art classes begin", "text": "The art center opens for free classes. Children come every Saturday. They learn to paint and draw. An old artist teaches them. Children make beautiful pictures. They take the pictures home. Their families love them. The center becomes the heart of the neighborhood." },
        { "heading": "Art changes lives", "text": "Today, 100 children come to classes. Some children make art every day now. One girl enters an art competition and wins. A boy wants to be an artist now. Maria says art gives people hope and dreams. A simple art center changed everything." }
      ],
      "questions": [
        {
          "type": "MC",
          "question": "Why does Maria want to open an art center?",
          "options": ["She wants to make the neighborhood alive and beautiful", "She wants to become famous", "The government asks her to", "She has money to spend"],
          "answer": "A",
          "evidence": { "paragraph": 2, "quote": "She walks past the empty building every day. She thinks about how to use it" },
          "why": "Paragraph 2 shows her motivation to use the empty space. The other reasons are not mentioned."
        },
        {
          "type": "TFNG",
          "statement": "The art classes cost money.",
          "answer": "FALSE",
          "evidence": { "paragraph": 4, "quote": "The art center opens for free classes" },
          "why": "Paragraph 4 says the classes are free."
        },
        {
          "type": "GAP",
          "question": "The building was a ____ long ago.",
          "limit": "ONE WORD",
          "answer": "school",
          "evidence": { "paragraph": 1, "quote": "It was a school long ago" },
          "why": "Paragraph 1 states what the building used to be."
        },
        {
          "type": "MATCH",
          "question": "Which paragraph says children learn to paint and draw?",
          "answer": 4,
          "evidence": { "paragraph": 4, "quote": "They learn to paint and draw" },
          "why": "Paragraph 4 is about the art classes."
        },
        {
          "type": "SHORT",
          "question": "How many children come to classes today?",
          "limit": "ONE WORD",
          "answer": "100",
          "evidence": { "paragraph": 5, "quote": "Today, 100 children come to classes" },
          "why": "Paragraph 5 gives this number."
        }
      ]
    }
  ]
}

Three hard rules for auto-grading to work:
1. Every evidence "quote" must be copied character-for-character from the passage (short snippet, 4–12 words).
2. GAP and SHORT answers must appear verbatim in the passage.
3. MC answers are a single letter ("A"–"D"); TFNG answers are exactly "TRUE", "FALSE", or "NOT GIVEN"; MATCH answers are a paragraph number 1–5.

---

## Tips
- Swap the table rows for any topics/levels you want; 3–5 tests per request is ideal.
- If the model's reply gets cut off, say "continue" and merge the pieces into one valid JSON.
- The importer also accepts the older markdown batch format for backwards compatibility.
- `python3 tools/import_tests.py batch.json` converts, validates, writes JSON, and updates manifest automatically.
