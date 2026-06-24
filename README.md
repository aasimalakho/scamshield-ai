# 🛡️ ScamShield AI

**Paste it. Check it. Stay safe.**

ScamShield AI instantly analyzes any suspicious message — SMS, email,
WhatsApp, or social media DM — and tells you whether it's safe,
suspicious, or a likely scam, with a plain-language explanation and a
practical next step. No sign-up, no data stored about who you are —
just paste and check.

Built for **Youth Code × AI** — Track 03: *AI That Actually Helps People*.

---

## How it works

1. You paste a message into the box.
2. The backend runs it through a **local Machine Learning + NLP
   detection engine** — no external AI API, no API key, no cost:
   - A **TF-IDF + Logistic Regression** classifier (trained on a
     built-in dataset of scam vs. legitimate messages) estimates how
     scam-like the wording is.
   - A **rule-based NLP layer** (regex pattern matching) detects
     specific, explainable red flags — urgency language, requests for
     money/gift cards/crypto, suspicious links, requests for sensitive
     info, impersonation, generic greetings — and tags the scam category.
   - The two signals are blended into a final risk score and verdict.
3. The result — verdict, risk score, scam category, red flags, and
   advice — is saved to a small local database and shown to you with
   an animated risk gauge.
4. A "recently flagged patterns" feed shows anonymized verdicts from
   other checks (never the actual message text), so visitors can see
   ScamShield AI in action even before they run their own check.

---

## Tech stack

| Layer        | Tech                                  |
|--------------|----------------------------------------|
| Frontend     | HTML, CSS, vanilla JavaScript (no build step) |
| Backend      | Python, FastAPI                        |
| Database     | SQLite via SQLAlchemy                  |
| ML / NLP     | scikit-learn (TF-IDF + Logistic Regression) + regex-based rule engine |

> **Why no paid AI API?** ScamShield AI is built to be free to run
> forever, with zero API keys and zero per-request cost — important
> for a tool meant to actually help people, not gate it behind a
> subscription. The ML model trains itself automatically on first run
> from the built-in dataset (`training_data.py`) and caches itself to
> `scam_model.pkl`, so startup after the first run is instant.

> **Why no React?** A plain HTML/CSS/JS frontend gives the same
> one-page, responsive result with zero build tooling — just open
> `index.html` in a browser, no npm install or bundler required. It
> can be ported into a React component later without changing the
> backend at all, if a build step is ever wanted.

---

## Project structure

```
scamshield/
├── backend/
│   ├── main.py            # FastAPI app + /api/analyze, /api/recent, /api/stats
│   ├── classifier.py      # ML model + rule-based NLP red-flag detection engine
│   ├── training_data.py   # Built-in scam/safe example dataset for training
│   ├── models.py          # SQLAlchemy ScamCheck model
│   ├── database.py        # DB engine/session setup (SQLite)
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html        # One-page app
│   ├── styles.css         # Design system + responsive layout
│   └── app.js              # Fetch calls + gauge animation
├── .gitignore
└── README.md
```

---

## Deployment (single platform — Render)

The FastAPI backend serves the frontend directly (via a static-files
mount), so the whole app — API + UI — deploys as **one Render Web
Service** with one URL. No separate frontend host needed.

1. Push this repo to GitHub.
2. On [render.com](https://render.com) → **New → Web Service** → connect your repo.
3. Settings:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy. Render gives you a URL like `https://scamshield-ai.onrender.com` — opening it shows the app directly; `/api/...` on that same URL is the API.

That's it — no `API_BASE_URL` to configure, since the frontend calls the API via a relative path on the same origin.

> Free Render services sleep after inactivity and take ~30s to wake on the next request — fine for a hackathon demo, just open the link a minute before you need it.

---

## Setup — step by step

You'll need a way to run Python:
- Locally on your machine, or
- **Replit** / **GitHub Codespaces** (full Linux terminal in the browser), or
- **Google Colab** (run the backend in a cell + use `ngrok`/Colab's port forwarding to expose it), or
- Any cloud VM or hosting where you can run Python.

### 1. Get the code onto your environment
Upload the `scamshield/` folder, or if using Replit/Codespaces, create
a new Python project and add these files.

### 2. Install backend dependencies
```bash
cd scamshield/backend
pip install -r requirements.txt
```
No API key needed — the ML model trains itself on first run.

### 3. Run the app
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The first run will take a few extra seconds while the ML model trains
on the built-in dataset and caches itself to `scam_model.pkl`. Every
run after that is instant.

Open `http://localhost:8000` in a browser (or your Codespaces/Replit
forwarded URL) — you'll see the ScamShield AI app directly. The API
lives at the same address under `/api/...` (e.g. `/api/health`).

### 4. Try it
Paste a test message like:
> "Congratulations! You've won a $1,000 gift card. Click here within
> 24 hours to claim: bit.ly/claim-now"

You should see a red "Likely a scam" verdict with red flags explained.

---

## API reference

### `POST /api/analyze`
Request body:
```json
{ "message_text": "the message you want checked" }
```
Response:
```json
{
  "id": 1,
  "verdict": "scam",
  "risk_score": 92,
  "category": "lottery_prize",
  "explanation": "Creates urgency with a 24-hour deadline...",
  "advice": "Don't click the link. Delete the message..."
}
```

### `GET /api/recent?limit=8`
Returns the most recent checks (verdict + category only, no message
text, for privacy).

### `GET /api/stats`
Returns `{ "total_checks": N, "scams_caught": N }` for the header counter.

---

## Possible next steps

- Add a "report this scam" button that lets users flag false
  positives/negatives to improve detection accuracy.
- Add a browser extension or share-sheet integration so messages can
  be checked without copy-pasting.
- Support more languages and region-specific scam patterns.
