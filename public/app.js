const state = {
  questions: [],
  activeSet: [],
  currentIndex: 0,
  answers: {},
  startedAt: null,
  timerId: null,
  user: JSON.parse(localStorage.getItem("eddyUser") || "null"),
  attempts: JSON.parse(localStorage.getItem("eddyAttempts") || "[]"),
  latestResult: null,
  selectedSubject: localStorage.getItem("eddySelectedSubject") || "full",
  selectedBundle: localStorage.getItem("eddySelectedBundle") || "full-pt4"
};

const SAT_BLUEPRINT = [
  {
    id: "full",
    label: "Full Digital SAT",
    section: "All",
    minutes: 134,
    questions: "Reading/Writing + Math",
    description: "A combined practice route with both scored SAT sections.",
    objectives: [
      "Reading and Writing: Craft and Structure",
      "Reading and Writing: Information and Ideas",
      "Reading and Writing: Standard English Conventions",
      "Reading and Writing: Expression of Ideas",
      "Math: Algebra",
      "Math: Advanced Math",
      "Math: Problem-Solving and Data Analysis",
      "Math: Geometry and Trigonometry"
    ],
    bundles: [
      { id: "full-pt4", title: "Practice Test 4 Full Bank", source: "College Board Practice Test 4 PDF", status: "available", mode: "All", practiceTest: 4, size: 120 },
      { id: "full-pt5", title: "Practice Test 5 Full Bank", source: "College Board Practice Test 5 PDF", status: "available", mode: "All", practiceTest: 5, size: 120 },
      { id: "full-adaptive-1", title: "Adaptive Full SAT Bundle", source: "Coming when more tests are imported", status: "locked", mode: "All", size: 0 },
      { id: "full-review-1", title: "Weakness Review Bundle", source: "Generated from student history", status: "locked", mode: "All", size: 0 }
    ]
  },
  {
    id: "rw",
    label: "Reading and Writing",
    section: "Reading and Writing",
    minutes: 64,
    questions: "Two modules",
    description: "Short passages and single multiple-choice questions across four content domains.",
    objectives: [
      "Craft and Structure",
      "Information and Ideas",
      "Standard English Conventions",
      "Expression of Ideas"
    ],
    bundles: [
      { id: "rw-pt4", title: "Practice Test 4 Reading/Writing", source: "College Board Practice Test 4 PDF", status: "available", mode: "Reading and Writing", practiceTest: 4, size: 66 },
      { id: "rw-pt5", title: "Practice Test 5 Reading/Writing", source: "College Board Practice Test 5 PDF", status: "available", mode: "Reading and Writing", practiceTest: 5, size: 66 },
      { id: "rw-domain-craft", title: "Craft and Structure Drill", source: "Coming from generated bank", status: "locked", mode: "Reading and Writing", size: 0 },
      { id: "rw-grammar", title: "Grammar and Expression Drill", source: "Coming from generated bank", status: "locked", mode: "Reading and Writing", size: 0 }
    ]
  },
  {
    id: "math",
    label: "Math",
    section: "Math",
    minutes: 70,
    questions: "Two modules",
    description: "Calculator-allowed SAT math practice across the official math domains.",
    objectives: [
      "Algebra",
      "Advanced Math",
      "Problem-Solving and Data Analysis",
      "Geometry and Trigonometry"
    ],
    bundles: [
      { id: "math-pt4", title: "Practice Test 4 Math", source: "College Board Practice Test 4 PDF", status: "available", mode: "Math", practiceTest: 4, size: 54 },
      { id: "math-pt5", title: "Practice Test 5 Math", source: "College Board Practice Test 5 PDF", status: "available", mode: "Math", practiceTest: 5, size: 54 },
      { id: "math-algebra", title: "Algebra and Functions Drill", source: "Coming from generated bank", status: "locked", mode: "Math", size: 0 },
      { id: "math-data-geo", title: "Data, Geometry, and Trig Drill", source: "Coming from generated bank", status: "locked", mode: "Math", size: 0 }
    ]
  }
];

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const els = {
  loginPanel: $("#loginPanel"),
  accountMenu: $("#accountMenu"),
  profileTitle: $("#profileTitle"),
  signedOutStep: $("#signedOutStep"),
  signedInStep: $("#signedInStep"),
  signedInName: $("#signedInName"),
  signedInEmail: $("#signedInEmail"),
  llmStatus: $("#llmStatus"),
  llmDescription: $("#llmDescription"),
  studentName: $("#studentName"),
  studentEmail: $("#studentEmail"),
  studentPassword: $("#studentPassword"),
  passwordField: $("#passwordField"),
  loginButton: $("#loginButton"),
  registerButton: $("#registerButton"),
  logoutButton: $("#logoutButton"),
  openAiLoginButton: $("#openAiLoginButton"),
  codexLogoutButton: $("#codexLogoutButton"),
  authStatus: $("#authStatus"),
  subjectCards: $("#subjectCards"),
  bundleHeading: $("#bundleHeading"),
  bundleDescription: $("#bundleDescription"),
  bundleCards: $("#bundleCards"),
  sectionFilter: $("#sectionFilter"),
  bundleFilter: $("#bundleFilter"),
  startTestButton: $("#startTestButton"),
  questionSection: $("#questionSection"),
  questionConcept: $("#questionConcept"),
  timer: $("#timer"),
  questionCounter: $("#questionCounter"),
  questionPrompt: $("#questionPrompt"),
  choices: $("#choices"),
  previousButton: $("#previousButton"),
  nextButton: $("#nextButton"),
  submitButton: $("#submitButton"),
  chatLog: $("#chatLog"),
  chatInput: $("#chatInput"),
  sendChatButton: $("#sendChatButton"),
  quickPrompts: $(".quick-prompts"),
  tutorMode: $("#tutorMode"),
  attemptCount: $("#attemptCount"),
  avgScore: $("#avgScore"),
  scoreBig: $("#scoreBig"),
  scoreDetail: $("#scoreDetail"),
  conceptBreakdown: $("#conceptBreakdown"),
  focusConcept: $("#focusConcept"),
  focusExplanation: $("#focusExplanation"),
  similarQuestions: $("#similarQuestions"),
  answerReview: $("#answerReview"),
  masteryList: $("#masteryList"),
  progressChart: $("#progressChart")
};

