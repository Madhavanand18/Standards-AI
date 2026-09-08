import pytest
from app.services.ranker import compute_metadata_relevance, rank_and_filter_candidates

def test_compute_metadata_relevance_field_matching():
    standard = {
        "standard_number": "IS 1786:2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification",
        "category": "Reinforcement Steel / Construction",
        "keywords": ["TMT bars", "reinforcement steel", "deformed steel bars", "RCC", "concrete reinforcement", "Fe 415", "Fe 500", "rebar"],
        "scope": "Covers the requirements of deformed steel bars and wires for use as reinforcement in concrete in strength grades Fe 415, Fe 500, Fe 550."
    }

    # Query matching keywords, title, category, scope
    query = "Fe 500 ribbed steel bars for reinforced concrete columns"
    score = compute_metadata_relevance(query, standard)
    assert score > 0.5

    # Query for completely unrelated category
    unrelated_query = "Polyvinyl chloride insulated domestic wiring cable 450V"
    unrelated_score = compute_metadata_relevance(unrelated_query, standard)
    assert unrelated_score < 0.15

def test_rank_fe500_reinforcement_bars_is1786_above_is2062():
    """
    Requirement: IS 1786 should rank above IS 2062 for:
    'Fe 500 ribbed steel bars for reinforced concrete columns'
    """
    query = "Fe 500 ribbed steel bars for reinforced concrete columns"

    candidates = [
        {
            "standard_number": "IS 2062:2011",
            "title": "Hot Rolled Medium and High Tensile Structural Steel — Specification",
            "category": "Structural Steel",
            "keywords": ["structural steel", "hot rolled steel", "steel plates", "MS angles", "steel beams", "E250", "bridge fabrication"],
            "scope": "Covers the requirements of hot-rolled medium and high tensile structural steel plates, sections, flats, bars, etc. for structural work.",
            "dense_score": 0.62
        },
        {
            "standard_number": "IS 1786:2008",
            "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification",
            "category": "Reinforcement Steel / Construction",
            "keywords": ["TMT bars", "reinforcement steel", "deformed steel bars", "RCC", "concrete reinforcement", "Fe 415", "Fe 500", "rebar"],
            "scope": "Covers the requirements of deformed steel bars and wires for use as reinforcement in concrete in strength grades Fe 415, Fe 500, Fe 550.",
            "dense_score": 0.70
        },
        {
            "standard_number": "IS 2925:1984",
            "title": "Specification for Industrial Safety Helmets",
            "category": "Personal Protective Equipment",
            "keywords": ["safety helmets", "PPE", "head protection"],
            "scope": "Covers physical and performance requirements for industrial safety helmets.",
            "dense_score": 0.18
        }
    ]

    results = rank_and_filter_candidates(query, candidates, limit=10, threshold=0.35)

    assert len(results) == 2  # Safety helmets below threshold 0.35 should be excluded
    assert results[0]["standard_number"] == "IS 1786:2008"
    assert results[1]["standard_number"] == "IS 2062:2011"
    assert results[0]["similarity_score"] > results[1]["similarity_score"]

