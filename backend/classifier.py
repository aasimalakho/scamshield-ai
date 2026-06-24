"""
ScamShield AI - detection engine.

Combines two layers, fully offline and free (no external API calls):

1. MACHINE LEARNING LAYER
   A TF-IDF vectorizer + Logistic Regression classifier, trained on a
   small built-in dataset (see training_data.py), predicts the
   probability that a message is a scam based on patterns learned
   from real scam/safe wording.

2. RULE-BASED NLP LAYER
   A set of regex pattern-matchers detects specific, explainable red
   flags - urgency language, requests for money/gift cards/crypto,
   suspicious links, requests for sensitive info, generic greetings -
   and tags the scam category. This layer is what makes the
   explanation ("what we found") concrete instead of a black box.

The final risk score blends both layers, and the rule-based layer
always has the final say on category + explanation text, since that's
what makes the tool actually useful to a person reading the result.
"""

import re
import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from training_data import get_training_data

MODEL_PATH = Path(__file__).parent / "scam_model.pkl"


# ---------------------------------------------------------------------------
# Rule-based red-flag patterns (NLP via regex - lightweight & explainable)
# ---------------------------------------------------------------------------

RED_FLAG_PATTERNS = {
    "urgency": {
        "pattern": re.compile(
            r"\b(act now|urgent|immediately|within \d+ (hour|minute)s?|"
            r"expires? (today|soon|in)|final warning|right away|"
            r"as soon as possible|limited time|hurry|last chance|"
            r"before it'?s too late|do not (delay|wait))\b",
            re.IGNORECASE,
        ),
        "label": "creates urgency or time pressure",
    },
    "money_request": {
        "pattern": re.compile(
            r"\b(gift card|wire transfer|western union|bitcoin|crypto(currency)?|"
            r"prepaid card|send (money|cash|funds)|processing fee|registration fee|"
            r"customs fee|small fee|claim(ing)? fee|pay (a |the )?(fee|fine))\b",
            re.IGNORECASE,
        ),
        "label": "asks for money, gift cards, or cryptocurrency",
    },
    "sensitive_info_request": {
        "pattern": re.compile(
            r"\b(ssn|social security|pin\b|otp\b|password|card number|cvv|"
            r"bank (account|details)|date of birth|verify your (identity|information|account))\b",
            re.IGNORECASE,
        ),
        "label": "requests sensitive personal or financial information",
    },
    "suspicious_link": {
        "pattern": re.compile(
            r"(bit\.ly|tinyurl|click here|click this link|verify.*\.(com|net)|"
            r"[a-z0-9-]+-(update|verify|secure|confirm|claim)\.(com|net))",
            re.IGNORECASE,
        ),
        "label": "contains a suspicious or shortened link",
    },
    "too_good_to_be_true": {
        "pattern": re.compile(
            r"\b(you'?ve won|you have won|congratulations|guaranteed returns?|"
            r"double your money|no experience needed|\$\d+/?(week|day|hour)|"
            r"free (iphone|cruise|prize|gift))\b",
            re.IGNORECASE,
        ),
        "label": "makes an offer that's too good to be true",
    },
    "impersonation": {
        "pattern": re.compile(
            r"\b(this is the irs|this is your bank|fraud department|this is the police|"
            r"microsoft support|apple support|amazon support|your ceo|legal action|arrest warrant)\b",
            re.IGNORECASE,
        ),
        "label": "impersonates an authority, company, or known contact",
    },
    "generic_greeting": {
        "pattern": re.compile(
            r"\b(dear (customer|user|valued customer|sir/madam)|my (love|darling|dear))\b",
            re.IGNORECASE,
        ),
        "label": "uses a generic or overly affectionate greeting instead of your real name",
    },
}

CATEGORY_PATTERNS = {
    "phishing": re.compile(
        r"\b(verify your (identity|account|information)|account.*suspend|sign-?in|password|"
        r"confirm your (information|account))\b",
        re.IGNORECASE,
    ),
    "romance_scam": re.compile(
        r"\b(my (love|darling|dear)|deployed overseas|fallen for you|soldier|i love you)\b",
        re.IGNORECASE,
    ),
    "fake_job_offer": re.compile(
        r"\b(work.from.home|hiring immediately|no experience needed|\$\d+/?(week|hour|day)|"
        r"data entry|starter kit|resume has been selected)\b",
        re.IGNORECASE,
    ),
    "lottery_prize": re.compile(
        r"\b(you'?ve won|lottery|winner|claim your (prize|free)|free (cruise|iphone|gift))\b",
        re.IGNORECASE,
    ),
    "tech_support_scam": re.compile(
        r"\b(virus|microsoft support|technician|infected|certified technician|remove (it|the virus))\b",
        re.IGNORECASE,
    ),
    "fake_refund_payment": re.compile(
        r"\b(refund|jazzcash|paypal|sent.*by mistake|return (it|the amount))\b",
        re.IGNORECASE,
    ),
    "impersonation": re.compile(
        r"\b(this is the irs|this is your bank|this is the police|your ceo|fraud department|arrest warrant)\b",
        re.IGNORECASE,
    ),
    "investment_scam": re.compile(
        r"\b(guaranteed returns?|trading (bot|group)|double your money|invest now|crypto trading)\b",
        re.IGNORECASE,
    ),
}


