/* IELTS Reading Lab — static SPA for GitHub Pages */
(() => {
  "use strict";

  const app = document.getElementById("app");
  const timerEl = document.getElementById("timer");

  const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
  const TYPE_LABELS = {
    multiple_choice: "Multiple choice",
    true_false_not_given: "True / False / Not Given",
    matching_information: "Matching information",
    sentence_completion: "Sentence completion",
    short_answer: "Short answer",
  };

  let manifest = null;
  const topicCache = new Map();

  // ---------- storage ----------
  const store = {
    getProgress() {
      try { return JSON.parse(localStorage.getItem("irl-progress")) || {}; }
      catch { return {}; }
    },
    saveAttempt(topicId, score, total) {
      const p = store.getProgress();
      const prev = p[topicId];
      p[topicId] = {
        last: score,
        best: prev ? Math.max(prev.best, score) : score,
        total,
        date: new Date().toISOString(),
        attempts: prev ? prev.attempts + 1 : 1,
      };
      localStorage.setItem("irl-progress", JSON.stringify(p));
    },
    getDraft(topicId) {
      try { return JSON.parse(localStorage.getItem("irl-draft-" + topicId)); }
      catch { return null; }
    },
    saveDraft(topicId, draft) {
      localStorage.setItem("irl-draft-" + topicId, JSON.stringify(draft));
    },
    clearDraft(topicId) {
      localStorage.removeItem("irl-draft-" + topicId);
    },
  };

  // ---------- theme ----------
  const themeToggle = document.getElementById("themeToggle");
  function applyTheme(t) {
    document.documentElement.dataset.theme = t;
    localStorage.setItem("irl-theme", t);
  }
  themeToggle.addEventListener("click", () => {
    applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
  });
  applyTheme(
    localStorage.getItem("irl-theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
  );

  // ---------- utils ----------
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const normalize = (s) =>
    String(s ?? "")
      .toLowerCase()
      .replace(/[’‘]/g, "'")
      .replace(/[“”]/g, '"')
      .replace(/[^\p{L}\p{N}\s]/gu, " ")
      .replace(/\s+/g, " ")
      .trim();

  function fmtTime(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  function scoreClass(pct) {
    return pct >= 80 ? "good" : pct >= 55 ? "mid" : "low";
  }

  async function loadManifest() {
    if (manifest) return manifest;
    const res = await fetch("data/manifest.json");
    if (!res.ok) throw new Error("Failed to load manifest: " + res.status);
    manifest = await res.json();
    return manifest;
  }

  async function loadTopic(entry) {
    if (topicCache.has(entry.id)) return topicCache.get(entry.id);
    const res = await fetch("data/" + entry.file);
    if (!res.ok) throw new Error("Failed to load topic: " + res.status);
    const data = await res.json();
    topicCache.set(entry.id, data);
    return data;
  }

  // ---------- timer ----------
  let timerInterval = null;
  function stopTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
    timerEl.hidden = true;
    timerEl.classList.remove("low");
  }
  function startTimer(totalSeconds, startedAt, onExpire) {
    stopTimer();
    timerEl.hidden = false;
    const tick = () => {
      const elapsed = Math.floor((Date.now() - startedAt) / 1000);
      const remaining = totalSeconds - elapsed;
      if (remaining <= 0) {
        timerEl.textContent = "0:00";
        stopTimer();
        onExpire();
        return;
      }
      timerEl.textContent = fmtTime(remaining);
      timerEl.classList.toggle("low", remaining <= 180);
    };
    tick();
    timerInterval = setInterval(tick, 1000);
  }

  // ---------- router ----------
  window.addEventListener("hashchange", route);

  function route() {
    stopTimer();
    const hash = location.hash || "#/";
    const testMatch = hash.match(/^#\/test\/([\w-]+)/);
    if (testMatch) {
      renderTest(testMatch[1]).catch(showError);
    } else {
      const params = new URLSearchParams(hash.split("?")[1] || "");
      renderHome(params).catch(showError);
    }
  }

  function showError(err) {
    app.innerHTML = `<div class="empty-note">Something went wrong: ${esc(err.message)}.<br>
      <a class="back-link" href="#/">← Back to library</a></div>`;
    console.error(err);
  }

  // ---------- home view ----------
  async function renderHome(params) {
    app.innerHTML = `<div class="loading">Loading library…</div>`;
    const m = await loadManifest();
    const progress = store.getProgress();

    const level = params.get("level") || "A1";
    const domain = params.get("domain") || "";
    const query = params.get("q") || "";

    const domains = [...new Set(m.files.map((f) => f.domain))].sort();
    const doneCount = Object.keys(progress).length;
    const attempts = Object.values(progress).reduce((a, p) => a + p.attempts, 0);
    const avgBest = doneCount
      ? Math.round(Object.values(progress).reduce((a, p) => a + (p.best / p.total) * 100, 0) / doneCount)
      : 0;

    const filtered = m.files.filter((f) =>
      f.level === level &&
      (!domain || f.domain === domain) &&
      (!query || f.title.toLowerCase().includes(query.toLowerCase()))
    );

    const levelDone = (lv) => m.files.filter((f) => f.level === lv && progress[f.id]).length;
    const levelTotal = (lv) => m.files.filter((f) => f.level === lv).length;

    app.innerHTML = `
      <section class="hero">
        <h1>IELTS-style Reading Practice</h1>
        <p>${m.total_topics} passages · ${m.total_questions.toLocaleString()} questions · CEFR A1–C2 · your progress is saved in this browser</p>
      </section>

      <div class="stats-row">
        <div class="stat-card"><div class="num">${doneCount} / ${m.total_topics}</div><div class="lbl">Tests completed</div></div>
        <div class="stat-card"><div class="num">${attempts}</div><div class="lbl">Total attempts</div></div>
        <div class="stat-card"><div class="num">${doneCount ? avgBest + "%" : "—"}</div><div class="lbl">Average best score</div></div>
      </div>

      <nav class="level-tabs">
        ${LEVELS.map((lv) => `
          <button class="level-tab ${lv === level ? "active" : ""}" data-level="${lv}">
            ${lv} <span class="count">${levelDone(lv)}/${levelTotal(lv)}</span>
          </button>`).join("")}
      </nav>

      <div class="filters">
        <input type="search" id="searchBox" placeholder="Search topics…" value="${esc(query)}">
        <select id="domainSelect">
          <option value="">All domains</option>
          ${domains.map((d) => `<option value="${esc(d)}" ${d === domain ? "selected" : ""}>${esc(d)}</option>`).join("")}
        </select>
      </div>

      <div class="topic-grid">
        ${filtered.map((f) => topicCardHTML(f, progress)).join("") ||
          `<div class="empty-note">No topics match your filters.</div>`}
      </div>
    `;

    const nav = (patch) => {
      const p = new URLSearchParams({ level, domain, q: query });
      for (const [k, v] of Object.entries(patch)) p.set(k, v);
      for (const k of [...p.keys()]) if (!p.get(k)) p.delete(k);
      location.hash = "#/?" + p.toString();
    };

    app.querySelectorAll(".level-tab").forEach((btn) =>
      btn.addEventListener("click", () => nav({ level: btn.dataset.level, domain: "", q: "" })));
    app.querySelector("#domainSelect").addEventListener("change", (e) => nav({ domain: e.target.value }));

    let searchDebounce;
    app.querySelector("#searchBox").addEventListener("input", (e) => {
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => nav({ q: e.target.value }), 350);
    });
  }

  function topicCardHTML(f, progress) {
    const p = progress[f.id];
    const draft = store.getDraft(f.id);
    let scoreBadge = "";
    if (p) {
      const pct = Math.round((p.best / p.total) * 100);
      scoreBadge = `<span class="badge score-${scoreClass(pct)}">Best ${p.best}/${p.total}</span>`;
    } else if (draft) {
      scoreBadge = `<span class="badge in-progress">In progress</span>`;
    }
    return `
      <a class="topic-card" href="#/test/${esc(f.id)}">
        <div class="title">${esc(f.title)}</div>
        <div class="meta">
          <span class="badge level">${esc(f.level)}</span>
          <span class="badge">${esc(f.domain)}</span>
          <span class="badge">${f.questions} questions</span>
          ${scoreBadge}
        </div>
      </a>`;
  }

  // ---------- test view ----------
  async function renderTest(topicId) {
    app.innerHTML = `<div class="loading">Loading test…</div>`;
    const m = await loadManifest();
    const entry = m.files.find((f) => f.id === topicId);
    if (!entry) throw new Error("Unknown topic " + topicId);
    const topic = await loadTopic(entry);

    const draft = store.getDraft(topicId);
    const state = {
      answers: (draft && draft.answers) || {},
      startedAt: (draft && draft.startedAt) || Date.now(),
      submitted: false,
      results: null,
    };
    if (!draft) store.saveDraft(topicId, { answers: state.answers, startedAt: state.startedAt });

    const durationSec = (topic.recommended_time_minutes || 30) * 60;

    app.innerHTML = `
      <a class="back-link" href="#/?level=${esc(entry.level)}">← Back to ${esc(entry.level)} library</a>
      <div class="test-header">
        <h1>${esc(topic.topic.title)}</h1>
        <div class="actions">
          <button class="btn" id="restartBtn">Restart</button>
          <button class="btn primary" id="submitTopBtn">Submit answers</button>
        </div>
      </div>
      <div class="test-layout">
        <div class="passage-pane" id="passagePane"></div>
        <div class="questions-pane" id="questionsPane"></div>
      </div>
    `;

    const passagePane = document.getElementById("passagePane");
    const questionsPane = document.getElementById("questionsPane");

    renderPassage(passagePane, topic, null);
    renderQuestions(questionsPane, topic, state);

    document.getElementById("restartBtn").addEventListener("click", () => {
      if (!confirm("Restart this test? Your current answers will be cleared.")) return;
      store.clearDraft(topicId);
      state.answers = {};
      state.startedAt = Date.now();
      state.submitted = false;
      state.results = null;
      store.saveDraft(topicId, { answers: {}, startedAt: state.startedAt });
      renderPassage(passagePane, topic, null);
      renderQuestions(questionsPane, topic, state);
      startTimer(durationSec, state.startedAt, expire);
    });
    document.getElementById("submitTopBtn").addEventListener("click", () => submit(false));

    function expire() {
      if (!state.submitted) {
        alert("Time is up — your answers have been submitted.");
        submit(true);
      }
    }

    function setAnswer(qid, value) {
      state.answers[qid] = value;
      store.saveDraft(topicId, { answers: state.answers, startedAt: state.startedAt });
      updateProgressNote();
    }

    function updateProgressNote() {
      const note = document.getElementById("progressNote");
      if (!note) return;
      const answered = topic.questions.filter((q) => (state.answers[q.id] ?? "") !== "").length;
      note.textContent = `${answered} of ${topic.questions.length} answered`;
    }

    function submit(auto) {
      if (state.submitted) return;
      const answered = topic.questions.filter((q) => (state.answers[q.id] ?? "") !== "").length;
      if (!auto && answered < topic.questions.length &&
          !confirm(`You have answered ${answered} of ${topic.questions.length} questions. Submit anyway?`)) {
        return;
      }
      stopTimer();
      state.submitted = true;
      state.results = grade(topic, state.answers);
      store.saveAttempt(topicId, state.results.score, topic.questions.length);
      store.clearDraft(topicId);
      renderQuestions(questionsPane, topic, state);
      window.scrollTo({ top: 0, behavior: "smooth" });
      const topBtn = document.getElementById("submitTopBtn");
      topBtn.textContent = "Try again";
      topBtn.onclick = () => document.getElementById("restartBtn").click();
    }

    // expose for question renderers
    state.setAnswer = setAnswer;
    state.submit = submit;
    state.showEvidence = (q) => {
      renderPassage(passagePane, topic, q);
      const mark = passagePane.querySelector("mark.evidence");
      if (mark) mark.scrollIntoView({ behavior: "smooth", block: "center" });
    };

    startTimer(durationSec, state.startedAt, expire);
    updateProgressNote();
  }

  function renderPassage(pane, topic, evidenceQ) {
    const sections = topic.passage.sections || [];
    pane.innerHTML = `
      <h2>Reading passage</h2>
      <div class="instructions">${esc(topic.candidate_instructions || "")}
        · Recommended time: ${topic.recommended_time_minutes} minutes</div>
      ${sections.map((s) => {
        let text = esc(s.text);
        if (evidenceQ && evidenceQ.evidence &&
            evidenceQ.evidence.paragraph === s.paragraph && evidenceQ.evidence.anchor) {
          const anchor = esc(evidenceQ.evidence.anchor);
          text = text.split(anchor).join(`<mark class="evidence">${anchor}</mark>`);
        }
        return `
          <div class="passage-section">
            <h3>Paragraph ${s.paragraph} — ${esc(s.heading)}</h3>
            <p>${text}</p>
          </div>`;
      }).join("")}
    `;
  }

  function renderQuestions(pane, topic, state) {
    pane.innerHTML = `
      ${topic.questions.map((q, i) => questionHTML(q, i + 1, state)).join("")}
      ${state.submitted ? resultBannerHTML(topic, state) : `
        <div class="submit-bar">
          <span class="progress-note" id="progressNote"></span>
          <button class="btn primary" id="submitBottomBtn">Submit answers</button>
        </div>`}
    `;

    if (!state.submitted) {
      pane.querySelector("#submitBottomBtn").addEventListener("click", () => state.submit(false));
    }

    // wire inputs
    topic.questions.forEach((q) => {
      const card = pane.querySelector(`[data-qid="${q.id}"]`);
      if (!card) return;

      if (q.type === "multiple_choice" || q.type === "matching_information") {
        card.querySelectorAll("input[type=radio]").forEach((input) => {
          input.addEventListener("change", () => {
            state.setAnswer(q.id, input.value);
            card.querySelectorAll(".opt").forEach((o) => o.classList.remove("selected"));
            input.closest(".opt").classList.add("selected");
          });
        });
      } else if (q.type === "true_false_not_given") {
        card.querySelectorAll(".tfng-btn").forEach((btn) => {
          btn.addEventListener("click", () => {
            state.setAnswer(q.id, btn.dataset.value);
            card.querySelectorAll(".tfng-btn").forEach((b) => b.classList.remove("selected"));
            btn.classList.add("selected");
          });
        });
      } else {
        const input = card.querySelector(".text-answer");
        if (input) input.addEventListener("input", () => state.setAnswer(q.id, input.value));
      }

      const evBtn = card.querySelector(".evidence-link");
      if (evBtn) evBtn.addEventListener("click", () => state.showEvidence(q));
    });

    if (state.submitted) {
      const first = pane.querySelector(".result-banner");
      if (first) pane.prepend(first);
    }
  }

  function questionHTML(q, num, state) {
    const userAnswer = state.answers[q.id] ?? "";
    const r = state.submitted ? state.results.byId[q.id] : null;
    const cardClass = r ? (r.correct ? "correct" : "incorrect") : "";
    const disabled = state.submitted ? "disabled" : "";

    let body = "";
    if (q.type === "multiple_choice") {
      body = `<div class="opt-list">
        ${q.options.map((opt, i) => {
          const letter = String.fromCharCode(65 + i);
          const selected = userAnswer === letter;
          let cls = selected ? "selected" : "";
          if (r) {
            if (letter === q.answer) cls = "right";
            else if (selected) cls = "wrong";
            else cls = "";
          }
          return `<label class="opt ${cls}">
            <input type="radio" name="${q.id}" value="${letter}" ${selected ? "checked" : ""} ${disabled}>
            <span class="opt-key">${letter}</span><span>${esc(opt)}</span>
          </label>`;
        }).join("")}
      </div>`;
    } else if (q.type === "matching_information") {
      body = `<div class="opt-list">
        ${q.options.map((opt) => {
          const selected = userAnswer === opt;
          let cls = selected ? "selected" : "";
          if (r) {
            if (opt === q.answer) cls = "right";
            else if (selected) cls = "wrong";
            else cls = "";
          }
          return `<label class="opt ${cls}">
            <input type="radio" name="${q.id}" value="${esc(opt)}" ${selected ? "checked" : ""} ${disabled}>
            <span>${esc(opt)}</span>
          </label>`;
        }).join("")}
      </div>`;
    } else if (q.type === "true_false_not_given") {
      body = `<div class="tfng-row">
        ${["TRUE", "FALSE", "NOT GIVEN"].map((v) => {
          const selected = userAnswer === v;
          let cls = selected ? "selected" : "";
          if (r) {
            if (v === q.answer) cls = "right";
            else if (selected) cls = "wrong";
            else cls = "";
          }
          return `<button class="tfng-btn ${cls}" data-value="${v}" ${disabled}>${v}</button>`;
        }).join("")}
      </div>`;
    } else {
      const cls = r ? (r.correct ? "right" : "wrong") : "";
      body = `
        ${q.word_limit ? `<div class="word-limit">${esc(q.word_limit)}</div>` : ""}
        <input class="text-answer ${cls}" type="text" value="${esc(userAnswer)}"
          placeholder="Type your answer…" ${disabled}>`;
    }

    let feedback = "";
    if (r) {
      feedback = `
        <div class="feedback">
          <span class="verdict ${r.correct ? "ok" : "bad"}">${r.correct ? "✓ Correct" : "✗ Incorrect"}</span>
          ${r.correct ? "" : `<div class="correct-answer"><strong>Correct answer:</strong> ${esc(displayAnswer(q))}</div>`}
          <p class="explanation">${esc(q.explanation || "")}</p>
          ${q.evidence ? `<button class="evidence-link">Show evidence in paragraph ${q.evidence.paragraph} (${esc(q.evidence.heading)})</button>` : ""}
        </div>`;
    }

    return `
      <div class="q-card ${cardClass}" data-qid="${q.id}">
        <div class="q-head">
          <span class="q-num">Q${num}</span>
          <span class="q-type">${TYPE_LABELS[q.type] || esc(q.type)} · ${esc(q.skill || "")}</span>
        </div>
        <p class="q-text">${esc(q.question || q.statement || "")}</p>
        ${body}
        ${feedback}
      </div>`;
  }

  function displayAnswer(q) {
    if (q.type === "multiple_choice") {
      return `${q.answer} — ${q.answer_text || q.options["ABCDE".indexOf(q.answer)] || ""}`;
    }
    return q.answer;
  }

  // ---------- grading ----------
  function grade(topic, answers) {
    const byId = {};
    let score = 0;
    const byType = {};
    for (const q of topic.questions) {
      const user = answers[q.id] ?? "";
      let correct = false;
      if (q.type === "sentence_completion" || q.type === "short_answer") {
        correct = normalize(user) !== "" && normalize(user) === normalize(q.answer);
      } else {
        correct = user === q.answer;
      }
      byId[q.id] = { correct, user };
      if (correct) score++;
      const t = byType[q.type] || { correct: 0, total: 0 };
      t.total++;
      if (correct) t.correct++;
      byType[q.type] = t;
    }
    return { score, byId, byType };
  }

  function resultBannerHTML(topic, state) {
    const total = topic.questions.length;
    const score = state.results.score;
    const pct = Math.round((score / total) * 100);
    const cls = scoreClass(pct);
    const message =
      pct >= 80 ? "Excellent work — you are reading at this level with confidence."
      : pct >= 55 ? "Good effort — review the explanations below to close the gaps."
      : "Keep practising — read the explanations and try the passage again.";
    return `
      <div class="result-banner">
        <div class="score-circle ${cls}">
          <span class="big">${score}/${total}</span>
          <span class="small">${pct}%</span>
        </div>
        <div class="result-detail">
          <h2>${message}</h2>
          <p>${esc(topic.topic.title)} · Level ${esc(topic.cefr.level)} (${esc(topic.cefr.label)})</p>
          <div class="type-breakdown">
            ${Object.entries(state.results.byType).map(([t, v]) => `
              <div class="type-chip">
                <div class="t-name">${TYPE_LABELS[t] || esc(t)}</div>
                <div class="t-score">${v.correct} / ${v.total}</div>
              </div>`).join("")}
          </div>
        </div>
      </div>`;
  }

  // ---------- boot ----------
  route();
})();