function shuffle(items) {
  return [...items].sort(() => Math.random() - 0.5);
}

function userId() {
  return state.user?.id || state.user?.email || "demo-user";
}

function isSignedIn() {
  return Boolean(state.user);
}

function trackEvent(event, properties = {}) {
  const payload = JSON.stringify({ event, properties });
  if (navigator.sendBeacon) {
    navigator.sendBeacon("/api/events", new Blob([payload], { type: "application/json" }));
    return;
  }
  fetch("/api/events", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: payload,
    keepalive: true
  }).catch(() => {});
}

function requireSignedIn(action = "practice") {
  if (isSignedIn()) return true;
  els.authStatus.textContent = `Sign in or create an Eddy account to ${action}.`;
  if (els.accountMenu) els.accountMenu.open = true;
  els.loginPanel.classList.add("attention");
  setTimeout(() => els.loginPanel.classList.remove("attention"), 900);
  return false;
}

function attemptsStorageKey() {
  return `eddyAttempts:${userId()}`;
}

function saveLocal() {
  localStorage.setItem(attemptsStorageKey(), JSON.stringify(state.attempts));
  if (state.user) localStorage.setItem("eddyUser", JSON.stringify(state.user));
}

function loadLocalAttempts() {
  const userAttempts = localStorage.getItem(attemptsStorageKey());
  const legacyAttempts = !state.user ? localStorage.getItem("eddyAttempts") : null;
  state.attempts = JSON.parse(userAttempts || legacyAttempts || "[]");
}

