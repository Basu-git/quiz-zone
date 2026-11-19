/* Quiz Zone - one script for both pages. Scores are ALWAYS calculated by the backend. */
const API = "/api";   // same origin: FastAPI serves both the API and these pages

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function api(path, options) {
  const res = await fetch(API + path, options);
  if (!res.ok) {
    let msg = "Request failed (" + res.status + ")";
    try { const j = await res.json(); if (typeof j.detail === "string") msg = j.detail; } catch (e) { /* ignore */ }
    throw new Error(msg);
  }
  return res.json();
}

const ICONS = {
  "Python Programming": "🐍", "Artificial Intelligence": "🤖", "Database Management": "🗄️",
  "Computer Networks": "🌐", "General Knowledge": "💡",
};

/* ---------------- PAGE 1: HOME ---------------- */
async function initHome() {
  const grid = $("quizGrid");
  try {
    const quizzes = await api("/quizzes");
    $("totalQuizzes").textContent = quizzes.length;
    if (!quizzes.length) { grid.innerHTML = "<p class='section-sub'>No quizzes yet. Run seed.py to add some.</p>"; return; }
    grid.innerHTML = quizzes.map((q) => `
      <article class="quiz-card">
        <div class="quiz-icon" aria-hidden="true">${ICONS[q.category] || "📝"}</div>
        <h3>${esc(q.category)}</h3>
        <p class="desc">${esc(q.description)}</p>
        <div class="meta">
          <span class="tag">${q.total_questions} questions</span>
          <span class="tag">${q.duration_minutes} min</span>
          <span class="tag ${esc(q.difficulty)}">${esc(q.difficulty)}</span>
        </div>
        <a class="btn block" href="quiz.html?id=${q.id}">Start Quiz</a>
      </article>`).join("");
  } catch (err) {
    grid.innerHTML = "<div class='error-box'>Could not load quizzes: " + esc(err.message) + "</div>";
  }
}

/* ---------------- PAGE 2: QUIZ + RESULT ---------------- */
const state = { quiz: null, questions: [], answers: {}, index: 0, endAt: 0, startedAt: 0, timerId: null, submitting: false };

function show(view) {
  ["loadingView", "errorView", "introView", "quizView", "resultView"].forEach((v) => { $(v).hidden = v !== view; });
  window.scrollTo({ top: 0 });
}
function fail(msg) { $("errorText").textContent = msg; show("errorView"); }

async function initQuiz() {
  const id = parseInt(new URLSearchParams(location.search).get("id"), 10);
  if (!id) return fail("No quiz selected. Please choose a quiz from the home page.");
  try {
    const [quiz, questions] = await Promise.all([api("/quizzes/" + id), api("/quizzes/" + id + "/questions")]);
    if (!questions.length) return fail("This quiz has no questions yet.");
    state.quiz = quiz; state.questions = questions;
    $("introCategory").textContent = quiz.category;
    $("introTitle").textContent = quiz.title;
    $("introDesc").textContent = quiz.description || "";
    $("introCount").textContent = questions.length;
    $("introTime").textContent = quiz.duration_minutes;
    $("introDiff").textContent = quiz.difficulty;
    show("introView");
  } catch (err) { fail(err.message); }

  $("startBtn").addEventListener("click", startQuiz);
  $("prevBtn").addEventListener("click", () => go(-1));
  $("nextBtn").addEventListener("click", () => go(1));
  $("submitBtn").addEventListener("click", () => {
    const left = state.questions.length - Object.keys(state.answers).length;
    if (left > 0 && !confirm(left + " question(s) unanswered. Submit anyway?")) return;
    submitQuiz();
  });
  $("retakeBtn").addEventListener("click", () => location.reload()); // reload = fresh shuffle + intro
}

function startQuiz() {
  state.startedAt = Date.now();
  state.endAt = state.startedAt + state.quiz.duration_minutes * 60000;
  show("quizView");
  renderQuestion();
  tick();
  state.timerId = setInterval(tick, 500);
}