def _train_and_save_model():
    """Train the TF-IDF + Logistic Regression pipeline and cache it to disk."""
    texts, labels = get_training_data()

    pipeline = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, stop_words="english")),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    pipeline.fit(texts, labels)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    return pipeline


def load_model():
    """Load the cached model, training it fresh if no cache exists yet."""
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as f:
            return pickle.load(f)
    return _train_and_save_model()


_MODEL = load_model()


def detect_red_flags(text: str):
    """Return a list of (flag_key, label) for every red-flag pattern matched."""
    found = []
    for key, info in RED_FLAG_PATTERNS.items():
        if info["pattern"].search(text):
            found.append((key, info["label"]))
    return found


def detect_category(text: str, is_scam: bool) -> str:
    """Pick the most likely scam category based on keyword pattern matches."""
    if not is_scam:
        return "not_a_scam"

    best_category = "other"
    best_matches = 0
    for category, pattern in CATEGORY_PATTERNS.items():
        matches = len(pattern.findall(text))
        if matches > best_matches:
            best_matches = matches
            best_category = category

    return best_category


def build_explanation(red_flags, ml_probability: float) -> str:
    """Turn the list of matched red flags into a short, readable sentence."""
    if not red_flags:
        if ml_probability < 0.3:
            return "No common scam red flags were detected - the wording and tone look like a normal, legitimate message."
        return "No specific red-flag phrases were found, but the overall tone and structure of the message is unusual enough to warrant a closer look."

    flag_labels = [label for _, label in red_flags[:3]]
    if len(flag_labels) == 1:
        return f"This message {flag_labels[0]}."
    if len(flag_labels) == 2:
        return f"This message {flag_labels[0]} and {flag_labels[1]}."
    return f"This message {flag_labels[0]}, {flag_labels[1]}, and {flag_labels[2]}."


def build_advice(verdict: str, category: str) -> str:
    """Return practical next-step advice tailored to the verdict and category."""
    if verdict == "safe":
        return "This looks fine, but it's always smart to verify directly with the sender if anything feels even slightly off."

    advice_map = {
        "phishing": "Don't click the link or enter any details. Go directly to the official website or app instead, and verify there.",
        "romance_scam": "Never send money, gift cards, or crypto to someone you haven't met in person - this is a very common pattern in romance scams.",
        "fake_job_offer": "Never pay a fee to get a job, and never share your bank or SSN before verifying the company is real through its official website.",
        "lottery_prize": "Real prizes never require you to pay a fee to claim them. Don't click the link or share any payment information.",
        "tech_support_scam": "Don't call the number or download anything. Close the message and run a scan using your device's built-in security tool if you're worried.",
        "fake_refund_payment": "Don't send anything back. Contact your bank or the official payment provider directly through their app to check your real balance.",
        "impersonation": "Hang up or ignore the message. Real government agencies and banks never ask for gift cards or OTPs over text or call.",
        "investment_scam": "Guaranteed high returns are a major red flag - no legitimate investment can promise this. Don't send funds.",
    }
    return advice_map.get(
        category,
        "When in doubt, don't click links or share personal info - verify through an official channel first.",
    )


def analyze_message(text: str):
    """
    Run the full detection pipeline on a message and return a dict with:
    verdict, risk_score, category, explanation, advice.
    """
    # --- ML layer: probability the message is a scam ---
    ml_probability = float(_MODEL.predict_proba([text])[0][1])

    # --- Rule-based layer: explainable red flags ---
    red_flags = detect_red_flags(text)

    # Blend: each red flag nudges the risk score up, anchored on the ML probability.
    rule_boost = min(len(red_flags) * 12, 48)
    risk_score = round(ml_probability * 100 * 0.65 + rule_boost * 0.35 + (rule_boost if ml_probability > 0.5 else 0) * 0)
    risk_score = max(0, min(100, risk_score + (10 if red_flags and ml_probability > 0.4 else 0)))

    if risk_score >= 60:
        verdict = "scam"
    elif risk_score >= 32:
        verdict = "suspicious"
    else:
        verdict = "safe"

    category = detect_category(text, is_scam=(verdict != "safe"))
    explanation = build_explanation(red_flags, ml_probability)
    advice = build_advice(verdict, category)

    return {
        "verdict": verdict,
        "risk_score": int(risk_score),
        "category": category,
        "explanation": explanation,
        "advice": advice,
    }