function formatTime(ms) {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function setView(viewId) {
  $$(".view").forEach((view) => view.classList.toggle("active", view.id === viewId));
  $$(".nav-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.view === viewId));
  $("#viewTitle").textContent = {
    landingView: "SAT Practice",
    practiceView: "Practice Test",
    reviewView: "Review and Concepts",
    progressView: "Progress Tracker"
  }[viewId];
  if (viewId === "progressView") drawProgress();
}

function currentQuestion() {
  return state.activeSet[state.currentIndex];
}

function activeSubject() {
  return SAT_BLUEPRINT.find((subject) => subject.id === state.selectedSubject) || SAT_BLUEPRINT[0];
}

function activeBundle() {
  const subject = activeSubject();
  return subject.bundles.find((bundle) => bundle.id === state.selectedBundle)
    || subject.bundles.find((bundle) => bundle.status === "available")
    || subject.bundles[0];
}

function setSubject(subjectId) {
  state.selectedSubject = subjectId;
  const availableBundle = activeSubject().bundles.find((bundle) => bundle.status === "available") || activeSubject().bundles[0];
  state.selectedBundle = availableBundle.id;
  localStorage.setItem("eddySelectedSubject", state.selectedSubject);
  localStorage.setItem("eddySelectedBundle", state.selectedBundle);
  syncSelectorsFromSelection();
  renderLanding();
}

function setBundle(bundleId) {
  state.selectedBundle = bundleId;
  localStorage.setItem("eddySelectedBundle", state.selectedBundle);
  syncSelectorsFromSelection();
  renderLanding();
}

function syncSelectorsFromSelection() {
  const subject = activeSubject();
  const bundle = activeBundle();
  els.sectionFilter.value = bundle.mode || subject.section || "All";
  renderBundleFilter();
}

function renderBundleFilter() {
  const subject = activeSubject();
  els.bundleFilter.innerHTML = subject.bundles.map((bundle) => (
    `<option value="${bundle.id}" ${bundle.id === state.selectedBundle ? "selected" : ""} ${bundle.status !== "available" ? "disabled" : ""}>${bundle.title}${bundle.status !== "available" ? " (soon)" : ""}</option>`
  )).join("");
}

function questionsForBundle(bundle) {
  const mode = bundle.mode || "All";
  return state.questions.filter((question) => {
    if (mode !== "All" && question.section !== mode) return false;
    if (bundle.practiceTest && question.metadata?.practiceTest !== bundle.practiceTest) return false;
    return true;
  });
}

function bundleQuestionCount(bundle) {
  if (bundle.status !== "available") return Number(bundle.size || 0);
  return questionsForBundle(bundle).length;
}

function renderLanding() {
  const subject = activeSubject();
  els.subjectCards.innerHTML = SAT_BLUEPRINT.map((item) => (
    `<button class="subject-card ${item.id === subject.id ? "active" : ""}" type="button" data-subject="${item.id}">
      <span>${item.questions}</span>
      <strong>${item.label}</strong>
      <small>${item.minutes} minutes</small>
      <ul>${item.objectives.slice(0, 4).map((objective) => `<li>${objective}</li>`).join("")}</ul>
    </button>`
  )).join("");

  els.bundleHeading.textContent = subject.label;
  els.bundleDescription.textContent = subject.description;
  els.bundleCards.innerHTML = subject.bundles.map((bundle) => (
    `<button class="bundle-card ${bundle.id === state.selectedBundle ? "active" : ""} ${bundle.status !== "available" ? "locked" : ""}" type="button" data-bundle="${bundle.id}" ${bundle.status !== "available" ? "disabled" : ""}>
      <span>${bundle.status === "available" ? "Ready" : "Coming soon"}</span>
      <strong>${bundle.title}</strong>
      <small>${bundle.source}</small>
      <em>${bundle.status === "available" ? `${bundleQuestionCount(bundle)} questions in this prototype set` : "Add more PDFs or generated questions to unlock"}</em>
    </button>`
  )).join("");

  $$(".subject-card").forEach((card) => card.addEventListener("click", () => setSubject(card.dataset.subject)));
  $$(".bundle-card:not(.locked)").forEach((card) => card.addEventListener("click", () => setBundle(card.dataset.bundle)));
}

function renderQuestion() {
  if (!state.activeSet.length) return;
  const question = currentQuestion();
  els.questionSection.textContent = question.section;
  els.questionConcept.textContent = question.concept;
  els.questionCounter.textContent = `Question ${state.currentIndex + 1} of ${state.activeSet.length}`;
  els.questionPrompt.innerHTML = renderMathText(question.prompt);
  els.choices.innerHTML = "";
  const choices = Array.isArray(question.choices) ? question.choices : [];

  if (question.metadata?.image) {
    const figure = document.createElement("figure");
    figure.className = "question-figure";
    figure.innerHTML = `<img src="${question.metadata.image}" alt="Figure for ${question.id}">`;
    els.choices.appendChild(figure);
  }

  if (!choices.length) {
    const wrapper = document.createElement("label");
    wrapper.className = "free-response";
    wrapper.innerHTML = `<span>Your answer</span>`;
    const input = document.createElement("input");
    input.type = "text";
    input.inputMode = "decimal";
    input.autocomplete = "off";
    input.placeholder = "Type a number, decimal, or fraction";
    input.value = state.answers[question.id] || "";
    input.addEventListener("input", () => {
      state.answers[question.id] = input.value;
    });
    wrapper.appendChild(input);
    els.choices.appendChild(wrapper);
  }

  choices.forEach((choice) => {
    const key = choice.slice(0, 1);
    const button = document.createElement("button");
    button.className = `choice ${state.answers[question.id] === key ? "selected" : ""}`;
    button.type = "button";
    button.innerHTML = `<span class="choice-key">${key}</span><span>${renderMathText(choice.slice(3))}</span>`;
    button.addEventListener("click", () => {
      state.answers[question.id] = key;
      renderQuestion();
    });
    els.choices.appendChild(button);
  });

  els.previousButton.disabled = state.currentIndex === 0;
  els.nextButton.classList.toggle("hidden", state.currentIndex === state.activeSet.length - 1);
  els.submitButton.classList.toggle("hidden", state.currentIndex !== state.activeSet.length - 1);
}

function normalizeAnswer(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/^0+(?=\d)/, "")
    .replace(/\s+/g, "")
    .replace(/^\./, "0.");
}

function correctAnswers(answer) {
  return String(answer || "")
    .split(";")
    .map(normalizeAnswer)
    .filter(Boolean);
}

function isCorrectAnswer(selected, answer) {
  return correctAnswers(answer).includes(normalizeAnswer(selected));
}

function resetPracticeSession() {
  clearInterval(state.timerId);
  state.timerId = null;
  state.activeSet = [];
  state.currentIndex = 0;
  state.answers = {};
  state.startedAt = null;
  els.timer.textContent = "00:00";
  els.questionSection.textContent = "Section";
  els.questionConcept.textContent = "Concept";
  els.questionCounter.textContent = "Question 1";
  els.questionPrompt.textContent = "";
  els.choices.innerHTML = "";
  els.chatLog.innerHTML = "";
  els.tutorMode.textContent = "Local";
  setView("landingView");
}

function addChatMessage(role, text) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  if (role === "agent") {
    message.innerHTML = renderChatMarkdown(text);
  } else {
    message.textContent = text;
  }
  els.chatLog.appendChild(message);
  els.chatLog.scrollTop = els.chatLog.scrollHeight;
  return message;
}