function tick() {
  const left = Math.max(0, Math.ceil((state.endAt - Date.now()) / 1000));
  const m = String(Math.floor(left / 60)).padStart(2, "0"), s = String(left % 60).padStart(2, "0");
  $("timer").textContent = m + ":" + s;
  $("timer").classList.toggle("low", left <= 30);
  if (left === 0) submitQuiz(true);   // auto-submit
}

function renderQuestion() {
  const q = state.questions[state.index], total = state.questions.length;
  $("qCount").textContent = "Question " + (state.index + 1) + " of " + total;
  $("progressBar").style.width = ((state.index + 1) / total * 100) + "%";
  $("qText").textContent = q.question_text;
  const opts = [["A", q.option_a], ["B", q.option_b], ["C", q.option_c], ["D", q.option_d]];
  $("options").innerHTML = opts.map(([l, t]) => `
    <button type="button" class="option ${state.answers[q.id] === l ? "selected" : ""}" role="radio"
      aria-checked="${state.answers[q.id] === l}" data-letter="${l}">
      <span class="letter">${l}</span><span>${esc(t)}</span>
    </button>`).join("");
  document.querySelectorAll(".option").forEach((b) =>
    b.addEventListener("click", () => { state.answers[q.id] = b.dataset.letter; renderQuestion(); }));
  $("prevBtn").disabled = state.index === 0;
  $("nextBtn").hidden = state.index === total - 1;
}

function go(step) {
  state.index = Math.min(Math.max(state.index + step, 0), state.questions.length - 1);
  renderQuestion();
}

async function submitQuiz(auto = false) {
  if (state.submitting) return;
  state.submitting = true;
  clearInterval(state.timerId);
  $("submitBtn").disabled = true;
  const taken = Math.min(Math.round((Date.now() - state.startedAt) / 1000), state.quiz.duration_minutes * 60);
  const payload = {
    answers: state.questions.map((q) => ({ question_id: q.id, selected: state.answers[q.id] || null })),
    time_taken: taken,
  };
  try {
    const result = await api("/quizzes/" + state.quiz.id + "/submit", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    renderResult(result, auto);
  } catch (err) {
    state.submitting = false; $("submitBtn").disabled = false;
    alert("Could not submit: " + err.message + "\nPlease try Submit again.");
  }
}

function renderResult(r, auto) {
  show("resultView");
  $("ring").style.setProperty("--p", r.percentage);
  $("ring").style.setProperty("--ring", r.passed ? "var(--good)" : "var(--bad)");
  $("ringText").textContent = Math.round(r.percentage) + "%";
  $("status").textContent = r.passed ? "Passed" : "Failed";
  $("status").className = "status " + (r.passed ? "pass" : "fail");
  $("resultTitle").textContent = r.quiz_title;
  const mm = Math.floor(r.time_taken / 60), ss = r.time_taken % 60;
  $("resultTime").textContent = (auto ? "Time is up. " : "") + "Time taken: " + mm + "m " + ss + "s · Pass mark " + r.pass_percentage + "%";
  $("rTotal").textContent = r.total_questions;
  $("rCorrect").textContent = r.correct_answers;
  $("rWrong").textContent = r.incorrect_answers;
  $("rPct").textContent = r.percentage + "%";
  $("review").innerHTML = r.review.map((it, i) => {
    const rows = [["A", it.option_a], ["B", it.option_b], ["C", it.option_c], ["D", it.option_d]].map(([l, t]) => {
      let cls = "", note = "";
      if (l === it.correct_answer) { cls = "correct"; note = "Correct answer"; }
      else if (l === it.selected) { cls = "wrong"; note = "Your answer"; }
      if (l === it.correct_answer && l === it.selected) note = "Your answer · Correct";
      return `<div class="ropt ${cls}">${l}. ${esc(t)}${note ? "<small>" + note + "</small>" : ""}</div>`;
    }).join("");
    return `<div class="review-item ${it.is_correct ? "ok" : ""}">
      <h4>${i + 1}. ${esc(it.question_text)}</h4>${rows}
      ${it.selected ? "" : "<div class='explain'>You did not answer this question.</div>"}
      <div class="explain"><b>Explanation:</b> ${esc(it.explanation)}</div></div>`;
  }).join("");
}

/* ---------------- Start ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "home") initHome();
  if (page === "quiz") initQuiz();
});
