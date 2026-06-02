"use client";

import { useEffect, useMemo, useRef, useState } from "react";

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
      "Problem-Solving and Data Analysis",
      "Geometry and Trigonometry",
    ],
    bundles: [
      { id: "full-pt4", title: "Practice Test 4 Full Bank", source: "College Board Practice Test 4 PDF", status: "available", mode: "All", practiceTest: 4, size: 120 },
      { id: "full-pt5", title: "Practice Test 5 Full Bank", source: "College Board Practice Test 5 PDF", status: "available", mode: "All", practiceTest: 5, size: 120 },
      { id: "full-adaptive-1", title: "Adaptive Full SAT Bundle", source: "Coming when more tests are imported", status: "locked", mode: "All", size: 0 },
      { id: "full-review-1", title: "Weakness Review Bundle", source: "Generated from student history", status: "locked", mode: "All", size: 0 },
    ],
  },
  {
    id: "rw",
    label: "Reading and Writing",
    section: "Reading and Writing",
    minutes: 64,
    questions: "Two modules",
    description: "Short passages and single multiple-choice questions across four content domains.",
    objectives: ["Craft and Structure", "Information and Ideas", "Standard English Conventions", "Expression of Ideas"],
    bundles: [
      { id: "rw-pt4", title: "Practice Test 4 Reading/Writing", source: "College Board Practice Test 4 PDF", status: "available", mode: "Reading and Writing", practiceTest: 4, size: 66 },
      { id: "rw-pt5", title: "Practice Test 5 Reading/Writing", source: "College Board Practice Test 5 PDF", status: "available", mode: "Reading and Writing", practiceTest: 5, size: 66 },
      { id: "rw-domain-craft", title: "Craft and Structure Drill", source: "Coming from generated bank", status: "locked", mode: "Reading and Writing", size: 0 },
      { id: "rw-grammar", title: "Grammar and Expression Drill", source: "Coming from generated bank", status: "locked", mode: "Reading and Writing", size: 0 },
    ],
  },
  {
    id: "math",
    label: "Math",
    section: "Math",
    minutes: 70,
    questions: "Two modules",
    description: "Calculator-allowed SAT math practice across the official math domains.",
    objectives: ["Algebra", "Advanced Math", "Problem-Solving and Data Analysis", "Geometry and Trigonometry"],
    bundles: [
      { id: "math-pt4", title: "Practice Test 4 Math", source: "College Board Practice Test 4 PDF", status: "available", mode: "Math", practiceTest: 4, size: 54 },
      { id: "math-pt5", title: "Practice Test 5 Math", source: "College Board Practice Test 5 PDF", status: "available", mode: "Math", practiceTest: 5, size: 54 },
      { id: "math-algebra", title: "Algebra and Functions Drill", source: "Coming from generated bank", status: "locked", mode: "Math", size: 0 },
      { id: "math-data-geo", title: "Data, Geometry, and Trig Drill", source: "Coming from generated bank", status: "locked", mode: "Math", size: 0 },
    ],
  },
];

const VIEW_TITLES = {
  landingView: "SAT Practice",
  practiceView: "Practice Test",
  reviewView: "Review and Concepts",
  progressView: "Progress Tracker",
};

const TUTOR_PROMPTS = {
  practiceView: [
    { label: "Hint", icon: "?", tone: "hint", message: "Give me a hint.", prompt: "Start with 'Hint:' on the first line. Give one focused hint that points me in the right direction without revealing the answer." },
    { label: "Concept", icon: "i", tone: "concept", message: "Explain the key concept.", prompt: "Start with 'Concept:' on the first line. Explain the main concept needed for this question in clear SAT tutor language." },
    { label: "Eliminate", icon: "x", tone: "eliminate", message: "Help me eliminate choices.", prompt: "Start with 'Eliminate:' on the first line. Show how to eliminate the wrong choices using evidence or math from the question." },
    { label: "Answer", icon: "✓", tone: "answer", message: "Show the correct answer.", prompt: "Show the correct answer first at the top, then explain why it is correct." },
  ],
  reviewView: [
    { label: "Practice plan", icon: "↗", tone: "concept", message: "Create a practice plan.", prompt: "Create a short practice plan based on my latest SAT attempt." },
    { label: "Weakness plan", icon: "!", tone: "eliminate", message: "Analyze my weak areas.", prompt: "Analyze my weak areas and give me an improvement plan." },
    { label: "Next focus", icon: "→", tone: "hint", message: "Choose my next focus.", prompt: "What should I focus on next, and why?" },
    { label: "Score analysis", icon: "✓", tone: "answer", message: "Explain my score.", prompt: "Explain my score and concept breakdown in plain language." },
  ],
};

const CHAT_PLACEHOLDERS = {
  practiceView: "Ask Eddy to explain step-by-step...",
  reviewView: "Ask why your answer was wrong...",
  landingView: "Ask Eddy anything...",
  progressView: "Ask about your progress...",
};

function shuffle(items) {
  return [...items].sort(() => Math.random() - 0.5);
}