function escapeHtml(text) {
  return String(text || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderMathText(text) {
  return escapeHtml(text)
    .replace(/\^(-?\d+)/g, "<sup>$1</sup>");
}

function renderInlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>");
}

function renderChatMarkdown(text) {
  const lines = String(text || "").trim().split(/\r?\n/);
  const html = [];
  let listItems = [];

  const flushList = () => {
    if (!listItems.length) return;
    html.push(`<ul>${listItems.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</ul>`);
    listItems = [];
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushList();
      continue;
    }
    const heading = trimmed.match(/^#{1,6}\s+(.+)$/);
    if (heading) {
      flushList();
      html.push(`<p class="chat-heading">${renderInlineMarkdown(heading[1])}</p>`);
      continue;
    }
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (bullet || numbered) {
      listItems.push((bullet || numbered)[1]);
      continue;
    }
    flushList();
    html.push(`<p>${renderInlineMarkdown(trimmed)}</p>`);
  }
  flushList();
  return html.join("");
}

window.renderChatMarkdown = renderChatMarkdown;

function startTimer() {
  clearInterval(state.timerId);
  state.startedAt = Date.now();
  state.timerId = setInterval(() => {
    els.timer.textContent = formatTime(Date.now() - state.startedAt);
  }, 500);
}

function startSet() {
  if (!requireSignedIn("start a practice set")) return;
  const bundle = activeBundle();
  const pool = questionsForBundle(bundle);
  state.activeSet = shuffle(pool);
  state.currentIndex = 0;
  state.answers = {};
  els.chatLog.innerHTML = "";
  addChatMessage("agent", "I’m here. Ask for a hint, a concept check, or help eliminating choices. I’ll keep it clear and not overdo it.");
  trackEvent("practice_set_started", {
    bundleId: bundle.id,
    section: bundle.mode || "All",
    questionCount: state.activeSet.length
  });
  startTimer();
  renderQuestion();
  setView("practiceView");
}

async function scoreAttemptOnServer(questionIds, answers) {
  try {
    const response = await fetch("/api/scoring/score", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ questionIds, answers })
    });
    if (!response.ok) return null;
    const data = await response.json();
    return data.scoring || null;
  } catch {
    return null;
  }
}

