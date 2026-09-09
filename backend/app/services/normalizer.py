"""
Multilingual Query Normalization Service — Run 7.

Provides deterministic lightweight normalization and language classification
for procurement search queries and extracted tender requirements.

Prioritizes:
- English
- Hindi (Devanagari script)
- Hinglish (Roman Hindi)
- Mixed English + Hindi technical terms

Key Principle:
Technical identifiers (IS numbers, grades, dimensions, units, voltages)
MUST NOT be corrupted or removed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class NormalizationResult:
    """Dataclass holding normalized text and language classification metadata."""
    original_query: str
    normalized_query: str
    detected_language: str  # ENGLISH, HINDI, HINGLISH, MIXED, UNKNOWN


# Regular expressions for technical identifiers to preserve intact
TECHNICAL_PATTERNS: Final[list[re.Pattern[str]]] = [
    # BIS Standard numbers: e.g. IS 1786:2008, IS 7098 (Part 1):1988, IS 456:2000
    re.compile(r"\bIS\s*\d+(?:\s*\([^\)]+\))?(?::\d+)?\b", re.IGNORECASE),
    # Steel grades: Fe 415, Fe 415D, Fe 500, Fe 500D, Fe 550, Fe 550D, Fe 600
    re.compile(r"\bFe\s*\d+[AD]?\b", re.IGNORECASE),
    # Structural grades: E 250, E250, E 350, E350, Grade E250, Grade E350
    re.compile(r"\b(?:Grade\s*)?E\s*\d+[A-Z]?\b", re.IGNORECASE),
    # Cement grades: 33 grade, 43 grade, 53 grade, M10, M50, M100
    re.compile(r"\b(?:M\d+|\d+\s*grade)\b", re.IGNORECASE),
    # Voltages: 450/750 V, 450/750v, 1100 V, 1100v, 1100V
    re.compile(r"\b\d+(?:/\d+)?\s*V\b", re.IGNORECASE),
    # Dimensions & Units: 12 mm, 168.3 mm, 2540 mm, 200 Joules
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:mm|cm|m|inch|in|joules?)\b", re.IGNORECASE),
    # Structural designations: ISMB 300, ISMC 200
    re.compile(r"\bIS[A-Z]{2,4}\s*\d+\b", re.IGNORECASE),
]

# Devanagari unit transliterations to standardize to English symbols
DEVANAGARI_UNITS: Final[dict[str, str]] = {
    "मिमी": "mm",
    "मि.मी.": "mm",
    "सेमी": "cm",
    "मीटर": "m",
    "वोल्ट": "V",
    "वी": "V",
}

# Curated small terminology and alias map for the 15-standard BIS catalog
# Maps Hindi (Devanagari) & Hinglish (Roman Hindi) terms to English domain technical equivalents
TERMINOLOGY_MAP: Final[dict[str, str]] = {
    # Reinforcement Steel / TMT Bars (IS 1786)
    "सरिया": "reinforcement steel TMT rebar",
    "सरिये": "reinforcement steel TMT rebar",
    "sariya": "reinforcement steel TMT rebar",
    "sariye": "reinforcement steel TMT rebar",
    "sariyan": "reinforcement steel TMT rebar",
    "सड़िया": "reinforcement steel TMT rebar",

    # Concrete & RCC (IS 456, IS 10262)
    "कंक्रीट": "concrete",
    "आरसीसी": "RCC reinforced concrete",
    "rcc": "RCC reinforced concrete",

    # Cement (IS 269)
    "सीमेंट": "cement",
    "seement": "cement",
    "ciment": "cement",

    # Structural Steel (IS 2062, IS 800)
    "स्टील": "steel",
    "लोहा": "steel",
    "loha": "structural steel",

    # Bricks (IS 1077)
    "ईंट": "clay building brick",
    "ईंटों": "clay building bricks",
    "ईंटें": "clay building bricks",
    "eent": "clay building brick",
    "eentein": "clay building bricks",
    "eenton": "clay building bricks",
    "int": "clay building brick",

    # Electrical Cables & Wiring (IS 694, IS 7098, IS 1554)
    "केबल": "electrical cable",
    "kabel": "electrical cable",
    "वायरिंग": "electrical wiring",
    "वाइरिंग": "electrical wiring",
    "तार": "wire conductor",
    "taar": "wire conductor",
    "बिजली": "electrical power wiring",
    "bijli": "electrical power wiring",

    # Pipes & Water Supply (IS 1239, IS 4984, IS 3589)
    "पाइप": "pipe",
    "पानी": "potable water supply",
    "paani": "potable water supply",
    "pani": "potable water supply",
    "जल": "water supply",
    "पीने का पानी": "potable drinking water supply",
    "peene ka pani": "potable drinking water supply",
    "peene ke pani": "potable drinking water supply",

    # Safety Helmet (IS 2925)
    "सुरक्षा हेलमेट": "industrial safety helmet head protection",
    "हेलमेट": "safety helmet hard hat",
    "helmet": "safety helmet hard hat",

    # Safety Shoes / Footwear (IS 15298)
    "सुरक्षा जूते": "industrial safety footwear shoes",
    "जूते": "safety footwear shoes",
    "jootey": "safety footwear shoes",
    "juute": "safety footwear shoes",

    # Metals / Conductors
    "तांबा": "copper",
    "तांबे": "copper",
    "tamba": "copper",
    "एल्यूमीनियम": "aluminium",
    "eluminyam": "aluminium",

    # Miscellaneous technical / domain words
    "निर्माण": "construction",
    "nirmaan": "construction",
    "nirman": "construction",
    "चिनाई": "masonry wall",
    "chinai": "masonry wall",
    "अग्नि शामक": "fire extinguisher",
    "aag bujhane wala": "fire extinguisher",

    # Common Hinglish connectors / stop phrases
    "के लिए": "for",
    "ke liye": "for",
    "hetu": "for",
    "हेतु": "for",
    "का": "for",
    "की": "for",
    "के": "for",
}

# Key Hinglish indicators to assist in language detection
HINGLISH_INDICATOR_WORDS: Final[set[str]] = {
    "sariya", "sariye", "sariyan", "nirmaan", "nirman", "ke", "liye", "paani",
    "pani", "peene", "loha", "eent", "eentein", "eenton", "taar", "bijli",
    "jootey", "juute", "chinai", "hetu", "kabel", "tamba"
}


def detect_language(text: str) -> str:
    """
    Classifies input query language into one of:
    - HINDI (primarily Devanagari script)
    - HINGLISH (Roman Hindi script / transliterated phrases)
    - MIXED (combination of Devanagari/Hindi and English technical text)
    - ENGLISH (Standard English technical text)
    - UNKNOWN (Empty or unclassifiable)
    """
    cleaned = text.strip()
    if not cleaned:
        return "UNKNOWN"

    has_devanagari = bool(re.search(r"[\u0900-\u097F]", cleaned))
    has_latin = bool(re.search(r"[a-zA-Z]", cleaned))

    if has_devanagari and has_latin:
        return "MIXED"
    elif has_devanagari and not has_latin:
        return "HINDI"
    elif has_latin and not has_devanagari:
        tokens = [t.lower() for t in re.findall(r"\b[a-z]+\b", cleaned.lower())]
        matching_hinglish_words = [t for t in tokens if t in HINGLISH_INDICATOR_WORDS]
        if len(matching_hinglish_words) >= 1:
            return "HINGLISH"
        return "ENGLISH"

    return "UNKNOWN"


def _replace_term_safely(text: str, term: str, replacement: str) -> str:
    """Replaces a target term safely regardless of script type (ASCII vs Devanagari)."""
    if re.search(r"[\u0900-\u097F]", term):
        # Devanagari term replacement using literal substring replacement
        pattern = re.escape(term)
        return re.sub(pattern, replacement, text)
    else:
        # ASCII / Hinglish term replacement using standard word boundaries
        pattern = rf"(?i)\b{re.escape(term)}\b"
        return re.sub(pattern, replacement, text)


def normalize_query(query: str) -> NormalizationResult:
    """
    Performs lightweight query normalization:
    1. Preserves explicit technical identifiers (IS numbers, grades, dimensions, units, voltages).
    2. Maps Devanagari units (e.g. 'मिमी') to standard symbols ('mm').
    3. Normalizes Hindi and Hinglish terminology to English technical equivalents.
    4. Detects language metadata.
    5. Cleans extra whitespace while retaining technical meaning.

    Does NOT corrupt numbers, units, or standard designations.
    Does NOT call external translation APIs or LLMs.
    """
    original = query.strip()
    if not original:
        return NormalizationResult(
            original_query=query,
            normalized_query="",
            detected_language="UNKNOWN"
        )

    detected_lang = detect_language(original)
    working_text = original

    # 1. Protect technical identifiers with placeholders so normalizer won't touch them
    protected_placeholders: dict[str, str] = {}
    for idx, pattern in enumerate(TECHNICAL_PATTERNS):
        for match in pattern.finditer(working_text):
            matched_str = match.group(0)
            placeholder = f"__TECH_ID_{idx}_{len(protected_placeholders)}__"
            protected_placeholders[placeholder] = matched_str
            working_text = working_text.replace(matched_str, placeholder, 1)

    # 2. Replace Devanagari units with English standard unit symbols
    for dev_unit, eng_unit in DEVANAGARI_UNITS.items():
        working_text = _replace_term_safely(working_text, dev_unit, eng_unit)

    # 3. Replace multi-word terminology mappings first (longer phrases first)
    sorted_terms = sorted(TERMINOLOGY_MAP.keys(), key=len, reverse=True)
    for term in sorted_terms:
        replacement = TERMINOLOGY_MAP[term]
        working_text = _replace_term_safely(working_text, term, replacement)

    # 4. Restore protected technical identifiers exactly as originally specified
    for placeholder, original_id in protected_placeholders.items():
        working_text = working_text.replace(placeholder, original_id)

    # 5. Clean up redundant spaces
    normalized = re.sub(r"\s+", " ", working_text).strip()

    return NormalizationResult(
        original_query=original,
        normalized_query=normalized,
        detected_language=detected_lang
    )
