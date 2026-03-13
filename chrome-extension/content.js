// NeuroRoute Content Script

(function () {
  "use strict";

  const API = "http://localhost:3000";
  let popup = null;
  let selectedText = "";
  let isLoading = false;

  // ── Build popup once ───────────────────────────────────────────────────────
  function buildPopup() {
    if (document.getElementById("nr-popup")) return;

    popup = document.createElement("div");
    popup.id = "nr-popup";
    popup.innerHTML = `
      <div class="nr-head">
        <div class="nr-logo"><span class="nr-hex">⬡</span><span class="nr-name">NeuroRoute</span><span class="nr-tag">GREEN AI</span></div>
        <button id="nr-x">✕</button>
      </div>

      <!-- VIEW 1: action buttons -->
      <div id="nr-v-actions">
        <div class="nr-preview" id="nr-preview"></div>
        <div class="nr-grid">
          <button class="nr-btn" id="nr-ask-btn">💬 Ask</button>
          <button class="nr-btn" data-task="explain">🔍 Explain</button>
          <button class="nr-btn nr-green" data-task="summarize">📝 Summarize</button>
          <button class="nr-btn" data-task="simplify">✨ Simplify</button>
        </div>
      </div>

      <!-- VIEW 2: ask input (appears when Ask is clicked) -->
      <div id="nr-v-ask" style="display:none;">
        <div class="nr-ctx-label">Context — selected text:</div>
        <div class="nr-ctx-box" id="nr-ctx"></div>
        <div class="nr-q-label">Ask a question about this text:</div>
        <textarea id="nr-q-input" class="nr-q-input" placeholder="e.g. What does this mean? Why is this important?" rows="3"></textarea>
        <div class="nr-q-row">
          <button id="nr-q-back">← Back</button>
          <button id="nr-q-send">Send ↵</button>
        </div>
      </div>

      <!-- VIEW 3: loading -->
      <div id="nr-v-load" style="display:none;">
        <div class="nr-spin"></div>
        <p class="nr-load-txt">Processing...</p>
        <p class="nr-load-sub" id="nr-load-sub">Routing to optimal model...</p>
      </div>

      <!-- VIEW 4: result -->
      <div id="nr-v-result" style="display:none;">
        <div class="nr-ans-wrap">
          <div class="nr-ans-lbl" id="nr-ans-lbl">Answer</div>
          <div class="nr-ans-txt" id="nr-ans-txt"></div>
        </div>
        <div class="nr-foot">
          <button class="nr-fb" data-v="helpful">👍</button>
          <button class="nr-fb" data-v="not_helpful">👎</button>
          <button id="nr-back">← Back</button>
        </div>
      </div>
    `;

    document.body.appendChild(popup);
    bindEvents();
  }

  // ── Bind all events once ───────────────────────────────────────────────────
  function bindEvents() {
    // Close
    document.getElementById("nr-x").onclick = hidePopup;
    document.getElementById("nr-back").onclick = goActions;
    document.getElementById("nr-q-back").onclick = goActions;

    // Non-ask task buttons — send immediately
    popup.querySelectorAll(".nr-btn[data-task]").forEach(btn => {
      btn.onclick = () => send(btn.dataset.task, selectedText);
    });

    // Ask button — reveal input panel
    document.getElementById("nr-ask-btn").onclick = () => {
      document.getElementById("nr-ctx").textContent = selectedText.length > 200
        ? selectedText.slice(0, 200) + "…" : selectedText;
      document.getElementById("nr-q-input").value = "";
      show("nr-v-ask");
      setTimeout(() => document.getElementById("nr-q-input").focus(), 40);
    };

    // Send question
    document.getElementById("nr-q-send").onclick = submitAsk;

    // Textarea — Enter = send, Shift+Enter = newline, block all keys from page
    const ta = document.getElementById("nr-q-input");
    ta.addEventListener("keydown", e => {
      e.stopPropagation();
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submitAsk(); }
    });
    ta.addEventListener("keyup",    e => e.stopPropagation());
    ta.addEventListener("keypress", e => e.stopPropagation());

    // Feedback
    popup.querySelectorAll(".nr-fb").forEach(btn => {
      btn.onclick = () => {
        popup.querySelectorAll(".nr-fb").forEach(b => b.classList.remove("nr-fb-on"));
        btn.classList.add("nr-fb-on");
        sendFeedback(btn.dataset.v);
      };
    });

    // Block popup mouse events from escaping to page
    popup.addEventListener("mousedown", e => e.stopPropagation(), true);
    popup.addEventListener("mouseup",   e => e.stopPropagation(), true);
  }

  function submitAsk() {
    const q = document.getElementById("nr-q-input").value.trim();
    if (!q) {
      document.getElementById("nr-q-input").placeholder = "Please type a question first...";
      document.getElementById("nr-q-input").focus();
      return;
    }
    // Send user question WITH selected text locked as context
    send("ask", `${q}\n\nContext (selected text only):\n${selectedText}`);
  }

  // ── Panel switcher ─────────────────────────────────────────────────────────
  function show(id) {
    ["nr-v-actions","nr-v-ask","nr-v-load","nr-v-result"].forEach(v => {
      document.getElementById(v).style.display = "none";
    });
    document.getElementById(id).style.display = "block";
  }

  function goActions() { show("nr-v-actions"); }

  // ── Position + show popup ──────────────────────────────────────────────────
  function showPopup(x, y, text) {
    buildPopup();
    selectedText = text;

    document.getElementById("nr-preview").textContent =
      text.length > 120 ? text.slice(0, 120) + "…" : text;

    show("nr-v-actions");

    const W = 380, H = 240;
    let left = x + window.scrollX + 12;
    let top  = y + window.scrollY + 12;
    if (left + W > window.scrollX + window.innerWidth)  left = x + window.scrollX - W - 12;
    if (top  + H > window.scrollY + window.innerHeight) top  = y + window.scrollY - H - 12;

    popup.style.cssText += `left:${Math.max(8,left)}px;top:${Math.max(8,top)}px;display:flex;`;
    requestAnimationFrame(() => popup.classList.add("nr-on"));
  }

  function hidePopup() {
    if (!popup) return;
    popup.classList.remove("nr-on");
    setTimeout(() => { if (popup) popup.style.display = "none"; }, 180);
  }

  // ── API call ───────────────────────────────────────────────────────────────
  async function send(task, text) {
    if (isLoading) return;
    isLoading = true;

    const labels = { ask:"Answer", explain:"Explanation", summarize:"Summary", simplify:"Simplified" };
    show("nr-v-load");

    const msgs = ["Analyzing query...", "Routing to optimal model...", "Generating answer..."];
    let i = 0;
    const sub = document.getElementById("nr-load-sub");
    sub.textContent = msgs[0];
    const t = setInterval(() => { sub.textContent = msgs[++i % msgs.length]; }, 900);

    try {
      const res  = await fetch(`${API}/neuroroute/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          selected_text: text,
          task,
          page_url:   window.location.href,
          page_title: document.title,
          timestamp:  new Date().toISOString(),
        }),
      });
      const data = await res.json();
      clearInterval(t);
      document.getElementById("nr-ans-lbl").textContent = labels[task] || "Answer";
      document.getElementById("nr-ans-txt").textContent = data.answer || "No answer returned.";
      popup.querySelectorAll(".nr-fb").forEach(b => b.classList.remove("nr-fb-on"));
      show("nr-v-result");
    } catch {
      clearInterval(t);
      goActions();
      document.getElementById("nr-preview").style.color = "#ff6b6b";
      document.getElementById("nr-preview").textContent = "⚠ Server not reachable. Is middleware running on port 3000?";
    } finally {
      isLoading = false;
    }
  }

  async function sendFeedback(value) {
    try {
      await fetch(`${API}/neuroroute/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: selectedText, feedback: value }),
      });
    } catch (_) {}
  }

  // ── Text selection listener ────────────────────────────────────────────────
  document.addEventListener("mouseup", e => {
    if (popup && popup.contains(e.target)) return;
    setTimeout(() => {
      const sel  = window.getSelection();
      const text = sel ? sel.toString().trim() : "";
      if (text.length > 5) {
        const rect = sel.getRangeAt(0).getBoundingClientRect();
        showPopup(rect.right, rect.bottom, text);
      } else {
        const ta = document.getElementById("nr-q-input");
        if (ta && document.activeElement === ta) return; // don't close while typing
        hidePopup();
      }
    }, 10);
  });

  document.addEventListener("mousedown", e => {
    if (popup && !popup.contains(e.target)) hidePopup();
  });

})();