async function scoreActiveSet() {
  clearInterval(state.timerId);
  const results = state.activeSet.map((question) => {
    const selected = state.answers[question.id] || "";
    return {
      id: question.id,
      prompt: question.prompt,
      section: question.section,
      concept: question.concept,
      skill: question.skill,
      answer: question.answer,
      selected,
      correct: isCorrectAnswer(selected, question.answer),
      explanation: question.explanation,
      logic: question.logic,
      tutorial: question.tutorial
    };
  });
  const correct = results.filter((item) => item.correct).length;
  const score = Math.round((correct / results.length) * 100);
  const scoring = await scoreAttemptOnServer(state.activeSet.map((question) => question.id), state.answers);
  const attempt = {
    id: crypto.randomUUID(),
    date: new Date().toISOString(),
    score,
    correct,
    total: results.length,
    durationMs: Date.now() - state.startedAt,
    scoring,
    results
  };
  state.latestResult = attempt;
  state.attempts.push(attempt);
  saveLocal();
  trackEvent("practice_set_completed", {
    total: attempt.total,
    correct: attempt.correct,
    score: attempt.score,
    durationMs: attempt.durationMs
  });
  syncProgress();
  renderReview();
  renderStats();
  setView("reviewView");
}

function conceptStatsFromAttempts(attempts = state.attempts) {
  const stats = {};
  attempts.flatMap((attempt) => attempt.results || []).forEach((result) => {
    stats[result.concept] ||= { correct: 0, total: 0 };
    stats[result.concept].total += 1;
    if (result.correct) stats[result.concept].correct += 1;
  });
  return stats;
}

function renderStats() {
  els.attemptCount.textContent = state.attempts.length;
  const avg = state.attempts.length
    ? Math.round(state.attempts.reduce((sum, attempt) => sum + attempt.score, 0) / state.attempts.length)
    : 0;
  els.avgScore.textContent = `${avg}%`;
}

function weakestConcept(attempt) {
  const stats = {};
  attempt.results.forEach((result) => {
    stats[result.concept] ||= { correct: 0, total: 0 };
    stats[result.concept].total += 1;
    if (result.correct) stats[result.concept].correct += 1;
  });
  return Object.entries(stats)
    .map(([concept, value]) => ({ concept, ...value, rate: value.correct / value.total }))
    .sort((a, b) => a.rate - b.rate || b.total - a.total)[0];
}

function renderReview() {
  const attempt = state.latestResult || state.attempts.at(-1);
  if (!attempt) {
    els.scoreBig.textContent = "No attempt yet";
    els.scoreDetail.textContent = "";
    els.conceptBreakdown.innerHTML = "";
    els.focusConcept.textContent = "Complete a set to get recommendations";
    els.focusExplanation.textContent = "";
    els.similarQuestions.innerHTML = "";
    els.answerReview.innerHTML = "";
    return;
  }

  const totalRange = attempt.scoring?.totalScoreRange;
  const sectionLines = Object.entries(attempt.scoring?.sections || {})
    .map(([section, value]) => {
      const range = value.scoreRange ? `, score range ${value.scoreRange[0]}-${value.scoreRange[1]}` : "";
      return `${section}: ${value.raw}/${value.total} raw${range}`;
    });
  els.scoreBig.textContent = totalRange ? `${totalRange[0]}-${totalRange[1]}` : `${attempt.score}%`;
  els.scoreDetail.textContent = [
    `${attempt.correct} of ${attempt.total} correct in ${formatTime(attempt.durationMs)}.`,
    totalRange ? `Official paper-test SAT score range for Practice Test ${attempt.scoring.practiceTest}.` : "",
    ...sectionLines
  ].filter(Boolean).join(" ");

  const latestStats = conceptStatsFromAttempts([attempt]);
  els.conceptBreakdown.innerHTML = Object.entries(latestStats).map(([concept, value]) => {
    const rate = Math.round((value.correct / value.total) * 100);
    return `<div class="concept-row"><strong>${concept}</strong><div class="meter"><span style="width:${rate}%"></span></div><small>${value.correct}/${value.total} correct</small></div>`;
  }).join("");

  const focus = weakestConcept(attempt);
  if (focus) {
    els.focusConcept.textContent = `Focus next: ${focus.concept}`;
    const tutorial = attempt.results.find((result) => result.concept === focus.concept)?.tutorial || "Review the concept, then do two similar questions before moving on.";
    els.focusExplanation.textContent = tutorial;
    const similar = state.questions.filter((question) => question.concept === focus.concept && !attempt.results.some((result) => result.id === question.id));
    els.similarQuestions.innerHTML = (similar.length ? similar : state.questions.filter((question) => question.concept === focus.concept)).slice(0, 3).map((question) => (
      `<div class="similar-item"><strong>${question.skill}</strong><p>${question.prompt}</p><small>${question.tutorial}</small></div>`
    )).join("");
  }

  els.answerReview.innerHTML = attempt.results.map((result, index) => (
    `<article class="answer-card ${result.correct ? "correct" : "incorrect"}">
      <span class="status ${result.correct ? "correct" : "incorrect"}">${result.correct ? "Correct" : "Review"}</span>
      <strong>${index + 1}. ${result.concept}</strong>
      <p>${result.prompt}</p>
      <p><b>Your answer:</b> ${result.selected || "Blank"} &nbsp; <b>Correct:</b> ${result.answer}</p>
      <p><b>Logic:</b> ${result.logic}</p>
      <p><b>Explanation:</b> ${result.explanation}</p>
    </article>`
  )).join("");
}