def test_dynamic_results_threshold_filtering():
    """
    Requirement: Return only results above a configurable threshold.
    If few standards are relevant, return fewer results.
    """
    query = "High density polyethylene HDPE pipes for potable water supply"

    candidates = [
        {
            "standard_number": "IS 4984:2016",
            "title": "High Density Polyethylene (HDPE) Pipes for Water Supply",
            "category": "Plastic Piping Systems",
            "keywords": ["HDPE pipes", "potable water pipe", "water supply", "PE 100"],
            "scope": "Specifies requirements for HDPE pipes for conveyance of water for human consumption.",
            "dense_score": 0.85
        },
        {
            "standard_number": "IS 3589:2001",
            "title": "Seamless or Electrically Welded Steel Pipes for Water, Gas and Sewage",
            "category": "Steel Pipes & Fittings",
            "keywords": ["large diameter steel pipes", "sewage pipes", "bulk water transmission"],
            "scope": "Covers requirements for steel pipes for conveyance of water, gas, and sewage.",
            "dense_score": 0.44
        },
        {
            "standard_number": "IS 1077:2020",
            "title": "Common Burnt Clay Building Bricks — Specification",
            "category": "Building Materials",
            "keywords": ["clay bricks", "building bricks", "masonry bricks"],
            "scope": "Specifies requirements for dimensions, quality, and strength of common burnt clay building bricks.",
            "dense_score": 0.20
        },
        {
            "standard_number": "IS 2925:1984",
            "title": "Specification for Industrial Safety Helmets",
            "category": "Personal Protective Equipment",
            "keywords": ["safety helmets", "PPE", "head protection"],
            "scope": "Covers requirements for industrial safety helmets.",
            "dense_score": 0.15
        }
    ]

    # With default threshold 0.38: only the 2 pipe standards should pass
    results_normal = rank_and_filter_candidates(query, candidates, limit=10, threshold=0.38)
    assert len(results_normal) == 2
    assert [r["standard_number"] for r in results_normal] == ["IS 4984:2016", "IS 3589:2001"]

    # With higher threshold 0.60: only IS 4984 passes
    results_high = rank_and_filter_candidates(query, candidates, limit=10, threshold=0.60)
    assert len(results_high) == 1
    assert results_high[0]["standard_number"] == "IS 4984:2016"

    # With limit=1: only top 1 is returned
    results_limit1 = rank_and_filter_candidates(query, candidates, limit=1, threshold=0.38)
    assert len(results_limit1) == 1
    assert results_limit1[0]["standard_number"] == "IS 4984:2016"

from app.services.ranker import get_relevance_label, generate_explanation

def test_relevance_label_tiers():
    assert get_relevance_label(0.75) == "High"
    assert get_relevance_label(0.60) == "High"
    assert get_relevance_label(0.59) == "Medium"
    assert get_relevance_label(0.40) == "Medium"
    assert get_relevance_label(0.39) == "Low"
    assert get_relevance_label(0.15) == "Low"

def test_generate_factual_explanation():
    standard = {
        "standard_number": "IS 1786:2008",
        "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement — Specification",
        "category": "Reinforcement Steel / Construction",
        "keywords": ["TMT bars", "reinforcement steel", "deformed steel bars", "RCC", "concrete reinforcement", "Fe 415", "Fe 500", "rebar"],
        "scope": "Covers the requirements of deformed steel bars and wires for use as reinforcement in concrete in strength grades Fe 415, Fe 500, Fe 550."
    }

    query = "Fe 500 ribbed steel bars for reinforced concrete columns"
    explanation = generate_explanation(query, standard)

    assert explanation is not None
    assert len(explanation) > 10
    # Must mention matched requirements / keywords
    assert "Fe 500" in explanation or "concrete" in explanation or "reinforcement" in explanation
    # Must ground in official BIS scope
    assert "scope" in explanation.lower()
    # Must not contain unsupported mandatory/regulatory claims
    assert "mandatory" not in explanation.lower()
    assert "qco" not in explanation.lower()

def test_rank_and_filter_populates_explanation_and_labels():
    query = "12 mm TMT reinforcement bars for RCC construction"
    candidates = [
        {
            "standard_number": "IS 1786:2008",
            "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
            "category": "Reinforcement Steel / Construction",
            "keywords": ["TMT bars", "reinforcement steel", "RCC"],
            "scope": "Covers deformed steel bars for concrete reinforcement.",
            "dense_score": 0.70
        }
    ]

    results = rank_and_filter_candidates(query, candidates, limit=5, threshold=0.35)
    assert len(results) == 1
    res = results[0]
    assert res["relevance_label"] == "High"
    assert "TMT bars" in res["explanation"] or "RCC" in res["explanation"] or "scope" in res["explanation"].lower()
