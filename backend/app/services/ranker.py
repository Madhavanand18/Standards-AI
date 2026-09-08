import re
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

STOP_WORDS = {
    "for", "and", "the", "in", "of", "with", "to", "a", "an", "is", "by", "or", "as",
    "at", "from", "on", "into", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "can", "will", "just", "should", "now", "etc", "use", "used", "using",
    "item", "items", "supply", "requirement", "requirements", "specification", "specifications"
}

def tokenize(text: str) -> list[str]:
    """
    Extracts normalized tokens from text while preserving technical designations.
    """
    if not text:
        return []
    # Replace punctuation other than alphanumeric, hyphens, slashes
    cleaned = re.sub(r"[^\w\s\-/]", " ", text.lower())
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

def compute_metadata_relevance(query: str, standard: dict[str, Any]) -> float:
    """
    Calculates a normalized metadata relevance score in [0.0, 1.0] by evaluating
    the query against authentic BIS metadata: title, keywords, category, scope,
    and standard number.
    
    Semantic retrieval remains the primary signal; this score acts as a precision
    booster for domain attributes.
    """
    q_tokens = set(tokenize(query))
    if not q_tokens:
        return 0.0

    q_lower = query.lower()
    score = 0.0

    # 1. Standard Number Exact / Code Match (e.g., '1786', '2062', 'IS 1786')
    std_num = standard.get("standard_number", "").lower()
    std_digits = re.findall(r"\d+", std_num)
    for digit_group in std_digits:
        if len(digit_group) >= 3 and digit_group in q_lower:
            score += 0.40
            break

    # 2. Keywords Match (High-precision domain tags curated from official BIS catalog)
    keywords = standard.get("keywords") or []
    if isinstance(keywords, list):
        kw_matched_points = 0.0
        for kw in keywords:
            kw_clean = str(kw).lower().strip()
            if not kw_clean:
                continue
            # Full phrase match in query (e.g., "fe 500", "tmt bars", "concrete reinforcement")
            if kw_clean in q_lower:
                kw_matched_points += 2.0
            else:
                # Token overlap with keyword
                kw_tokens = set(tokenize(kw_clean))
                overlap = len(q_tokens.intersection(kw_tokens))
                if overlap > 0:
                    kw_matched_points += overlap * 0.5
        score += min(0.40, kw_matched_points * 0.10)

    # 3. Title Token & Phrase Overlap
    title = str(standard.get("title") or "").lower()
    title_tokens = set(tokenize(title))
    if title_tokens:
        title_overlap = len(q_tokens.intersection(title_tokens))
        title_ratio = title_overlap / len(q_tokens)
        score += min(0.30, title_ratio * 0.30)

    # 4. Category Overlap
    category = str(standard.get("category") or "").lower()
    cat_tokens = set(tokenize(category))
    if cat_tokens:
        cat_overlap = len(q_tokens.intersection(cat_tokens))
        if cat_overlap > 0:
            score += min(0.15, (cat_overlap / len(q_tokens)) * 0.20)

    # 5. Scope Technical Term Overlap
    scope = str(standard.get("scope") or "").lower()
    scope_tokens = set(tokenize(scope))
    if scope_tokens:
        scope_overlap = len(q_tokens.intersection(scope_tokens))
        scope_ratio = scope_overlap / len(q_tokens)
        score += min(0.15, scope_ratio * 0.15)

    return max(0.0, min(1.0, score))


def get_relevance_label(score: float) -> str:
    """
    Categorizes the composite similarity score into standard relevance tiers:
    - High: score >= 0.60
    - Medium: 0.40 <= score < 0.60
    - Low: score < 0.40
    """
    if score >= 0.60:
        return "High"
    elif score >= 0.40:
        return "Medium"
    else:
        return "Low"