function renderMastery() {
  const stats = conceptStatsFromAttempts();
  const entries = Object.entries(stats).sort((a, b) => (a[1].correct / a[1].total) - (b[1].correct / b[1].total));
  els.masteryList.innerHTML = entries.length ? entries.map(([concept, value]) => {
    const rate = Math.round((value.correct / value.total) * 100);
    return `<div class="concept-row"><strong>${concept}</strong><div class="meter"><span style="width:${rate}%"></span></div><small>${rate}% mastery across ${value.total} item${value.total === 1 ? "" : "s"}</small></div>`;
  }).join("") : "<p>No practice history yet.</p>";
}

function drawProgress() {
  renderMastery();
  const canvas = els.progressChart;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#fbfcfa";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "#d9ded6";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i += 1) {
    const y = 30 + i * 50;
    ctx.beginPath();
    ctx.moveTo(48, y);
    ctx.lineTo(canvas.width - 24, y);
    ctx.stroke();
  }
  ctx.fillStyle = "#657069";
  ctx.font = "14px sans-serif";
  ctx.fillText("100%", 8, 35);
  ctx.fillText("0%", 20, 235);

  if (!state.attempts.length) {
    ctx.fillStyle = "#17211b";
    ctx.font = "20px sans-serif";
    ctx.fillText("Complete a practice set to see your trend.", 70, 145);
    return;
  }

  const points = state.attempts.map((attempt, index) => {
    const x = 60 + index * ((canvas.width - 100) / Math.max(1, state.attempts.length - 1));
    const y = 230 - attempt.score * 2;
    return { x, y, score: attempt.score };
  });

  ctx.strokeStyle = "#176b5b";
  ctx.lineWidth = 4;
  ctx.beginPath();
  points.forEach((point, index) => index ? ctx.lineTo(point.x, point.y) : ctx.moveTo(point.x, point.y));
  ctx.stroke();

  points.forEach((point, index) => {
    ctx.fillStyle = "#176b5b";
    ctx.beginPath();
    ctx.arc(point.x, point.y, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#17211b";
    ctx.font = "13px sans-serif";
    ctx.fillText(`${point.score}%`, point.x - 12, point.y - 14);
    ctx.fillStyle = "#657069";
    ctx.fillText(`#${index + 1}`, point.x - 8, 260);
  });
}

async function syncProgress() {
  if (!isSignedIn()) return;
  const conceptStats = conceptStatsFromAttempts();
  try {
    await fetch("/api/progress", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ userId: userId(), attempts: state.attempts, conceptStats })
    });
  } catch {
    // Browser storage still keeps the student moving if the server cannot save.
  }
}

async function loadProgress() {
  loadLocalAttempts();
  if (!isSignedIn()) {
    state.attempts = [];
    state.latestResult = null;
    renderStats();
    renderReview();
    return;
  }
  try {
    const response = await fetch("/api/progress");
    if (response.status === 401) {
      state.user = null;
      localStorage.removeItem("eddyUser");
      renderAuthUser();
      state.attempts = [];
      state.latestResult = null;
      renderStats();
      renderReview();
      return;
    }
    const data = await response.json();
    if (data.progress?.attempts) {
      state.attempts = data.progress.attempts;
      localStorage.setItem(attemptsStorageKey(), JSON.stringify(state.attempts));
    } else if (state.attempts.length) {
      await syncProgress();
    }
  } catch {
    // Local attempts remain available if the server cannot be reached.
  }
  state.latestResult = state.attempts.at(-1) || null;
  renderStats();
  renderReview();
}

