// NeuroRoute Popup — Query-only UI
const API = "http://localhost:3000";

let selectedTask = "ask";

// ── Server status check ───────────────────────────────────────────────────────
async function checkServer() {
  const pill = document.getElementById("status-pill");
  const text = document.getElementById("status-text");
  try {
    const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      pill.classList.add("online");
      text.textContent = "online";
      document.getElementById("send-btn").disabled = false;
    } else throw new Error();
  } catch {
    pill.classList.remove("online");
    text.textContent = "offline";
    document.getElementById("send-btn").disabled = true;
    document.getElementById("footer-text").textContent = "Start middleware: python server.py";
  }
}

// ── Task button selection ─────────────────────────────────────────────────────
document.querySelectorAll(".task-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".task-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    selectedTask = btn.dataset.task;
  });
});

// ── Label per task ────────────────────────────────────────────────────────────
const LABELS = {
  ask: "Answer", explain: "Explanation", summarize: "Summary",
  simplify: "Simplified", analyze: "Analysis", research: "Research"
};

// ── Send query ────────────────────────────────────────────────────────────────
document.getElementById("send-btn").addEventListener("click", sendQuery);

document.getElementById("query-input").addEventListener("keydown", e => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) sendQuery();
});

async function sendQuery() {
  const text = document.getElementById("query-input").value.trim();
  if (!text) return;

  const answerSection = document.getElementById("answer-section");
  const answerBox     = document.getElementById("answer-box");
  const labelEl       = document.getElementById("answer-label-text");
  const modelTag      = document.getElementById("model-tag");
  const sendBtn       = document.getElementById("send-btn");

  // Show loading state
  answerSection.classList.add("visible");
  labelEl.textContent = LABELS[selectedTask] || "Answer";
  modelTag.textContent = "";
  answerBox.innerHTML = `<div class="loading-dots"><span></span><span></span><span></span></div>`;
  sendBtn.disabled = true;
  sendBtn.textContent = "Running...";

  try {
    const res = await fetch(`${API}/neuroroute/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        selected_text: text,
        task: selectedTask,
        page_url: "",
        page_title: "NeuroRoute Popup",
      }),
    });

    const data = await res.json();

    if (data.error) {
      answerBox.textContent = "Error: " + data.error;
    } else {
      answerBox.textContent = data.answer || "No answer returned.";
      modelTag.textContent  = `${data.model_used || ""} · ${data.complexity || ""}`;
    }

  } catch (err) {
    answerBox.textContent = "Could not reach server. Make sure middleware is running.";
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "⬡  RUN QUERY";
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────
checkServer();
