from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, Optional


@dataclass(frozen=True)
class IndustryGuess:
    label: str
    confidence: float  # 0..1


_INDUSTRY_KEYWORDS: Dict[str, Iterable[str]] = {
    "ecommerce": ["shop", "cart", "checkout", "store", "product", "shipping", "returns", "myshopify", "sku", "inventory"],
    "saas": ["api", "platform", "dashboard", "pricing", "integrations", "documentation", "cloud", "developer", "software as a service", "subscription"],
    "agency": ["agency", "studio", "portfolio", "clients", "case studies", "branding", "design", "marketing", "consulting", "services"],
    "education": ["course", "curriculum", "university", "college", "student", "learn", "academy", "training", "school", "education"],
    "finance": ["bank", "insurance", "loan", "invest", "trading", "fintech", "mortgage", "credit", "crypto", "wallet", "payments"],
    "healthcare": ["clinic", "hospital", "patient", "medical", "health", "telehealth", "pharmacy", "doctor", "wellness", "care"],
    "news_media": ["news", "subscribe", "magazine", "editorial", "press", "journalism", "blog", "newspaper"],
    "nonprofit": ["donate", "donation", "nonprofit", "charity", "foundation", "volunteer", "impact", "cause"],
    "real_estate": ["real estate", "property", "listing", "agent", "broker", "homes", "apartments", "mortgage"],
    "legal": ["law", "legal", "attorney", "lawyer", "firm", "litigation", "counsel"],
    "travel_hospitality": ["travel", "hotel", "booking", "flight", "resort", "vacation", "tour", "hospitality"],
}


def guess_industry(*, title: Optional[str], description: Optional[str], keywords: Iterable[str], tech_stack: Iterable[str]) -> Optional[IndustryGuess]:
    title_desc = f"{title or ''} {description or ''}".lower()
    keywords_text = " ".join(keywords or []).lower()
    tech_text = " ".join(tech_stack or []).lower()
    
    all_text = f"{title_desc} {keywords_text} {tech_text}"
    if not all_text.strip():
        return None

    scores: Dict[str, float] = {k: 0 for k in _INDUSTRY_KEYWORDS.keys()}
    for industry, words in _INDUSTRY_KEYWORDS.items():
        for w in words:
            # Weighted scoring
            if w in title_desc:
                scores[industry] += 2.0  # Title/Desc is strong
            if w in keywords_text:
                scores[industry] += 1.0  # Keywords are good
            if w in tech_text:
                scores[industry] += 1.5  # Tech stack is very specific (e.g., Shopify = eCommerce)
                
    # Industry-specific tech stack boosts
    if "shopify" in tech_text or "woocommerce" in tech_text:
        scores["ecommerce"] += 5.0
    if "wordpress" in tech_text:
        scores["news_media"] += 1.0
    if any(t in tech_text for t in ["react", "next.js", "node.js"]):
        scores["saas"] += 1.0

    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] <= 0:
        return None

    # Simple confidence heuristic
    total = sum(scores.values()) or 1.0
    confidence = min(0.98, max(0.1, best[1] / total + 0.2))
    return IndustryGuess(label=best[0], confidence=float(confidence))