async function refreshAuthStatus() {
  try {
    const response = await fetch("/api/auth/openai-status");
    const data = await response.json();
    const signedIn = Boolean(state.user || data.signedIn);
    els.openAiLoginButton.classList.toggle("hidden", !signedIn || data.codexConnected);
    els.codexLogoutButton.classList.toggle("hidden", !signedIn || !data.codexConnected);
    els.openAiLoginButton.disabled = !signedIn;
    if (data.codexConnected) {
      els.llmStatus.textContent = "SAT AI Tutor connected";
      els.llmDescription.textContent = "Ask Eddy will try ChatGPT/Codex first, then fall back if needed.";
      els.authStatus.textContent = "SAT AI Tutor is connected.";
    } else if (!signedIn) {
      els.authStatus.textContent = "Sign in or create an Eddy account to unlock SAT AI Tutor setup.";
    } else if (data.chatModelAvailable) {
      els.llmStatus.textContent = "Server OpenAI ready";
      els.llmDescription.textContent = "Ask Eddy can use the server OpenAI API. SAT AI Tutor connection is optional.";
      els.authStatus.textContent = "Signed in. You can connect SAT AI Tutor, or use the configured server tutor.";
    } else {
      els.llmStatus.textContent = "Local tutor ready";
      els.llmDescription.textContent = "Connect SAT AI Tutor to let Ask Eddy try ChatGPT/Codex first.";
      els.authStatus.textContent = "Signed in. Connect SAT AI Tutor to enable LLM tutoring.";
    }
  } catch {
    els.authStatus.textContent = "Could not check OpenAI status. Student login still works locally.";
  }
}

function renderAuthUser() {
  const signedIn = Boolean(state.user);
  els.profileTitle.textContent = signedIn ? state.user.name || "Signed in" : "Ready to practice?";
  els.signedOutStep.classList.toggle("hidden", signedIn);
  els.signedInStep.classList.toggle("hidden", !signedIn);
  els.studentName.value = state.user?.name || els.studentName.value || "";
  els.studentEmail.value = state.user?.email || els.studentEmail.value || "";
  els.studentPassword.value = "";
  els.signedInName.textContent = state.user?.name || "Student";
  els.signedInEmail.textContent = state.user?.email || "";
  if (!signedIn) {
    els.llmStatus.textContent = "Locked until sign in";
    els.llmDescription.textContent = "Create or sign into an Eddy account to connect SAT AI Tutor.";
    els.openAiLoginButton.classList.add("hidden");
    els.codexLogoutButton.classList.add("hidden");
  }
  els.startTestButton.disabled = !signedIn;
  els.startTestButton.textContent = signedIn ? "Start set" : "Sign in to start";
  els.sendChatButton.disabled = !signedIn;
  els.chatInput.disabled = !signedIn;
  els.chatInput.placeholder = signedIn ? "Ask for a hint" : "Sign in to ask Eddy";
  els.quickPrompts.querySelectorAll("button").forEach((button) => {
    button.disabled = !signedIn;
  });
}

async function loadCurrentUser() {
  try {
    const response = await fetch("/api/auth/me");
    const data = await response.json();
    state.user = data.user || null;
    if (state.user) {
      localStorage.setItem("eddyUser", JSON.stringify(state.user));
    } else {
      localStorage.removeItem("eddyUser");
    }
    renderAuthUser();
    await loadProgress();
  } catch {
    renderAuthUser();
    loadLocalAttempts();
  }
}

async function submitAuth(mode) {
  const payload = {
    name: els.studentName.value.trim(),
    email: els.studentEmail.value.trim(),
    password: els.studentPassword.value
  };
  const endpoint = mode === "register" ? "/api/auth/register" : "/api/auth/login";
  els.authStatus.textContent = mode === "register" ? "Creating account..." : "Signing in...";
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) {
    els.authStatus.textContent = data.error || "Authentication failed.";
    return;
  }
  state.user = data.user;
  localStorage.setItem("eddyUser", JSON.stringify(state.user));
  trackEvent(mode === "register" ? "auth_registered" : "auth_logged_in");
  renderAuthUser();
  await loadProgress();
  await refreshAuthStatus();
  if (els.accountMenu) els.accountMenu.open = false;
}

