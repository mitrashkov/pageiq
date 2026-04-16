from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class IndustryGuess:
    label: str
    confidence: float  # 0..1


_INDUSTRY_KEYWORDS: Dict[str, Iterable[str]] = {
    "ecommerce": ["shop", "cart", "checkout", "store", "product", "shipping", "returns", "myshopify"],
    "saas": ["api", "platform", "dashboard", "pricing", "integrations", "documentation", "cloud", "developer"],
    "agency": ["agency", "studio", "portfolio", "clients", "case studies", "branding", "design", "marketing"],
    "education": ["course", "curriculum", "university", "college", "student", "learn", "academy", "training"],
    "finance": ["bank", "insurance", "loan", "invest", "trading", "fintech", "mortgage", "credit"],
    "healthcare": ["clinic", "hospital", "patient", "medical", "health", "telehealth", "pharmacy", "doctor"],
    "news_media": ["news", "subscribe", "magazine", "editorial", "press", "journalism"],
    "nonprofit": ["donate", "donation", "nonprofit", "charity", "foundation", "volunteer"],
}


def guess_industry(*, title: Optional[str], description: Optional[str], keywords: Iterable[str], tech_stack: Iterable[str]) -> Optional[IndustryGuess]:
    text = " ".join([title or "", description or "", " ".join(keywords or []), " ".join(tech_stack or [])]).lower()
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None

    scores: Dict[str, int] = {k: 0 for k in _INDUSTRY_KEYWORDS.keys()}
    for industry, words in _INDUSTRY_KEYWORDS.items():
        for w in words:
            if w in text:
                scores[industry] += 1

    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] <= 0:
        return None

    # Simple confidence heuristic
    total = sum(scores.values()) or 1
    confidence = min(0.95, max(0.2, best[1] / total))
    return IndustryGuess(label=best[0], confidence=float(confidence))