def generate_explanation(query: str, standard: dict[str, Any]) -> str:
    """
    Generates a concise, factual 1-2 sentence explanation justifying why the
    standard was recommended for the user query, grounded strictly in stored
    BIS title, scope, category, and keywords without fabricating regulatory claims.
    """
    q_tokens = set(tokenize(query))
    q_lower = query.lower()

    # 1. Identify matched domain keywords
    matched_kws = []
    keywords = standard.get("keywords") or []
    for kw in keywords:
        kw_clean = str(kw).strip()
        if not kw_clean:
            continue
        if kw_clean.lower() in q_lower:
            matched_kws.append(kw_clean)
        else:
            kw_tokens = set(tokenize(kw_clean))
            if kw_tokens and kw_tokens.issubset(q_tokens):
                matched_kws.append(kw_clean)

    # 2. Extract most relevant scope clause
    scope = standard.get("scope") or ""
    sentences = [s.strip() for s in re.split(r"\.\s+", scope) if s.strip()]

    best_sentence = ""
    best_overlap = -1
    for sent in sentences:
        sent_tokens = set(tokenize(sent))
        overlap = len(q_tokens.intersection(sent_tokens))
        if overlap > best_overlap:
            best_overlap = overlap
            best_sentence = sent

    if not best_sentence and sentences:
        best_sentence = sentences[0]

    if best_sentence and not best_sentence.endswith("."):
        best_sentence += "."

    if len(best_sentence) > 160:
        best_sentence = best_sentence[:157].rsplit(" ", 1)[0] + "..."

    # 3. Assemble factual 1-2 sentence explanation
    if matched_kws:
        kws_str = ", ".join(matched_kws[:3])
        explanation = f"Matches procurement requirements for {kws_str}. Official BIS scope: {best_sentence}"
    elif best_overlap > 0:
        category = standard.get("category") or "BIS Specification"
        explanation = f"Applies to {category} specifications matching query parameters. Official BIS scope: {best_sentence}"
    else:
        title = standard.get("title") or standard.get("standard_number", "")
        explanation = f"Relevant under {title}. Official BIS scope: {best_sentence}"

    return explanation


def rank_and_filter_candidates(
    query: str,
    candidates: list[dict[str, Any]],
    limit: int = 10,
    threshold: float | None = None,
    semantic_weight: float = 0.75,
    metadata_weight: float = 0.25
) -> list[dict[str, Any]]:
    """
    Re-ranks candidates using hybrid weighted combination of dense vector
    similarity and domain metadata relevance, then dynamically filters by threshold.
    
    Guarantees:
    - Semantic search remains the primary signal (default 75% weight).
    - Results below threshold are discarded (dynamic result count).
    - Limit is respected as an upper bound.
    - Each candidate is annotated with a factual 1-2 sentence explanation and relevance tier.
    """
    effective_threshold = threshold if threshold is not None else settings.DEFAULT_SCORE_THRESHOLD
    
    scored_candidates = []
    for cand in candidates:
        dense_score = max(0.0, min(1.0, float(cand.get("dense_score", cand.get("similarity_score", 0.0)))))
        
        # Standard record metadata can be directly in candidate or in payload
        meta_dict = {
            "standard_number": cand.get("standard_number"),
            "title": cand.get("title"),
            "category": cand.get("category"),
            "keywords": cand.get("keywords") or [],
            "scope": cand.get("scope", "")
        }
        
        meta_score = compute_metadata_relevance(query, meta_dict)
        
        # Composite calibrated score
        composite_score = (semantic_weight * dense_score) + (metadata_weight * meta_score)
        clamped_score = max(0.0, min(1.0, round(composite_score, 4)))
        
        # Check threshold
        if clamped_score >= effective_threshold:
            cand_copy = dict(cand)
            cand_copy["similarity_score"] = clamped_score
            cand_copy["dense_score"] = round(dense_score, 4)
            cand_copy["metadata_score"] = round(meta_score, 4)
            cand_copy["relevance_label"] = get_relevance_label(clamped_score)
            cand_copy["explanation"] = generate_explanation(query, meta_dict)
            scored_candidates.append(cand_copy)

    # Sort descending by composite similarity score
    scored_candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return scored_candidates[:limit]