function formatTime(ms) {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function normalizeAnswer(value) {
  return String(value || "").trim().toLowerCase().replace(/^0+(?=\d)/, "").replace(/\s+/g, "").replace(/^\./, "0.");
}

function isCorrectAnswer(selected, answer) {
  return String(answer || "").split(";").map(normalizeAnswer).filter(Boolean).includes(normalizeAnswer(selected));
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
  return escapeHtml(text).replace(/\^(-?\d+)/g, "<sup>$1</sup>");
}

function renderInlineMarkdown(text) {
  return escapeHtml(text).replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>").replace(/\*([^*]+)\*/g, "<em>$1</em>");
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
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (bullet || numbered) {
      listItems.push((bullet || numbered)[1]);
      continue;
    }
    flushList();
    const answerLine = trimmed.match(/^Correct answer:\s*(.+)$/i);
    if (answerLine) {
      html.push(`<div class="chat-callout answer-callout"><span>Correct answer</span><strong>${renderInlineMarkdown(answerLine[1])}</strong></div>`);
      continue;
    }
    const actionLine = trimmed.match(/^(Hint|Concept|Eliminate):\s*(.+)$/i);
    if (actionLine) {
      const tone = actionLine[1].toLowerCase();
      html.push(`<div class="chat-callout ${tone}-callout"><span>${renderInlineMarkdown(actionLine[1])}</span><strong>${renderInlineMarkdown(actionLine[2])}</strong></div>`);
      continue;
    }
    const whyLine = trimmed.match(/^(Why|Why this is correct|Why the other choices are wrong):\s*(.*)$/i);
    if (whyLine) {
      html.push(`<p class="chat-heading">${renderInlineMarkdown(whyLine[1])}</p>`);
      if (whyLine[2]) html.push(`<p>${renderInlineMarkdown(whyLine[2])}</p>`);
      continue;
    }
    html.push(`<p>${renderInlineMarkdown(trimmed)}</p>`);
  }
  flushList();
  return html.join("");
}

function conceptStatsFromAttempts(attempts) {
  const stats = {};
  attempts.flatMap((attempt) => attempt.results || []).forEach((result) => {
    stats[result.concept] ||= { correct: 0, total: 0 };
    stats[result.concept].total += 1;
    if (result.correct) stats[result.concept].correct += 1;
  });
  return stats;
}

function weakestConcept(attempt) {
  if (!attempt?.results?.length) return null;
  const stats = conceptStatsFromAttempts([attempt]);
  return Object.entries(stats)
    .map(([concept, value]) => ({ concept, ...value, rate: value.correct / value.total }))
    .sort((a, b) => a.rate - b.rate || b.total - a.total)[0];
}

