// NeuroRoute Content Script — Layer 1
// Shows ONLY the AI answer in the popup. All stats go to the dashboard.

(function () {
  "use strict";

  const NEUROROUTE_API = "http://localhost:3000";
  let popup = null;
  let currentSelection = "";
  let isLoading = false;

  // ─── Create popup DOM ────────────────────────────────────────────────────────
  function createPopup() {
    if (document.getElementById("neuroroute-popup")) return;

    popup = document.createElement("div");
    popup.id = "neuroroute-popup";
    popup.innerHTML = `
      <div class="nr-header">
        <div class="nr-logo">
          <span class="nr-leaf">⬡</span>
          <span class="nr-title">NeuroRoute</span>
          <span class="nr-badge">GREEN AI</span>
        </div>
        <button class="nr-close" id="nr-close">✕</button>
      </div>

      <!-- Action buttons panel -->
      <div class="nr-actions" id="nr-actions">
        <p class="nr-selected-preview" id="nr-preview"></p>
        <div class="nr-btn-grid">
          <button class="nr-btn" data-task="ask">💬 Ask</button>
          <button class="nr-btn" data-task="explain">🔍 Explain</button>
          <button class="nr-btn nr-btn-primary" data-task="summarize">📝 Summarize</button>
          <button class="nr-btn" data-task="simplify">✨ Simplify</button>
        </div>
      </div>

      <!-- Loading panel -->
      <div class="nr-loading" id="nr-loading" style="display:none;">
        <div class="nr-spinner"></div>
        <p class="nr-loading-text">Processing...</p>
        <p class="nr-loading-sub" id="nr-loading-sub">Routing to optimal model...</p>
      </div>

      <!-- Result panel — ANSWER ONLY, no stats -->
      <div class="nr-result" id="nr-result" style="display:none;">
        <div class="nr-answer-box">
          <p class="nr-answer-label" id="nr-answer-label">Answer</p>
          <p class="nr-answer-text" id="nr-answer-text"></p>
        </div>
        <div class="nr-result-footer">
          <button class="nr-feedback-btn" data-val="helpful" title="Helpful">👍</button>
          <button class="nr-feedback-btn" data-val="not_helpful" title="Not helpful">👎</button>
          <button class="nr-reset-btn" id="nr-reset">← Back</button>
        </div>
      </div>
    `;

    document.body.appendChild(popup);
    attachPopupEvents();
  }

  // ─── Events ──────────────────────────────────────────────────────────────────
  function attachPopupEvents() {
    document.getElementById("nr-close").addEventListener("click", hidePopup);
    document.getElementById("nr-reset").addEventListener("click", resetToActions);

    document.querySelectorAll(".nr-btn[data-task]").forEach((btn) => {
      btn.addEventListener("click", () => sendQuery(btn.getAttribute("data-task")));
    });

    document.querySelectorAll(".nr-feedback-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        sendFeedback(btn.getAttribute("data-val"));
        document.querySelectorAll(".nr-feedback-btn").forEach(b => b.classList.remove("nr-feedback-active"));
        btn.classList.add("nr-feedback-active");
      });
    });
  }

  // ─── Show / Hide ─────────────────────────────────────────────────────────────
  function showPopup(x, y, selectedText) {
    createPopup();
    currentSelection = selectedText;

    const preview = document.getElementById("nr-preview");
    preview.textContent = selectedText.length > 80
      ? selectedText.slice(0, 80) + "…"
      : selectedText;
    preview.style.color = "";

    resetToActions();

    // Smart positioning — keep inside viewport
    const popupWidth  = 380;
    const popupHeight = 220;
    let left = x + window.scrollX + 12;
    let top  = y + window.scrollY + 12;

    if (left + popupWidth  > window.scrollX + window.innerWidth)  left = x + window.scrollX - popupWidth - 12;
    if (top  + popupHeight > window.scrollY + window.innerHeight) top  = y + window.scrollY - popupHeight - 12;

    popup.style.left    = Math.max(8, left) + "px";
    popup.style.top     = Math.max(8, top)  + "px";
    popup.style.display = "flex";
    requestAnimationFrame(() => popup.classList.add("nr-visible"));
  }

  function hidePopup() {
    if (!popup) return;
    popup.classList.remove("nr-visible");
    setTimeout(() => { if (popup) popup.style.display = "none"; }, 200);
  }

  function resetToActions() {
    document.getElementById("nr-actions").style.display = "block";
    document.getElementById("nr-loading").style.display = "none";
    document.getElementById("nr-result").style.display  = "none";
  }

  // ─── Send query ───────────────────────────────────────────────────────────────
  async function sendQuery(task) {
    if (isLoading) return;
    isLoading = true;

    const taskLabels = { ask: "Answer", explain: "Explanation", summarize: "Summary", simplify: "Simplified" };

    document.getElementById("nr-actions").style.display = "none";
    document.getElementById("nr-loading").style.display = "flex";
    document.getElementById("nr-result").style.display  = "none";

    const messages = [
      "Analyzing query...",
      "Routing to optimal model...",
      "Generating answer...",
    ];
    let idx = 0;
    const sub = document.getElementById("nr-loading-sub");
    const ticker = setInterval(() => { sub.textContent = messages[++idx % messages.length]; }, 900);

    try {
      const res = await fetch(`${NEUROROUTE_API}/neuroroute/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          selected_text: currentSelection,
          task:          task,
          page_url:      window.location.href,
          page_title:    document.title,
          domain:        window.location.hostname,
          timestamp:     new Date().toISOString(),
        }),
      });

      const data = await res.json();
      clearInterval(ticker);

      document.getElementById("nr-answer-label").textContent = taskLabels[task] || "Answer";
      renderResult(data.answer || "No answer returned.");

    } catch (err) {
      clearInterval(ticker);
      renderError();
    } finally {
      isLoading = false;
    }
  }

  // ─── Render — answer only ─────────────────────────────────────────────────────
  function renderResult(answerText) {
    document.getElementById("nr-loading").style.display = "none";
    document.getElementById("nr-result").style.display  = "block";
    document.getElementById("nr-answer-text").textContent = answerText;
    document.querySelectorAll(".nr-feedback-btn").forEach(b => b.classList.remove("nr-feedback-active"));
  }

  function renderError() {
    document.getElementById("nr-loading").style.display = "none";
    document.getElementById("nr-actions").style.display = "block";
    const preview = document.getElementById("nr-preview");
    preview.textContent = "⚠ Could not connect to NeuroRoute server. Is it running on port 3000?";
    preview.style.color = "#ff6b6b";
  }

  // ─── Feedback ─────────────────────────────────────────────────────────────────
  async function sendFeedback(value) {
    try {
      await fetch(`${NEUROROUTE_API}/neuroroute/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: currentSelection, feedback: value }),
      });
    } catch (_) {}
  }

  // ─── Text selection detection ────────────────────────────────────────────────
  document.addEventListener("mouseup", (e) => {
    if (popup && popup.contains(e.target)) return;
    setTimeout(() => {
      const sel  = window.getSelection();
      const text = sel ? sel.toString().trim() : "";
      if (text.length > 5) {
        const rect = sel.getRangeAt(0).getBoundingClientRect();
        showPopup(rect.right, rect.bottom, text);
      } else {
        hidePopup();
      }
    }, 10);
  });

  document.addEventListener("mousedown", (e) => {
    if (popup && !popup.contains(e.target)) hidePopup();
  });

})();