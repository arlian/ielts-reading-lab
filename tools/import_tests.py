#!/usr/bin/env python3
"""Import model-generated IELTS tests into the site.

Usage:
    python3 tools/import_tests.py batch1.json [batch2.md ...]
    python3 tools/import_tests.py --dry-run batch1.json   # validate only, write nothing

Accepts both formats defined in prompts/generate_test_prompt.md:
  - JSON batch: {"tests": [{level, domain, title, passage[], questions[]}]}
    (markdown fences and surrounding prose around the JSON are tolerated)
  - Markdown batch: "=== TEST ===" blocks (the older format)

Validates every evidence quote and answer against the passage, writes one JSON
file per test into data/<LEVEL>/, and updates data/manifest.json.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}
CEFR_LABEL = {
    "A1": "Beginner", "A2": "Elementary", "B1": "Intermediate",
    "B2": "Upper-Intermediate", "C1": "Advanced", "C2": "Proficiency",
}
CEFR_PROFILE = {
    "A1": ["very simple sentences", "high-frequency vocabulary", "concrete everyday topics"],
    "A2": ["clear connected sentences", "everyday vocabulary", "simple reasons and comparisons"],
    "B1": ["some abstract ideas", "common academic words", "varied tenses and relative clauses"],
    "B2": ["argument and counter-argument", "hedging and passive voice", "less common vocabulary"],
    "C1": ["nuanced stance and implication", "low-frequency academic vocabulary", "complex syntax"],
    "C2": ["dense argumentation", "sophisticated cohesion", "rare and idiomatic vocabulary"],
}
RECOMMENDED_MINUTES = {"A1": 20, "A2": 20, "B1": 25, "B2": 25, "C1": 30, "C2": 30}

TYPE_MAP = {
    "MC": "multiple_choice",
    "TFNG": "true_false_not_given",
    "MATCH": "matching_information",
    "GAP": "sentence_completion",
    "SHORT": "short_answer",
}
SKILL_BY_TYPE = {
    "multiple_choice": "detail",
    "true_false_not_given": "inference",
    "matching_information": "reference",
    "sentence_completion": "detail",
    "short_answer": "detail",
}


def norm_quotes(s: str) -> str:
    return (s.replace("'", "'").replace("'", "'")
             .replace(""", '"').replace(""", '"'))


def slugify(title: str, max_words: int = 8) -> str:
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    words = re.sub(r"[^a-z0-9\s]", " ", s.lower()).split()
    return "_".join(words[:max_words]) or "untitled"


class TestParseError(Exception):
    pass


def extract_json(text: str):
    """Return the parsed JSON payload in text, or None if there is none."""
    cleaned = re.sub(r"^```(?:json)?\s*$", "", text, flags=re.M)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        return None


def json_test_list(payload):
    """Return the list of test objects inside a parsed JSON payload."""
    if isinstance(payload, dict) and "tests" in payload:
        return payload["tests"]
    if isinstance(payload, list):
        return payload
    return [payload]


def parse_json_test(t):
    """Return (hdr, sections, raw_questions) for one JSON test object."""
    if not isinstance(t, dict):
        raise TestParseError(f"test entry is not an object: {t!r}")
    hdr = {}
    for req in ("level", "domain", "title"):
        if not t.get(req):
            raise TestParseError(f"missing {req!r} field")
        hdr[req] = str(t[req]).strip()
    hdr["level"] = hdr["level"].upper()
    if hdr["level"] not in LEVELS:
        raise TestParseError(f"unknown level {hdr['level']!r}")
    if t.get("focus"):
        hdr["focus"] = str(t["focus"]).strip()

    raw_sections = t.get("passage") or []
    sections = []
    for s in raw_sections:
        heading = str(s.get("heading", "")).strip()
        text = re.sub(r"\s*\n\s*", " ", str(s.get("text", "")).strip())
        if text:
            sections.append({"paragraph": len(sections) + 1, "heading": heading, "text": text})
    if len(sections) != 5:
        raise TestParseError(f"expected 5 passage paragraphs, found {len(sections)}")

    raw_questions = []
    for i, q in enumerate(t.get("questions") or [], 1):
        code = str(q.get("type", "")).strip().upper()
        if code not in TYPE_MAP:
            raise TestParseError(f"question {i}: unknown type {q.get('type')!r} "
                                 f"(expected one of {', '.join(TYPE_MAP)})")
        text = str(q.get("question") or q.get("statement") or "").strip()
        if not text:
            raise TestParseError(f"question {i}: missing question/statement text")
        if "answer" not in q:
            raise TestParseError(f"question {i}: missing answer")
        ev = q.get("evidence") or {}
        ev_para = ev.get("paragraph")
        ev_para = int(ev_para) if str(ev_para).isdigit() else None
        ev_quote = norm_quotes(str(ev.get("quote", "")).strip()) or None
        raw_questions.append({
            "code": code,
            "text": norm_quotes(text),
            "options": [norm_quotes(str(o).strip()) for o in (q.get("options") or [])],
            "answer": norm_quotes(str(q.get("answer")).strip()),
            "ev_para": ev_para,
            "ev_quote": ev_quote,
            "why": norm_quotes(str(q.get("why") or q.get("explanation") or "").strip()),
            "limit": str(q["limit"]).strip() if q.get("limit") else None,
            "num": str(i),
        })
    if not raw_questions:
        raise TestParseError("no questions found")
    return hdr, sections, raw_questions


def split_tests(text: str):
    blocks = re.split(r"^===\s*TEST[^\n]*===\s*$", text, flags=re.M)
    return [b.strip() for b in blocks if b.strip() and "LEVEL:" in b]


def parse_header(block: str) -> dict:
    hdr = {}
    for key in ("LEVEL", "DOMAIN", "TITLE", "FOCUS"):
        m = re.search(rf"^{key}:\s*(.+)$", block, flags=re.M)
        if m:
            hdr[key.lower()] = m.group(1).strip()
    for req in ("level", "domain", "title"):
        if req not in hdr:
            raise TestParseError(f"missing {req.upper()}: header line")
    hdr["level"] = hdr["level"].upper()
    if hdr["level"] not in LEVELS:
        raise TestParseError(f"unknown level {hdr['level']!r}")
    return hdr


def parse_passage(block: str):
    m = re.search(r"^PASSAGE\s*$(.*?)^QUESTIONS\s*$", block, flags=re.M | re.S)
    if not m:
        raise TestParseError("could not find PASSAGE ... QUESTIONS sections")
    body = m.group(1).strip()
    parts = re.split(r"^##\s*(.+)$", body, flags=re.M)
    sections = []
    for i in range(1, len(parts) - 1, 2):
        heading = parts[i].strip()
        text = re.sub(r"\s*\n\s*", " ", parts[i + 1].strip())
        if text:
            sections.append({"paragraph": len(sections) + 1, "heading": heading, "text": text})
    if len(sections) != 5:
        raise TestParseError(f"expected 5 passage paragraphs, found {len(sections)}")
    return sections


def parse_questions(block: str):
    m = re.search(r"^QUESTIONS\s*$(.*)", block, flags=re.M | re.S)
    body = m.group(1)
    q_iter = list(re.finditer(r"^\s*(\d+)\.\s*\[(MC|TFNG|MATCH|GAP|SHORT)\]\s*(.*)$", body, flags=re.M))
    if not q_iter:
        raise TestParseError("no questions found (expected lines like '1. [MC] ...')")
    questions = []
    for idx, qm in enumerate(q_iter):
        start = qm.end()
        end = q_iter[idx + 1].start() if idx + 1 < len(q_iter) else len(body)
        chunk = body[start:end]
        code = qm.group(2)
        qtext = qm.group(3).strip()

        limit = None
        lm = re.search(r"\(?\s*LIMIT:\s*([^)\n]+?)\s*\)?\s*$", qtext)
        if lm:
            limit = lm.group(1).strip()
            qtext = qtext[:lm.start()].strip()
        lm2 = re.search(r"^LIMIT:\s*(.+)$", chunk, flags=re.M)
        if lm2:
            limit = lm2.group(1).strip()

        options = re.findall(r"^\s*([A-E])\)\s*(.+)$", chunk, flags=re.M)

        am = re.search(r"^ANSWER:\s*(.+)$", chunk, flags=re.M)
        if not am:
            raise TestParseError(f"question {qm.group(1)}: missing ANSWER line")
        answer = am.group(1).strip()

        ev_para, ev_quote = None, None
        em = re.search(r'^EVIDENCE:\s*P(\d)\s*[""](.+?)[""]\s*$', chunk, flags=re.M)
        if em:
            ev_para, ev_quote = int(em.group(1)), em.group(2).strip()

        wm = re.search(r"^WHY:\s*(.+?)(?=^\s*[A-Z]+:|\Z)", chunk, flags=re.M | re.S)
        why = re.sub(r"\s*\n\s*", " ", wm.group(1).strip()) if wm else ""

        questions.append({
            "code": code, "text": qtext, "options": [o[1].strip() for o in options],
            "answer": answer, "ev_para": ev_para, "ev_quote": ev_quote,
            "why": why, "limit": limit, "num": qm.group(1),
        })
    return questions


def find_quote(quote: str, sections, preferred_para):
    """Return (paragraph, exact_substring) for a quote, or (None, None)."""
    order = [preferred_para] + [s["paragraph"] for s in sections if s["paragraph"] != preferred_para]
    for para in order:
        if para is None:
            continue
        text = sections[para - 1]["text"]
        if quote in text:
            return para, quote
        nt, nq = norm_quotes(text).lower(), norm_quotes(quote).lower()
        pos = nt.find(nq)
        if pos >= 0:
            return para, text[pos:pos + len(quote)]
    return None, None


def build_topic_json(hdr, sections, raw_questions, topic_id, warnings):
    questions, answer_key = [], []
    for i, rq in enumerate(raw_questions):
        qtype = TYPE_MAP[rq["code"]]
        qid = f"Q{i + 1:02d}"
        q = {
            "id": qid,
            "type": qtype,
            "skill": SKILL_BY_TYPE[qtype],
            "difficulty": hdr["level"],
        }

        if rq["ev_quote"]:
            para, exact = find_quote(rq["ev_quote"], sections, rq["ev_para"])
            if para:
                if para != rq["ev_para"]:
                    warnings.append(f"{topic_id} {qid}: evidence quote found in P{para}, not P{rq['ev_para']} — corrected")
                q["evidence"] = {"paragraph": para, "heading": sections[para - 1]["heading"], "anchor": exact}
            else:
                warnings.append(f"{topic_id} {qid}: evidence quote not found in passage — evidence dropped")
        else:
            warnings.append(f"{topic_id} {qid}: no EVIDENCE line")

        q["explanation"] = rq["why"]

        if qtype == "multiple_choice":
            if len(rq["options"]) < 2:
                raise TestParseError(f"{qid}: multiple choice needs options A) B) ...")
            letter = rq["answer"].strip().upper()[:1]
            idx = ord(letter) - 65
            if not (0 <= idx < len(rq["options"])):
                raise TestParseError(f"{qid}: MC answer {rq['answer']!r} is not one of the options")
            q["question"] = rq["text"]
            q["options"] = rq["options"]
            q["answer"] = letter
            q["answer_text"] = rq["options"][idx]
        elif qtype == "true_false_not_given":
            ans = rq["answer"].strip().upper()
            if ans not in ("TRUE", "FALSE", "NOT GIVEN"):
                raise TestParseError(f"{qid}: TFNG answer must be TRUE/FALSE/NOT GIVEN, got {rq['answer']!r}")
            q["statement"] = rq["text"]
            q["answer"] = ans
        elif qtype == "matching_information":
            m = re.search(r"[1-5]", rq["answer"])
            if not m:
                raise TestParseError(f"{qid}: MATCH answer must contain a paragraph number 1-5")
            q["question"] = rq["text"]
            q["options"] = [f"Paragraph {n}" for n in range(1, 6)]
            q["answer"] = f"Paragraph {m.group(0)}"
        else:
            q["question"] = rq["text"]
            if rq["limit"]:
                lim = rq["limit"].upper()
                q["word_limit"] = lim if "NO MORE THAN" in lim else f"NO MORE THAN {lim}"
            q["answer"] = rq["answer"]
            full = norm_quotes(" ".join(s["text"] for s in sections)).lower()
            if norm_quotes(rq["answer"]).lower() not in full:
                warnings.append(f"{topic_id} {qid}: answer {rq['answer']!r} does not appear verbatim in the passage")

        questions.append(q)
        answer_key.append({"id": qid, "answer": q["answer"], "explanation": q["explanation"]})

    full_text = "\n\n".join(
        f"Paragraph {s['paragraph']} — {s['heading']}\n{s['text']}" for s in sections)

    return {
        "dataset_version": "3.0-authored",
        "content_status": "Original IELTS-style practice; not official IELTS material.",
        "cefr": {
            "level": hdr["level"],
            "label": CEFR_LABEL[hdr["level"]],
            "language_profile": CEFR_PROFILE[hdr["level"]],
        },
        "topic": {
            "id": topic_id,
            "domain": hdr["domain"],
            "title": f"{hdr['domain']}: {hdr['title']}",
            "focus": hdr.get("focus", hdr["title"]),
        },
        "recommended_time_minutes": RECOMMENDED_MINUTES[hdr["level"]],
        "candidate_instructions":
            f"Read all five sections. Answer Questions 1-{len(questions)}. Follow the stated word limits exactly.",
        "passage": {"sections": sections, "full_text": full_text},
        "question_count": len(questions),
        "questions": questions,
        "answer_key": answer_key,
    }


def next_topic_id(manifest, level):
    nums = [int(f["id"].split("-")[1]) for f in manifest["files"]
            if f["level"] == level and re.fullmatch(rf"{level}-\d+", f["id"])]
    return f"{level}-{(max(nums) + 1 if nums else 1):03d}"


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    dry_run = "--dry-run" in argv
    if not args:
        print(__doc__)
        return 2

    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    existing_files = {f["file"] for f in manifest["files"]}
    imported, warnings, errors = [], [], []

    def import_one(parsed):
        hdr, sections, raw_qs = parsed
        topic_id = next_topic_id(manifest, hdr["level"])
        topic = build_topic_json(hdr, sections, raw_qs, topic_id, warnings)

        fname = f"{topic_id.replace('-', '_')}_{slugify(hdr['domain'] + ' ' + hdr['title'])}.json"
        rel = f"{hdr['level']}/{fname}"
        if rel in existing_files:
            raise TestParseError(f"file {rel} already exists in manifest")

        if not dry_run:
            out = DATA / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(topic, ensure_ascii=False, indent=2), encoding="utf-8")

        manifest["files"].append({
            "id": topic_id,
            "level": hdr["level"],
            "domain": hdr["domain"],
            "title": topic["topic"]["title"],
            "file": rel,
            "questions": len(topic["questions"]),
        })
        existing_files.add(rel)
        words = sum(len(s["text"].split()) for s in sections)
        imported.append(
            f"{topic_id} [{hdr['level']}] {topic['topic']['title']} — "
            f"{len(topic['questions'])} questions, {words}-word passage → data/{rel}")

    for path in args:
        raw = Path(path).read_text(encoding="utf-8")
        payload = extract_json(raw)

        if payload is not None:
            for bi, t in enumerate(json_test_list(payload), 1):
                try:
                    import_one(parse_json_test(t))
                except TestParseError as e:
                    title = t.get("title", "?") if isinstance(t, dict) else "?"
                    errors.append(f"{path} test #{bi} ({title}): {e}")
            continue

        text = norm_quotes(raw)
        blocks = split_tests(text)
        if not blocks:
            errors.append(f"{path}: neither valid JSON nor '=== TEST ===' blocks found")
            continue
        for bi, block in enumerate(blocks, 1):
            try:
                import_one((parse_header(block), parse_passage(block), parse_questions(block)))
            except TestParseError as e:
                errors.append(f"{path} test #{bi} ({block[:60].splitlines()[0]}…): {e}")

    if imported and not dry_run:
        manifest["total_topics"] = len(manifest["files"])
        manifest["total_questions"] = sum(f["questions"] for f in manifest["files"])
        (DATA / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    label = "Validated (dry run)" if dry_run else "Imported"
    print(f"{label}: {len(imported)} test(s)")
    for line in imported:
        print("  +", line)
    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print("  !", w)
    if errors:
        print(f"\nErrors ({len(errors)}) — these tests were skipped:")
        for e in errors:
            print("  x", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