export default function EddyApp() {
  const [questions, setQuestions] = useState([]);
  const [user, setUser] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [latestResult, setLatestResult] = useState(null);
  const [currentView, setCurrentView] = useState("landingView");
  const [selectedSubject, setSelectedSubject] = useState("full");
  const [selectedBundle, setSelectedBundle] = useState("full-pt4");
  const [activeSet, setActiveSet] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [startedAt, setStartedAt] = useState(null);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [accountOpen, setAccountOpen] = useState(false);
  const [authStatus, setAuthStatus] = useState("Students sign in here; the tutor uses OpenAI from the server when configured.");
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });
  const [tutorConnection, setTutorConnection] = useState("locked");
  const [llmStatus, setLlmStatus] = useState("Locked until sign in");
  const [llmDescription, setLlmDescription] = useState("Create or sign into an Eddy account to connect AI model.");
  const [tutorModel, setTutorModel] = useState("Not connected");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const chatLogRef = useRef(null);
  const progressCanvasRef = useRef(null);

  const signedIn = Boolean(user);
  const activeSubject = useMemo(() => SAT_BLUEPRINT.find((subject) => subject.id === selectedSubject) || SAT_BLUEPRINT[0], [selectedSubject]);
  const activeBundle = useMemo(() => (
    activeSubject.bundles.find((bundle) => bundle.id === selectedBundle)
    || activeSubject.bundles.find((bundle) => bundle.status === "available")
    || activeSubject.bundles[0]
  ), [activeSubject, selectedBundle]);
  const currentQuestion = activeSet[currentIndex];
  const latestAttempt = latestResult || attempts.at(-1) || null;
  const avgScore = attempts.length ? Math.round(attempts.reduce((sum, attempt) => sum + attempt.score, 0) / attempts.length) : 0;

  const questionsForBundle = (bundle) => questions.filter((question) => {
    if ((bundle.mode || "All") !== "All" && question.section !== bundle.mode) return false;
    if (bundle.practiceTest && question.metadata?.practiceTest !== bundle.practiceTest) return false;
    return true;
  });

  const userId = () => user?.id || user?.email || "demo-user";
  const attemptsStorageKey = () => `eddyAttempts:${userId()}`;

  const trackEvent = (event, properties = {}) => {
    const payload = JSON.stringify({ event, properties });
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/api/events", new Blob([payload], { type: "application/json" }));
      return;
    }
    fetch("/api/events", { method: "POST", headers: { "content-type": "application/json" }, body: payload, keepalive: true }).catch(() => {});
  };

  const addChatMessage = (role, text) => {
    setChatMessages((messages) => [...messages, { id: crypto.randomUUID(), role, text }]);
  };

  const resetTutorChat = (viewId = currentView) => {
    setChatInput("");
    if (viewId === "practiceView") {
      setChatMessages([{ id: crypto.randomUUID(), role: "system", text: "Ready when you are. Use a quick action or ask anything about this question." }]);
    } else if (viewId === "reviewView") {
      setChatMessages([{ id: crypto.randomUUID(), role: "system", text: "Review mode is ready. Ask for a plan, a weakness check, next steps, or anything about your results." }]);
    } else {
      setChatMessages([]);
    }
  };

  const requireSignedIn = (action = "practice") => {
    if (signedIn) return true;
    setAuthStatus(`Sign in or create an Eddy account to ${action}.`);
    setAccountOpen(true);
    window.setTimeout(() => setAccountOpen(true), 0);
    return false;
  };

  const changeView = (viewId) => {
    if (["practiceView", "reviewView", "progressView"].includes(viewId) && !requireSignedIn("view this section")) {
      setCurrentView("landingView");
      return;
    }
    if (viewId !== currentView) resetTutorChat(viewId);
    setCurrentView(viewId);
  };

  const saveLocalAttempts = (nextAttempts) => {
    localStorage.setItem(`eddyAttempts:${user?.id || user?.email || "demo-user"}`, JSON.stringify(nextAttempts));
    if (user) localStorage.setItem("eddyUser", JSON.stringify(user));
  };

  const syncProgress = async (nextAttempts = attempts) => {
    if (!user) return;
    try {
      await fetch("/api/progress", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ userId: userId(), attempts: nextAttempts, conceptStats: conceptStatsFromAttempts(nextAttempts) }),
      });
    } catch {
      // Local attempts remain available if the server cannot save.
    }
  };

  const refreshAuthStatus = async (currentUser = user) => {
    try {
      const response = await fetch("/api/auth/openai-status");
      const data = await response.json();
      const isKnownSignedIn = Boolean(currentUser || data.signedIn);
      if (data.codexConnected) {
        setTutorConnection("connected");
        setLlmStatus("SAT AI Tutor connected");
        setLlmDescription("Ask Eddy will try ChatGPT/Codex first, then fall back if needed.");
        setTutorModel(data.tutorModel || "ChatGPT/Codex");
        setAuthStatus("SAT AI Tutor is connected.");
      } else if (!isKnownSignedIn) {
        setTutorConnection("locked");
        setLlmStatus("Locked until sign in");
        setLlmDescription("Create or sign into an Eddy account to connect AI model.");
        setTutorModel("Not connected");
        setAuthStatus("Sign in or create an Eddy account to unlock SAT AI Tutor setup.");
      } else if (data.chatModelAvailable) {
        setTutorConnection("server");
        setLlmStatus("Server OpenAI ready");
        setLlmDescription("Ask Eddy can use the server OpenAI API. Connect AI model to use ChatGPT/Codex when available.");
        setTutorModel(data.tutorModel || "Server OpenAI");
        setAuthStatus("Signed in. Server OpenAI is ready; connect AI model for ChatGPT/Codex.");
      } else {
        setTutorConnection("local");
        setLlmStatus("Local tutor ready");
        setLlmDescription("Connect AI model to let Ask Eddy try ChatGPT/Codex first.");
        setTutorModel(data.tutorModel || "Local fallback");
        setAuthStatus("Signed in. Connect AI model to enable LLM tutoring.");
      }
    } catch {
      setTutorConnection(currentUser ? "local" : "locked");
      setTutorModel(currentUser ? "Local fallback" : "Not connected");
      setAuthStatus("Could not check OpenAI status. Student login still works locally.");
    }
  };

  const loadProgress = async (currentUser) => {
    if (!currentUser) {
      setAttempts([]);
      setLatestResult(null);
      return;
    }
    let nextAttempts = [];
    try {
      const local = localStorage.getItem(`eddyAttempts:${currentUser.id || currentUser.email}`);
      nextAttempts = JSON.parse(local || "[]");
    } catch {
      nextAttempts = [];
    }
    try {
      const response = await fetch("/api/progress");
      if (response.status === 401) {
        setUser(null);
        localStorage.removeItem("eddyUser");
        setAttempts([]);
        setLatestResult(null);
        return;
      }
      const data = await response.json();
      if (data.progress?.attempts) nextAttempts = data.progress.attempts;
    } catch {
      // Keep local progress if the API is not reachable.
    }
    setAttempts(nextAttempts);
    setLatestResult(nextAttempts.at(-1) || null);
  };

  useEffect(() => {
    const init = async () => {
      const [questionsResponse, meResponse] = await Promise.all([fetch("/api/questions"), fetch("/api/auth/me")]);
      const questionsData = await questionsResponse.json();
      const meData = await meResponse.json();
      const currentUser = meData.user || null;
      setQuestions(questionsData.questions || []);
      setUser(currentUser);
      if (currentUser) {
        localStorage.setItem("eddyUser", JSON.stringify(currentUser));
        setAuthForm((form) => ({ ...form, name: currentUser.name || "", email: currentUser.email || "" }));
      } else {
        localStorage.removeItem("eddyUser");
      }
      setSelectedSubject(localStorage.getItem("eddySelectedSubject") || "full");
      setSelectedBundle(localStorage.getItem("eddySelectedBundle") || "full-pt4");
      await loadProgress(currentUser);
      await refreshAuthStatus(currentUser);
      if (new URLSearchParams(location.search).get("codex_auth") === "success") {
        history.replaceState({}, "", "/");
        await refreshAuthStatus(currentUser);
      }
    };
    init().catch(() => setAuthStatus("Could not load the app data. Please refresh."));
  }, []);

  useEffect(() => {
    if (!startedAt) return undefined;
    const id = setInterval(() => setElapsedMs(Date.now() - startedAt), 500);
    return () => clearInterval(id);
  }, [startedAt]);

  useEffect(() => {
    if (signedIn) return;
    setActiveSet([]);
    setCurrentIndex(0);
    setAnswers({});
    setStartedAt(null);
    setElapsedMs(0);
    if (["practiceView", "reviewView", "progressView"].includes(currentView)) setCurrentView("landingView");
  }, [signedIn]);

  useEffect(() => {
    chatLogRef.current?.scrollTo({ top: chatLogRef.current.scrollHeight });
  }, [chatMessages]);

  useEffect(() => {
    if (currentView !== "progressView") return;
    const canvas = progressCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#fbfcfa";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = "#d9ded6";
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
    if (!attempts.length) {
      ctx.fillStyle = "#17211b";
      ctx.font = "20px sans-serif";
      ctx.fillText("Complete a practice set to see your trend.", 70, 145);
      return;
    }
    const points = attempts.map((attempt, index) => ({
      x: 60 + index * ((canvas.width - 100) / Math.max(1, attempts.length - 1)),
      y: 230 - attempt.score * 2,
      score: attempt.score,
    }));
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
  }, [attempts, currentView]);

  const selectSubject = (subjectId) => {
    const nextSubject = SAT_BLUEPRINT.find((subject) => subject.id === subjectId) || SAT_BLUEPRINT[0];
    const availableBundle = nextSubject.bundles.find((bundle) => bundle.status === "available") || nextSubject.bundles[0];
    setSelectedSubject(nextSubject.id);
    setSelectedBundle(availableBundle.id);
    localStorage.setItem("eddySelectedSubject", nextSubject.id);
    localStorage.setItem("eddySelectedBundle", availableBundle.id);
  };

  const selectBundle = (bundleId) => {
    setSelectedBundle(bundleId);
    localStorage.setItem("eddySelectedBundle", bundleId);
  };

  const startSet = () => {
    if (!requireSignedIn("start a practice set")) return;
    const pool = questionsForBundle(activeBundle);
    const nextSet = shuffle(pool);
    setActiveSet(nextSet);
    setCurrentIndex(0);
    setAnswers({});
    setStartedAt(Date.now());
    setElapsedMs(0);
    trackEvent("practice_set_started", { bundleId: activeBundle.id, section: activeBundle.mode || "All", questionCount: nextSet.length });
    resetTutorChat("practiceView");
    setCurrentView("practiceView");
  };

  const submitAuth = async (mode) => {
    const endpoint = mode === "register" ? "/api/auth/register" : "/api/auth/login";
    setAuthStatus(mode === "register" ? "Creating account..." : "Signing in...");
    const response = await fetch(endpoint, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(authForm),
    });
    const data = await response.json();
    if (!response.ok) {
      setAuthStatus(data.error || "Authentication failed.");
      return;
    }
    setUser(data.user);
    localStorage.setItem("eddyUser", JSON.stringify(data.user));
    trackEvent(mode === "register" ? "auth_registered" : "auth_logged_in");
    await loadProgress(data.user);
    await refreshAuthStatus(data.user);
    setAccountOpen(false);
    setAuthForm((form) => ({ ...form, password: "" }));
  };

  const logout = async () => {
    setAuthStatus("Signing out and disconnecting SAT AI Tutor...");
    await fetch("/api/auth/logout", { method: "POST" });
    localStorage.removeItem("eddyUser");
    setUser(null);
    setAttempts([]);
    setLatestResult(null);
    setActiveSet([]);
    setCurrentView("landingView");
    setChatMessages([]);
    trackEvent("auth_logged_out");
    await refreshAuthStatus(null);
  };

  const connectAiModel = async () => {
    setAuthStatus("Starting AI model login...");
    try {
      const response = await fetch("/api/auth/codex/start");
      const data = await response.json();
      if (!data.authUrl) throw new Error("Missing login URL");
      location.href = data.authUrl;
    } catch {
      setAuthStatus("Could not start AI model login. Local tutor fallback is still available.");
    }
  };

  const scoreActiveSet = async () => {
    const results = activeSet.map((question) => {
      const selected = answers[question.id] || "";
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
        tutorial: question.tutorial,
      };
    });
    const correct = results.filter((item) => item.correct).length;
    const score = Math.round((correct / Math.max(1, results.length)) * 100);
    let scoring = null;
    try {
      const response = await fetch("/api/scoring/score", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ questionIds: activeSet.map((question) => question.id), answers }),
      });
      scoring = response.ok ? (await response.json()).scoring || null : null;
    } catch {
      scoring = null;
    }
    const attempt = {
      id: crypto.randomUUID(),
      date: new Date().toISOString(),
      score,
      correct,
      total: results.length,
      durationMs: elapsedMs,
      scoring,
      results,
    };
    const nextAttempts = [...attempts, attempt];
    setStartedAt(null);
    setLatestResult(attempt);
    setAttempts(nextAttempts);
    saveLocalAttempts(nextAttempts);
    await syncProgress(nextAttempts);
    trackEvent("practice_set_completed", { total: attempt.total, correct: attempt.correct, score: attempt.score, durationMs: attempt.durationMs });
    setCurrentView("reviewView");
    resetTutorChat("reviewView");
  };

  const latestAttemptSummary = () => {
    if (!latestAttempt) return null;
    const focus = weakestConcept(latestAttempt);
    const totalRange = latestAttempt.scoring?.totalScoreRange;
    return {
      score: latestAttempt.score,
      correct: latestAttempt.correct,
      total: latestAttempt.total,
      scoreRange: totalRange ? `${totalRange[0]}-${totalRange[1]}` : null,
      focusConcept: focus?.concept || null,
      focusCorrect: focus ? `${focus.correct}/${focus.total}` : null,
    };
  };

  const sendChat = async (prompt, displayText) => {
    if (!requireSignedIn("ask Eddy")) return;
    const text = String(prompt ?? chatInput).trim();
    if (!text) return;
    const visibleText = String(displayText ?? text).trim();
    setChatInput("");
    const thinkingId = crypto.randomUUID();
    setChatMessages((messages) => [...messages, { id: crypto.randomUUID(), role: "user", text: visibleText }, { id: thinkingId, role: "agent", text: "Thinking..." }]);
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          userMessage: text,
          question: currentView === "practiceView" ? currentQuestion : null,
          concept: currentView === "practiceView" ? currentQuestion?.concept : latestAttemptSummary()?.focusConcept,
          pageContext: currentView,
          latestAttempt: latestAttemptSummary(),
          selectedAnswer: answers[currentQuestion?.id],
        }),
      });
      if (response.status === 401) {
        setChatMessages((messages) => messages.map((message) => message.id === thinkingId ? { ...message, text: "Please sign in to use Ask Eddy." } : message));
        return;
      }
      const data = await response.json();
      setTutorConnection(data.mode === "codex" ? "connected" : data.mode === "openai" ? "server" : "local");
      setTutorModel(data.model || (data.mode === "codex" ? "ChatGPT/Codex" : data.mode === "openai" ? "Server OpenAI" : "Local fallback"));
      setChatMessages((messages) => messages.map((message) => message.id === thinkingId ? { ...message, text: data.reply } : message));
      if (data.mode === "codex" && data.model) setAuthStatus(`Ask Eddy answered with ChatGPT/Codex (${data.model}).`);
      else if (data.mode === "openai") setAuthStatus("Ask Eddy answered with the server OpenAI API.");
      else if (data.warning) setAuthStatus("Ask Eddy used local fallback because the LLM call failed. Try reconnecting ChatGPT/Codex.");
    } catch {
      setChatMessages((messages) => messages.map((message) => message.id === thinkingId ? { ...message, text: "I could not reach the tutor service, but you can still review the explanation after submitting." } : message));
    }
  };

  const sectionChanged = (mode) => {
    const matchingSubject = SAT_BLUEPRINT.find((subject) => subject.section === mode) || SAT_BLUEPRINT[0];
    const bundle = matchingSubject.bundles.find((item) => item.status === "available" && item.mode === mode)
      || matchingSubject.bundles.find((item) => item.status === "available")
      || matchingSubject.bundles[0];
    setSelectedSubject(matchingSubject.id);
    setSelectedBundle(bundle.id);
    localStorage.setItem("eddySelectedSubject", matchingSubject.id);
    localStorage.setItem("eddySelectedBundle", bundle.id);
  };

  return (
    <div className="app-shell">
      <Header
        user={user}
        accountOpen={accountOpen}
        setAccountOpen={setAccountOpen}
        authForm={authForm}
        setAuthForm={setAuthForm}
        authStatus={authStatus}
        submitAuth={submitAuth}
        logout={logout}
        attempts={attempts}
        avgScore={avgScore}
        currentView={currentView}
        changeView={changeView}
      />
      <main>
        <section className="topbar">
          <div>
            <p className="eyebrow">Digital SAT practice</p>
            <h2>{VIEW_TITLES[currentView]}</h2>
            <p className="hero-copy">Focused practice sets, instant concept review, and a tutor ready while you work.</p>
          </div>
          <div className="test-controls">
            <label className="select-label" htmlFor="sectionFilter">Section</label>
            <select id="sectionFilter" value={activeBundle.mode || activeSubject.section || "All"} onChange={(event) => sectionChanged(event.target.value)}>
              <option value="All">All</option>
              <option value="Reading and Writing">Reading and Writing</option>
              <option value="Math">Math</option>
            </select>
            <label className="select-label bundle-label" htmlFor="bundleFilter">Bundle</label>
            <select id="bundleFilter" value={selectedBundle} onChange={(event) => selectBundle(event.target.value)}>
              {activeSubject.bundles.map((bundle) => (
                <option key={bundle.id} value={bundle.id} disabled={bundle.status !== "available"}>{bundle.title}{bundle.status !== "available" ? " (soon)" : ""}</option>
              ))}
            </select>
            <button id="startTestButton" className="primary-button" type="button" disabled={!signedIn} onClick={startSet}>{signedIn ? "Start set" : "Sign in to start"}</button>
          </div>
        </section>

        {currentView === "landingView" && (
          <LandingView
            activeSubject={activeSubject}
            selectedBundle={selectedBundle}
            questionsForBundle={questionsForBundle}
            selectSubject={selectSubject}
            selectBundle={selectBundle}
          />
        )}

        {currentView === "practiceView" && (
          <section id="practiceView" className="view active">
            <div className="study-layout">
              <PracticeView
                activeSet={activeSet}
                currentIndex={currentIndex}
                setCurrentIndex={setCurrentIndex}
                currentQuestion={currentQuestion}
                answers={answers}
                setAnswers={setAnswers}
                elapsedMs={elapsedMs}
                submit={scoreActiveSet}
                resetTutor={() => resetTutorChat("practiceView")}
              />
              <TutorPanel
                viewId={currentView}
                signedIn={signedIn}
                tutorConnection={tutorConnection}
                llmStatus={llmStatus}
                llmDescription={llmDescription}
                tutorModel={tutorModel}
                connectAiModel={connectAiModel}
                chatMessages={chatMessages}
                chatLogRef={chatLogRef}
                chatInput={chatInput}
                setChatInput={setChatInput}
                sendChat={sendChat}
              />
            </div>
          </section>
        )}

        {currentView === "reviewView" && (
          <section id="reviewView" className="view active">
            <div className="study-layout">
              <ReviewView attempt={latestAttempt} questions={questions} />
              <TutorPanel
                viewId={currentView}
                signedIn={signedIn}
                tutorConnection={tutorConnection}
                llmStatus={llmStatus}
                llmDescription={llmDescription}
                tutorModel={tutorModel}
                connectAiModel={connectAiModel}
                chatMessages={chatMessages}
                chatLogRef={chatLogRef}
                chatInput={chatInput}
                setChatInput={setChatInput}
                sendChat={sendChat}
              />
            </div>
          </section>
        )}

        {currentView === "progressView" && (
          <section id="progressView" className="view active">
            <div className="progress-grid">
              <article className="score-panel">
                <p className="eyebrow">Trend</p>
                <canvas ref={progressCanvasRef} width="720" height="280" />
              </article>
              <article className="score-panel">
                <p className="eyebrow">Concept mastery</p>
                <MasteryList attempts={attempts} />
              </article>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

function Header({ user, accountOpen, setAccountOpen, authForm, setAuthForm, authStatus, submitAuth, logout, attempts, avgScore, currentView, changeView }) {
  useEffect(() => {
    const close = (event) => {
      if (!event.target.closest?.("#accountMenu")) setAccountOpen(false);
    };
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, [setAccountOpen]);

  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark"><img src="/assets/favicon.png" alt="Eddy SAT GOAT logo" /></div>
        <div><h1>Eddy SAT GOAT</h1><p>Practice with an AI tutor.</p></div>
      </div>
      <nav className="top-nav" aria-label="SAT app sections">
        {[
          ["landingView", "SAT Home"],
          ["practiceView", "Practice"],
          ["reviewView", "Review"],
          ["progressView", "Progress"],
        ].map(([viewId, label]) => (
          <button key={viewId} className={`nav-tab ${currentView === viewId ? "active" : ""}`} type="button" onClick={(event) => { event.stopPropagation(); changeView(viewId); }}>{label}</button>
        ))}
      </nav>
      <div className="header-stats"><span>{attempts.length}</span><small>Attempts</small><span>{avgScore}%</span><small>Average</small></div>
      <details className="account-menu" id="accountMenu" open={accountOpen}>
        <summary onClick={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setAccountOpen((open) => !open);
        }}>
          <div className="profile-avatar compact"><img src="/assets/favicon.png" alt="Eddy SAT GOAT logo" /></div>
          <span>Account</span>
        </summary>
        <section className="login-panel" id="loginPanel" onClick={(event) => event.stopPropagation()}>
          <div className="profile-top">
            <div className="profile-avatar"><img src="/assets/favicon.png" alt="Eddy SAT GOAT logo" /></div>
            <div><p className="eyebrow">Student Hub</p><h3>{user ? user.name || "Signed in" : "Ready to practice?"}</h3></div>
          </div>
          {!user ? (
            <div className="hub-step">
              <Field label="Student" value={authForm.name} placeholder="Name" autoComplete="name" onChange={(name) => setAuthForm((form) => ({ ...form, name }))} />
              <Field label="Account" type="email" value={authForm.email} placeholder="student@example.com" autoComplete="email" onChange={(email) => setAuthForm((form) => ({ ...form, email }))} />
              <Field label="Password" type="password" value={authForm.password} placeholder="At least 8 characters" autoComplete="current-password" onChange={(password) => setAuthForm((form) => ({ ...form, password }))} />
              <div className="auth-actions">
                <button className="primary-button" type="button" onClick={() => submitAuth("login")}>Sign in</button>
                <button className="secondary-button" type="button" onClick={() => submitAuth("register")}>Create</button>
              </div>
            </div>
          ) : (
            <div className="hub-step">
              <div className="student-card"><span>Signed in as</span><strong>{user.name || "Student"}</strong><small>{user.email}</small></div>
              <div className="profile-actions"><button className="secondary-button" type="button" onClick={logout}>Sign out</button></div>
            </div>
          )}
          <p className="fine-print">{authStatus}</p>
        </section>
      </details>
    </header>
  );
}

function Field({ label, type = "text", value, placeholder, autoComplete, onChange }) {
  return (
    <div className="field-stack">
      <label>{label}</label>
      <input type={type} value={value} placeholder={placeholder} autoComplete={autoComplete} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

function LandingView({ activeSubject, selectedBundle, questionsForBundle, selectSubject, selectBundle }) {
  return (
    <section id="landingView" className="view active">
      <div className="landing-grid">
        <article className="exam-overview">
          <p className="eyebrow">Choose your route</p>
          <h3>Digital SAT practice bundles</h3>
          <p>Pick the whole test or focus on a section. Each card lists the objectives College Board tests so practice and review stay tied to real SAT skills.</p>
          <figure className="demo-video-card">
            <img src="/assets/eddy-demo.gif" alt="Short demo showing SAT AI Tutor hints, review analysis, and progress tracking for SAT improvement." />
            <figcaption>Quick demo: AI tutor help, review analysis, and progress tracking.</figcaption>
          </figure>
          <div className="subject-cards">
            {SAT_BLUEPRINT.map((item) => (
              <button key={item.id} className={`subject-card ${item.id === activeSubject.id ? "active" : ""}`} type="button" onClick={() => selectSubject(item.id)}>
                <span>{item.questions}</span><strong>{item.label}</strong><small>{item.minutes} minutes</small>
                <ul>{item.objectives.slice(0, 4).map((objective) => <li key={objective}>{objective}</li>)}</ul>
              </button>
            ))}
          </div>
        </article>
        <article className="bundle-panel">
          <p className="eyebrow">Available bundles</p>
          <h3>{activeSubject.label}</h3>
          <p>{activeSubject.description}</p>
          <div className="bundle-cards">
            {activeSubject.bundles.map((bundle) => (
              <button key={bundle.id} className={`bundle-card ${bundle.id === selectedBundle ? "active" : ""} ${bundle.status !== "available" ? "locked" : ""}`} type="button" disabled={bundle.status !== "available"} onClick={() => selectBundle(bundle.id)}>
                <span>{bundle.status === "available" ? "Ready" : "Coming soon"}</span>
                <strong>{bundle.title}</strong>
                <small>{bundle.source}</small>
                <em>{bundle.status === "available" ? `${questionsForBundle(bundle).length} questions in this prototype set` : "Add more PDFs or generated questions to unlock"}</em>
              </button>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}

function PracticeView({ activeSet, currentIndex, setCurrentIndex, currentQuestion, answers, setAnswers, elapsedMs, submit, resetTutor }) {
  const choices = Array.isArray(currentQuestion?.choices) ? currentQuestion.choices : [];
  const selected = answers[currentQuestion?.id] || "";
  const setAnswer = (value) => setAnswers((next) => ({ ...next, [currentQuestion.id]: value }));
  const move = (index) => {
    setCurrentIndex(index);
    resetTutor();
  };
  return (
    <article className="question-area">
      <div className="question-meta">
        <span>{currentQuestion?.section || "Section"}</span>
        <span>{currentQuestion?.concept || "Concept"}</span>
        <span>{formatTime(elapsedMs)}</span>
      </div>
      <div className="question-content">
        <h3>{activeSet.length ? `Question ${currentIndex + 1} of ${activeSet.length}` : "Question 1"}</h3>
        <p className="question-prompt" dangerouslySetInnerHTML={{ __html: renderMathText(currentQuestion?.prompt || "") }} />
        <div className="choices">
          {currentQuestion?.metadata?.image && <figure className="question-figure"><img src={currentQuestion.metadata.image} alt={`Figure for ${currentQuestion.id}`} /></figure>}
          {currentQuestion && !choices.length && (
            <label className="free-response">
              <span>Your answer</span>
              <input type="text" inputMode="decimal" autoComplete="off" placeholder="Type a number, decimal, or fraction" value={selected} onChange={(event) => setAnswer(event.target.value)} />
            </label>
          )}
          {choices.map((choice) => {
            const key = choice.slice(0, 1);
            return (
              <button key={choice} className={`choice ${selected === key ? "selected" : ""}`} type="button" onClick={() => setAnswer(key)}>
                <span className="choice-key">{key}</span>
                <span dangerouslySetInnerHTML={{ __html: renderMathText(choice.slice(3)) }} />
              </button>
            );
          })}
        </div>
      </div>
      <div className="answer-actions">
        <button type="button" className="secondary-button" disabled={currentIndex === 0} onClick={() => move(Math.max(0, currentIndex - 1))}>Back</button>
        {currentIndex < activeSet.length - 1 ? (
          <button type="button" className="primary-button" onClick={() => move(Math.min(activeSet.length - 1, currentIndex + 1))}>Next</button>
        ) : (
          <button type="button" className="primary-button" onClick={submit}>Submit</button>
        )}
      </div>
    </article>
  );
}

function ReviewView({ attempt, questions }) {
  const focus = weakestConcept(attempt);
  const latestStats = attempt ? conceptStatsFromAttempts([attempt]) : {};
  const totalRange = attempt?.scoring?.totalScoreRange;
  const sectionLines = Object.entries(attempt?.scoring?.sections || {}).map(([section, value]) => {
    const range = value.scoreRange ? `, score range ${value.scoreRange[0]}-${value.scoreRange[1]}` : "";
    return `${section}: ${value.raw}/${value.total} raw${range}`;
  });
  const similar = focus
    ? questions.filter((question) => question.concept === focus.concept && !attempt.results.some((result) => result.id === question.id))
    : [];
  return (
    <div className="review-content">
      <div className="review-grid">
        <article className="score-panel">
          <p className="eyebrow">Latest result</p>
          <div className="score-big">{attempt ? (totalRange ? `${totalRange[0]}-${totalRange[1]}` : `${attempt.score}%`) : "No attempt yet"}</div>
          <p>{attempt ? [`${attempt.correct} of ${attempt.total} correct in ${formatTime(attempt.durationMs)}.`, totalRange ? `Official paper-test SAT score range for Practice Test ${attempt.scoring.practiceTest}.` : "", ...sectionLines].filter(Boolean).join(" ") : ""}</p>
          <div className="concept-list">
            {Object.entries(latestStats).map(([concept, value]) => {
              const rate = Math.round((value.correct / value.total) * 100);
              return <div key={concept} className="concept-row"><strong>{concept}</strong><div className="meter"><span style={{ width: `${rate}%` }} /></div><small>{value.correct}/{value.total} correct</small></div>;
            })}
          </div>
        </article>
        <article className="recommendation-panel">
          <p className="eyebrow">Practice plan</p>
          <h3>{focus ? `Focus next: ${focus.concept}` : "Complete a set to get recommendations"}</h3>
          <p>{focus ? attempt.results.find((result) => result.concept === focus.concept)?.tutorial || "Review the concept, then do two similar questions before moving on." : ""}</p>
          <div className="similar-list">
            {(similar.length ? similar : questions.filter((question) => question.concept === focus?.concept)).slice(0, 3).map((question) => (
              <div key={question.id} className="similar-item"><strong>{question.skill}</strong><p>{question.prompt}</p><small>{question.tutorial}</small></div>
            ))}
          </div>
        </article>
      </div>
      <div className="answer-review">
        {(attempt?.results || []).map((result, index) => (
          <article key={result.id} className={`answer-card ${result.correct ? "correct" : "incorrect"}`}>
            <span className={`status ${result.correct ? "correct" : "incorrect"}`}>{result.correct ? "Correct" : "Review"}</span>
            <strong>{index + 1}. {result.concept}</strong>
            <p>{result.prompt}</p>
            <p><b>Your answer:</b> {result.selected || "Blank"} &nbsp; <b>Correct:</b> {result.answer}</p>
            <p><b>Logic:</b> {result.logic}</p>
            <p><b>Explanation:</b> {result.explanation}</p>
          </article>
        ))}
      </div>
    </div>
  );
}

function MasteryList({ attempts }) {
  const stats = conceptStatsFromAttempts(attempts);
  const entries = Object.entries(stats).sort((a, b) => (a[1].correct / a[1].total) - (b[1].correct / b[1].total));
  if (!entries.length) return <div className="concept-list"><p>No practice history yet.</p></div>;
  return (
    <div className="concept-list">
      {entries.map(([concept, value]) => {
        const rate = Math.round((value.correct / value.total) * 100);
        return <div key={concept} className="concept-row"><strong>{concept}</strong><div className="meter"><span style={{ width: `${rate}%` }} /></div><small>{rate}% mastery across {value.total} item{value.total === 1 ? "" : "s"}</small></div>;
      })}
    </div>
  );
}

function TutorPanel({ viewId, signedIn, tutorConnection, llmStatus, llmDescription, tutorModel, connectAiModel, chatMessages, chatLogRef, chatInput, setChatInput, sendChat }) {
  const prompts = TUTOR_PROMPTS[viewId] || TUTOR_PROMPTS.practiceView;
  const modeLabel = { connected: "Connected", server: "OpenAI", local: "Local", locked: "Locked" }[tutorConnection] || "Local";
  const statusLabel = tutorConnection === "locked" ? modeLabel : `${modeLabel} · ${tutorModel}`;
  return (
    <aside className="tutor-panel">
      <div className="panel-heading">
        <p className="eyebrow">SAT AI Tutor</p>
        <div className="tutor-title-row">
          <h3>Ask Eddy</h3>
          <div className="tutor-status">
            <span className={`tutor-mode-pill tutor-mode-${tutorConnection}`} title={llmStatus}>{statusLabel}</span>
          </div>
        </div>
        <p className="tutor-status-copy">{llmDescription}</p>
      </div>
      <div className="tutor-connect-actions">
        {tutorConnection !== "connected" && tutorConnection !== "locked" && <button className="secondary-button tutor-connect-button" type="button" onClick={connectAiModel}>Connect AI model</button>}
      </div>
      <div ref={chatLogRef} className="chat-log" aria-live="polite">
        {chatMessages.map((message) => <ChatMessage key={message.id} message={message} />)}
      </div>
      <div className="quick-prompts" aria-label="Quick tutor prompts">
        {prompts.map((prompt) => (
          <button key={prompt.label} className={`quick-prompt-${prompt.tone}`} type="button" disabled={!signedIn} onClick={() => sendChat(prompt.prompt, prompt.message)}><span aria-hidden="true">{prompt.icon}</span>{prompt.label}</button>
        ))}
      </div>
      <div className="chat-input-row">
        <input type="text" placeholder={signedIn ? CHAT_PLACEHOLDERS[viewId] || "Ask Eddy anything..." : "Sign in to ask Eddy"} disabled={!signedIn} value={chatInput} onChange={(event) => setChatInput(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") sendChat(); }} />
        <button type="button" className="icon-button" aria-label="Send message" disabled={!signedIn} onClick={() => sendChat()}>&gt;</button>
      </div>
    </aside>
  );
}

function ChatMessage({ message }) {
  if (message.role === "system") {
    return <div className="message system"><span className="system-avatar">E</span><span dangerouslySetInnerHTML={{ __html: renderInlineMarkdown(message.text) }} /></div>;
  }
  if (message.role === "agent") {
    return <div className="message agent" dangerouslySetInnerHTML={{ __html: renderChatMarkdown(message.text) }} />;
  }
  return <div className="message user">{message.text}</div>;
}
