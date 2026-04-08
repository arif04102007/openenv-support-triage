"""
Graders for the three OpenEnv tasks.
Each grader returns a float in [0.0, 1.0].
"""

import json
import re


# ─────────────────────────────────────────
# TASK 1 (EASY): Urgency Classification
# ─────────────────────────────────────────

URGENCY_LEVELS = ["low", "medium", "high", "critical"]
URGENCY_RANK = {u: i for i, u in enumerate(URGENCY_LEVELS)}


def grade_easy(agent_response: str, ground_truth: dict) -> float:
    """
    Full credit (1.0) for exact urgency match.
    Partial credit (0.4) if agent is exactly one level off.
    Zero otherwise.
    """
    predicted = agent_response.strip().lower()
    # Extract just the urgency word if the agent wrote extra text
    for level in URGENCY_LEVELS:
        if level in predicted:
            predicted = level
            break

    correct = ground_truth["urgency"]
    if predicted == correct:
        return 1.0
    if predicted in URGENCY_LEVELS:
        diff = abs(URGENCY_RANK[predicted] - URGENCY_RANK[correct])
        if diff == 1:
            return 0.4
    return 0.0


# ─────────────────────────────────────────
# TASK 2 (MEDIUM): Categorize + Extract
# ─────────────────────────────────────────

VALID_CATEGORIES = {"billing", "technical", "account", "shipping", "general"}


def grade_medium(agent_response: str, ground_truth: dict) -> float:
    """
    Score is average of three sub-scores:
      - Category match (0 or 1)
      - Customer name extracted (0 or 1, case-insensitive)
      - Complaint captured (0, 0.5, or 1 based on keyword overlap)
    """
    # Try to parse JSON from the response
    try:
        # Strip markdown code fences if present
        clean = re.sub(r"```(?:json)?|```", "", agent_response).strip()
        data = json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        # Fallback: try to extract fields with regex
        data = _extract_fallback(agent_response)

    scores = []

    # Sub-score 1: category
    predicted_cat = str(data.get("category", "")).strip().lower()
    scores.append(1.0 if predicted_cat == ground_truth["category"] else 0.0)

    # Sub-score 2: customer name (case-insensitive partial match)
    predicted_name = str(data.get("customer_name", "")).strip().lower()
    correct_name = ground_truth["customer_name"].lower()
    name_score = 0.0
    if correct_name in predicted_name or predicted_name in correct_name:
        name_score = 1.0
    elif any(part in predicted_name for part in correct_name.split()):
        name_score = 0.5
    scores.append(name_score)

    # Sub-score 3: complaint keyword overlap
    predicted_complaint = str(data.get("primary_complaint", "")).lower()
    correct_complaint = ground_truth["primary_complaint"].lower()
    correct_keywords = set(re.findall(r"\b\w{4,}\b", correct_complaint))
    predicted_keywords = set(re.findall(r"\b\w{4,}\b", predicted_complaint))
    if correct_keywords:
        overlap = len(correct_keywords & predicted_keywords) / len(correct_keywords)
        scores.append(min(overlap * 1.5, 1.0))  # boost partial overlap
    else:
        scores.append(0.0)

    return round(sum(scores) / len(scores), 4)


def _extract_fallback(text: str) -> dict:
    """Attempt to extract category, name, complaint from free text."""
    result = {}
    for cat in VALID_CATEGORIES:
        if cat in text.lower():
            result["category"] = cat
            break
    name_match = re.search(r"(?:name|customer)[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)", text)
    if name_match:
        result["customer_name"] = name_match.group(1)
    complaint_match = re.search(r"(?:complaint|issue|problem)[:\s]+(.+)", text, re.IGNORECASE)
    if complaint_match:
        result["primary_complaint"] = complaint_match.group(1).strip()
    return result


# ─────────────────────────────────────────
# TASK 3 (HARD): Full Triage + Draft Reply
# ─────────────────────────────────────────

RESPONSE_QUALITY_KEYWORDS = [
    "thank", "sorry", "apologize", "understand", "help",
    "resolve", "team", "contact", "please", "account"
]


def grade_hard(agent_response: str, ground_truth: dict, email: dict) -> float:
    """
    Score breakdown (each 0–1, averaged):
      - Urgency identified in response (0 or 1)
      - Category identified in response (0 or 1)
      - Customer name used in reply (0 or 1)
      - Response quality: empathy + professionalism (0–1)
      - Response addresses the actual issue (0–1)
    """
    response_lower = agent_response.lower()
    scores = []

    # Sub-score 1: urgency mentioned
    urgency = ground_truth["urgency"]
    scores.append(1.0 if urgency in response_lower else 0.5)

    # Sub-score 2: category/issue type mentioned
    category = ground_truth["category"]
    category_synonyms = {
        "billing": ["billing", "charge", "invoice", "payment", "refund"],
        "technical": ["technical", "error", "crash", "bug", "issue"],
        "account": ["account", "login", "access", "password", "locked"],
        "shipping": ["shipping", "delivery", "order", "package", "shipment"],
        "general": ["question", "help", "information", "inquiry"],
    }
    synonyms = category_synonyms.get(category, [category])
    scores.append(1.0 if any(s in response_lower for s in synonyms) else 0.0)

    # Sub-score 3: customer name used
    first_name = ground_truth["customer_name"].split()[0].lower()
    scores.append(1.0 if first_name in response_lower else 0.0)

    # Sub-score 4: response quality (empathy/professionalism keywords)
    quality_hits = sum(1 for kw in RESPONSE_QUALITY_KEYWORDS if kw in response_lower)
    scores.append(min(quality_hits / 5, 1.0))

    # Sub-score 5: addresses the actual issue (keyword overlap with complaint)
    complaint = ground_truth["primary_complaint"].lower()
    issue_keywords = set(re.findall(r"\b\w{4,}\b", complaint))
    response_keywords = set(re.findall(r"\b\w{4,}\b", response_lower))
    if issue_keywords:
        overlap = len(issue_keywords & response_keywords) / len(issue_keywords)
        scores.append(min(overlap * 2, 1.0))
    else:
        scores.append(0.5)

    # Minimum length check — too short = not a real reply
    if len(agent_response.strip()) < 80:
        return 0.1

    return round(sum(scores) / len(scores), 4)
