# 🛡️ ScamShield AI

**Paste it. Check it. Stay safe.**

ScamShield AI instantly analyzes any suspicious message, SMS, email,
WhatsApp, or social media DM and tells you whether it's safe,
suspicious, or a likely scam, with a plain-language explanation and a
practical next step. No sign-up, no data stored about who you are,
just paste and check.

Built for **Youth Code × AI** - Track 03: *AI That Actually Helps People*.

---

## How it works

1. You paste a message into the box.
2. The backend runs it through a **local Machine Learning + NLP
   detection engine** no external AI API, no API key, no cost:
   - A **TF-IDF + Logistic Regression** classifier (trained on a
     built-in dataset of scam vs. legitimate messages) estimates how
     scam-like the wording is.
   - A **rule-based NLP layer** (regex pattern matching) detects
     specific, explainable red flags, urgency language, requests for
     money/gift cards/crypto, suspicious links, requests for sensitive
     info, impersonation, generic greetings, and tags the scam category.
   - The two signals are blended into a final risk score and verdict.
3. The result, verdict, risk score, scam category, red flags, and
   advice, is saved to a small local database and shown to you with
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
> forever, with zero API keys and zero per-request cost, important
> for a tool meant to actually help people, not gate it behind a
> subscription. The ML model trains itself automatically on first run
> from the built-in dataset (`training_data.py`) and caches itself to
> `scam_model.pkl`, so startup after the first run is instant.

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

---

## Deployment (single platform — backend serves the frontend)

The FastAPI backend serves the frontend directly (via a static-files
mount), so the whole app — API + UI — deploys as **one web service**
with one URL. No separate frontend host needed. This works the same
way on either platform below; pick whichever you prefer.

### Option A: Render

1. Push this repo to GitHub.
2. On [render.com](https://render.com) → **New → Web Service** → connect your repo.
3. Settings:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance type:** Free
4. Deploy. Render gives you a URL like `https://scamshield-ai.onrender.com`.

> Free Render services sleep after inactivity and take ~30s to wake on the next request.

### Option B: Railway

1. Push this repo to GitHub.
2. On [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo** → select your repo.
3. Settings:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy. Railway gives you a generated URL, or you can set a custom domain under the service's Settings tab.

In both cases: opening the URL shows the app directly; `/api/...` on that same URL is the API. No `API_BASE_URL` to configure, since the frontend calls the API via a relative path on the same origin.
