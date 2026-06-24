/**
 * ScamShield AI — frontend logic.
 * No build step, no framework — just fetch() calls to the FastAPI backend.
 *
 * The frontend is served by the same FastAPI app as the API (single
 * deployment, single URL on Render), so requests use a relative path
 * and automatically hit the right host - no URL to configure.
 */

const API_BASE_URL = "";

const messageInput = document.getElementById("message-input");
const charCount = document.getElementById("char-count");
const analyzeBtn = document.getElementById("analyze-btn");
const errorMessage = document.getElementById("error-message");

const resultSection = document.getElementById("result-section");
const gaugeFill = document.getElementById("gauge-fill");
const gaugeNeedle = document.getElementById("gauge-needle");
const verdictLabel = document.getElementById("verdict-label");
const riskScoreLabel = document.getElementById("risk-score-label");
const categoryTag = document.getElementById("category-tag");
const resultHeading = document.getElementById("result-heading");
const explanationText = document.getElementById("explanation-text");
const adviceText = document.getElementById("advice-text");
const checkAnotherBtn = document.getElementById("check-another-btn");

const statTotal = document.getElementById("stat-total");
const recentTicker = document.getElementById("recent-ticker");

const VERDICT_COPY = {
  safe: { label: "Looks safe", color: "#3DDC97", heading: "This message looks legitimate" },
  suspicious: { label: "Suspicious", color: "#FFB84D", heading: "Proceed with caution" },
  scam: { label: "Likely a scam", color: "#FF5A4E", heading: "This has the markings of a scam" },
};

const CATEGORY_DISPLAY = {
  phishing: "Phishing",
  romance_scam: "Romance scam",
  fake_job_offer: "Fake job offer",
  lottery_prize: "Lottery / prize scam",
  tech_support_scam: "Tech support scam",
  fake_refund_payment: "Fake refund / payment",
  impersonation: "Impersonation",
  investment_scam: "Investment scam",
  not_a_scam: "Not a scam",
  other: "Other",
};

// ---- Character counter ----
messageInput.addEventListener("input", () => {
  charCount.textContent = `${messageInput.value.length} / 4000`;
});

// ---- Analyze button ----
analyzeBtn.addEventListener("click", analyzeMessage);

async function analyzeMessage() {
  const text = messageInput.value.trim();
  hideError();

  if (!text) {
    showError("Paste a message first — we need something to check.");
    return;
  }

  setLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_text: text }),
    });

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed (${res.status})`);
    }

    const data = await res.json();
    renderResult(data);
    loadRecent();
    loadStats();
  } catch (err) {
    showError(
      err.message.includes("fetch")
        ? "Couldn't reach the ScamShield server. Make sure the backend is running."
        : err.message
    );
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  analyzeBtn.querySelector(".btn-text").textContent = isLoading
    ? "Scanning…"
    : "Run fraud detection scan";
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorMessage.hidden = false;
}

function hideError() {
  errorMessage.hidden = true;
}

// ---- Render result + animate gauge ----
function renderResult(data) {
  resultSection.hidden = false;

  const copy = VERDICT_COPY[data.verdict] || VERDICT_COPY.suspicious;

  verdictLabel.textContent = copy.label;
  verdictLabel.style.color = copy.color;
  riskScoreLabel.textContent = `Risk score: ${data.risk_score} / 100`;

  categoryTag.textContent = CATEGORY_DISPLAY[data.category] || "Other";
  resultHeading.textContent = copy.heading;
  explanationText.textContent = data.explanation;
  adviceText.textContent = data.advice;

  // Animate the gauge: semicircle arc length is ~283 (pi * r=90)
  const arcLength = 283;
  const fillRatio = data.risk_score / 100;
  gaugeFill.style.stroke = copy.color;
  // Force a reflow so the transition re-triggers on repeat checks
  gaugeFill.style.strokeDashoffset = arcLength;
  requestAnimationFrame(() => {
    gaugeFill.style.strokeDashoffset = String(arcLength * (1 - fillRatio));
  });

  // Needle: -90deg (risk 0) to +90deg (risk 100)
  const angle = (data.risk_score / 100) * 180 - 90;
  gaugeNeedle.style.transform = `rotate(${angle}deg)`;

  resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---- "Check another message" ----
checkAnotherBtn.addEventListener("click", () => {
  messageInput.value = "";
  charCount.textContent = "0 / 4000";
  resultSection.hidden = true;
  messageInput.focus();
  window.scrollTo({ top: 0, behavior: "smooth" });
});

// ---- Recent checks ticker ----
async function loadRecent() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/recent?limit=8`);
    if (!res.ok) return;
    const items = await res.json();

    if (!items.length) {
      recentTicker.innerHTML = '<p class="ticker-empty">No checks yet — be the first to run one above.</p>';
      return;
    }

    recentTicker.innerHTML = items
      .map(
        (item) => `
        <div class="ticker-item">
          <div class="ticker-category">${CATEGORY_DISPLAY[item.category] || "Other"}</div>
          <span class="ticker-verdict verdict-${item.verdict}">${item.verdict}</span>
        </div>`
      )
      .join("");
  } catch {
    // Silently ignore — the ticker is a nice-to-have, not critical.
  }
}

// ---- Header stat ----
async function loadStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stats`);
    if (!res.ok) return;
    const data = await res.json();
    statTotal.textContent = data.total_checks;
  } catch {
    statTotal.textContent = "—";
  }
}

// Initial load
loadRecent();
loadStats();
