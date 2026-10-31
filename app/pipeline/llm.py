"""LLM backends. Provider is chosen with the LLM_PROVIDER env var (decision D8).

- anthropic : needs ANTHROPIC_API_KEY, model from LLM_MODEL (default claude-haiku-5-5)
- openai    : needs OPENAI_API_KEY,   model from LLM_MODEL (default gpt-4o-mini)
- mock      : no key, no network — deterministic keyword labels for tests and demos.
              Mock output is NOT AI and must never be used for evaluation results.
"""
from __future__ import annotations

import json
import os
import re

try:  # load keys from a local .env file if present (never committed)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_MODELS = {"anthropic": "claude-haiku-5-5", "openai": "gpt-4o-mini", "mock": "mock-keywords"}


def provider() -> str:
    return os.getenv("LLM_PROVIDER", "mock").lower()


def model_name() -> str:
    return os.getenv("LLM_MODEL", DEFAULT_MODELS.get(provider(), "unknown"))


def complete(prompt: str) -> str:
    """Send one prompt, return the raw text response."""
    p = provider()
    if p == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        # anthropic SDK 2.x removed the `temperature` parameter, so it is not sent here.
        # Repeatability (D9) is checked by the eval's duplicate-consistency measure instead.
        # The model's thinking counts towards max_tokens; 4000 truncated a 20-review batch mid-JSON.
        msg = client.messages.create(
            model=model_name(), max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    if p == "openai":
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=model_name(), temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""
    if p == "mock":
        return _mock(prompt)
    raise ValueError(f"Unknown LLM_PROVIDER '{p}'. Use anthropic, openai or mock.")


# --- mock backend -----------------------------------------------------------
_MOCK_RULES = [
    ("Login & Access", r"log ?in|logon|log on|password|passcode|locked out|biometric|fingerprint|face id|pin\b"),
    ("Identity & Security Checks", r"selfie|photo|licen[cs]e|passport|verif|identity|security code|fraud"),
    ("App Updates & Stability", r"update|crash|freez|install|bug|glitch|not working|keeps closing"),
    ("Performance", r"slow|lag|takes ages|loading|timeout"),
    ("Payments & Transfers", r"payment|transfer|payee|standing order|direct debit|send money"),
    ("Cards", r"\bcard\b|google pay|apple pay"),
    ("Fees & Charges", r"\bfee|charge|interest|exchange rate"),
    ("Customer Support", r"customer service|support|branch|phone|call|chat"),
    ("Missing Feature", r"please add|wish|would be nice|no option|can't even|doesn't have"),
    ("Design & Usability", r"layout|design|confusing|navigate|hard to find|screen|clutter"),
]
_POS = r"great|good|easy|love|excellent|brilliant|happy|fantastic|best|perfect|helpful|quick"
_NEG = r"rubbish|terrible|awful|worst|can't|cannot|unable|useless|poor|disappoint|annoying|hate|not"


def _mock(prompt: str) -> str:
    block = prompt.split("REVIEWS (format \"id: text\"):", 1)[1].split("Return ONLY", 1)[0]
    out = []
    for line in block.strip().splitlines():
        if ":" not in line:
            continue
        rid, text = line.split(":", 1)
        t = text.lower()
        pos, neg = bool(re.search(_POS, t)), bool(re.search(_NEG, t))
        sentiment = "mixed" if pos and neg else "positive" if pos else "negative" if neg else "neutral"
        matches = [c for c, rx in _MOCK_RULES if re.search(rx, t)]
        category = matches[0] if matches else ("Praise" if sentiment == "positive" else "Other")
        out.append({
            "id": int(rid.strip()) if rid.strip().isdigit() else rid.strip(),
            "category": category, "other_categories": matches[1:4], "sentiment": sentiment,
            "theme": " ".join(text.split()[:6]).lower(),
            "problem": None if sentiment in ("positive", "neutral") else f"Customer reports an issue: {text.strip()[:80]}",
            "confidence": 0.5,
        })
    return json.dumps(out)