async function sendChat() {
  if (!requireSignedIn("ask Eddy")) return;
  const text = els.chatInput.value.trim();
  if (!text) return;
  els.chatInput.value = "";
  addChatMessage("user", text);
  const question = currentQuestion();
  const thinking = addChatMessage("agent", "Thinking...");
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        userMessage: text,
        question,
        concept: question?.concept,
        selectedAnswer: state.answers[question?.id]
      })
    });
    if (response.status === 401) {
      thinking.textContent = "Please sign in to use Ask Eddy.";
      await loadCurrentUser();
      return;
    }
    const data = await response.json();
    els.tutorMode.textContent = data.mode === "codex" ? "Codex" : data.mode === "openai" ? "OpenAI" : "Local";
    thinking.innerHTML = renderChatMarkdown(data.reply);
    if (data.mode === "codex" && data.model) {
      els.authStatus.textContent = `Ask Eddy answered with ChatGPT/Codex (${data.model}).`;
    } else if (data.mode === "openai") {
      els.authStatus.textContent = "Ask Eddy answered with the server OpenAI API.";
    } else if (data.warning) {
      els.authStatus.textContent = "Ask Eddy used local fallback because the LLM call failed. Try reconnecting ChatGPT/Codex.";
    }
  } catch {
    thinking.textContent = "I could not reach the tutor service, but you can still review the explanation after submitting.";
  }
}

function bindEvents() {
  document.addEventListener("click", (event) => {
    if (!els.accountMenu?.open) return;
    if (els.accountMenu.contains(event.target)) return;
    els.accountMenu.open = false;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && els.accountMenu?.open) {
      els.accountMenu.open = false;
    }
  });

  els.loginButton.addEventListener("click", () => submitAuth("login"));
  els.registerButton.addEventListener("click", () => submitAuth("register"));
  els.logoutButton.addEventListener("click", async () => {
    els.authStatus.textContent = "Signing out and disconnecting SAT AI Tutor...";
    await fetch("/api/auth/logout", { method: "POST" });
    state.user = null;
    localStorage.removeItem("eddyUser");
    resetPracticeSession();
    trackEvent("auth_logged_out");
    await loadProgress();
    renderAuthUser();
    await refreshAuthStatus();
  });

  els.openAiLoginButton.addEventListener("click", async () => {
    els.authStatus.textContent = "Starting SAT AI Tutor login...";
    try {
      const response = await fetch("/api/auth/codex/start");
      const data = await response.json();
      if (!data.authUrl) throw new Error("Missing login URL");
      location.href = data.authUrl;
    } catch {
      els.authStatus.textContent = "Could not start SAT AI Tutor login. Local tutor fallback is still available.";
    }
  });

  els.codexLogoutButton.addEventListener("click", async () => {
    await fetch("/api/auth/codex/logout", { method: "POST" });
    els.tutorMode.textContent = "Local";
    await refreshAuthStatus();
  });

  $$(".nav-tab").forEach((tab) => tab.addEventListener("click", () => setView(tab.dataset.view)));
  els.sectionFilter.addEventListener("change", () => {
    const matchingSubject = SAT_BLUEPRINT.find((subject) => subject.section === els.sectionFilter.value);
    state.selectedSubject = matchingSubject?.id || "full";
    const bundle = activeSubject().bundles.find((item) => item.status === "available" && item.mode === els.sectionFilter.value)
      || activeSubject().bundles.find((item) => item.status === "available")
      || activeSubject().bundles[0];
    state.selectedBundle = bundle.id;
    localStorage.setItem("eddySelectedSubject", state.selectedSubject);
    localStorage.setItem("eddySelectedBundle", state.selectedBundle);
    renderLanding();
    renderBundleFilter();
  });
  els.bundleFilter.addEventListener("change", () => setBundle(els.bundleFilter.value));
  els.startTestButton.addEventListener("click", startSet);
  els.previousButton.addEventListener("click", () => {
    state.currentIndex = Math.max(0, state.currentIndex - 1);
    renderQuestion();
  });
  els.nextButton.addEventListener("click", () => {
    state.currentIndex = Math.min(state.activeSet.length - 1, state.currentIndex + 1);
    renderQuestion();
  });
  els.submitButton.addEventListener("click", scoreActiveSet);
  els.sendChatButton.addEventListener("click", sendChat);
  els.quickPrompts.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-prompt]");
    if (!button) return;
    els.chatInput.value = button.dataset.prompt;
    sendChat();
  });
  els.chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") sendChat();
  });
}

async function init() {
  const response = await fetch("/api/questions");
  const data = await response.json();
  state.questions = data.questions;
  await loadCurrentUser();
  bindEvents();
  await loadProgress();
  renderLanding();
  syncSelectorsFromSelection();
  setView("landingView");
  await refreshAuthStatus();
  if (new URLSearchParams(location.search).get("codex_auth") === "success") {
    history.replaceState({}, "", "/");
    await refreshAuthStatus();
  }
}

init();
