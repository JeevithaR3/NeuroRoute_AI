"""
NeuroRoute Query Analyzer
Analyzes incoming query text to determine task type, domain, and complexity level.

Fixed: short/simple queries (e.g. "2+2", "what is water") now correctly get LOW complexity
       instead of being bumped up by the task default.
"""

import re


# ─── Complexity keywords ─────────────────────────────────────────────────────

LOW_PATTERNS = [
    r"\bwhat is\b", r"\bwho is\b", r"\bdefine\b", r"\bwhen did\b",
    r"\bhow many\b", r"\bwhat year\b", r"\bname the\b", r"\blist\b",
    r"\bcapital of\b", r"\bspell\b", r"\btranslate\b",
    r"\d+\s*[\+\-\*\/\^]\s*\d+",   # math expressions: 2+2, 10*5, etc.
    r"^\d[\d\s\+\-\*\/\^\(\)\.]*$", # pure math strings
    r"\byes or no\b", r"\bis it\b", r"\bare you\b", r"\bhow old\b",
    r"\bwhat color\b", r"\bwhat time\b", r"\bwhat day\b",
]

MEDIUM_PATTERNS = [
    r"\bsummariz\b", r"\bexplain\b", r"\bdescribe\b", r"\bsimplif\b",
    r"\bcompare\b", r"\bdifference between\b", r"\bhow does\b",
    r"\bwhat are\b", r"\bwhat causes\b", r"\boverview\b", r"\boutline\b",
]

HIGH_PATTERNS = [
    r"\banalyze\b", r"\bevaluate\b", r"\bcritique\b", r"\bargue\b",
    r"\bdesign\b", r"\barchitect\b", r"\bimplement\b", r"\bprove\b",
    r"\bresearch\b", r"\binvestigate\b", r"\bphilosoph\b", r"\bquantum\b",
    r"\bneural network\b", r"\bdeep learning\b",
    r"\bcreate\b.*\bsystem\b", r"\bwrite.*code\b", r"\bdebug\b",
]

# ─── Domain keywords ─────────────────────────────────────────────────────────

DOMAINS = {
    "science":      ["quantum", "physics", "biology", "chemistry", "atom",
                     "molecule", "evolution", "dna", "cell", "energy", "force", "gravity"],
    "technology":   ["algorithm", "code", "programming", "software", "hardware",
                     "database", "network", "api", "machine learning", "ai", "neural"],
    "history":      ["war", "century", "ancient", "civilization", "empire",
                     "revolution", "historical", "president", "king", "queen", "battle"],
    "mathematics":  ["equation", "formula", "proof", "theorem", "calculus",
                     "algebra", "geometry", "statistics", "probability"],
    "medicine":     ["disease", "symptom", "treatment", "drug", "patient",
                     "diagnosis", "hospital", "health", "medical"],
    "general":      [],
}

# ─── Task complexity HINTS (not overrides) ───────────────────────────────────
# These are only applied when content analysis can't determine complexity clearly.

TASK_COMPLEXITY_HINT = {
    "ask":       "MEDIUM",   # popup uses ask for all queries — default MEDIUM, content can lower to LOW
    "explain":   "MEDIUM",
    "summarize": "MEDIUM",
    "simplify":  "LOW",
    "analyze":   "HIGH",
    "research":  "HIGH",
}


def analyze_query(text: str, task: str = "ask") -> dict:
    text_lower = text.lower().strip()
    word_count = len(text.split())

    # Detect complexity purely from content first
    content_complexity = _detect_complexity(text_lower, word_count)

    # Task hint only RAISES complexity, never lowers it
    # e.g. "2+2" with task=ask stays LOW; "explain quantum physics" with task=ask becomes MEDIUM
    task_hint = TASK_COMPLEXITY_HINT.get(task, "LOW")

    # Only apply task hint if content gave LOW — this prevents task from
    # overriding clear HIGH/MEDIUM signals from content
    if content_complexity == "LOW":
        complexity = task_hint
    else:
        complexity = content_complexity

    # But pure math / very short queries always stay LOW regardless of task
    if _is_trivially_simple(text_lower, word_count):
        complexity = "LOW"

    domain         = _detect_domain(text_lower)
    reasoning_depth = _get_reasoning_depth(complexity)
    summary        = _generate_summary(text, task, domain)

    return {
        "task":            task,
        "domain":          domain,
        "complexity":      complexity,
        "reasoning_depth": reasoning_depth,
        "word_count":      word_count,
        "summary":         summary,
    }


def _is_trivially_simple(text_lower: str, word_count: int) -> bool:
    """
    Returns True ONLY for pure math expressions like 2+2, 10*5.
    Nothing else should be force-overridden to LOW.
    """
    # Pure math expression only (e.g. "2+2", "100 / 4")
    if re.match(r'^[\d\s\+\-\*\/\^\(\)\.]+$', text_lower.strip()):
        return True

    # Inline math like "what is 2+2" — keep LOW only if the whole thing is a math lookup
    if re.search(r'\d+\s*[\+\-\*\/]\s*\d+', text_lower) and word_count <= 5:
        return True

    return False


def _detect_complexity(text_lower: str, word_count: int) -> str:
    # HIGH patterns always win first
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, text_lower):
            return "HIGH"

    # Long queries are always HIGH
    if word_count > 50:
        return "HIGH"

    # MEDIUM patterns
    for pattern in MEDIUM_PATTERNS:
        if re.search(pattern, text_lower):
            return "MEDIUM"

    # Medium-length with no signal → MEDIUM (not LOW)
    if word_count > 15:
        return "MEDIUM"

    # Explicit LOW patterns (what is, who is, define, etc.)
    for pattern in LOW_PATTERNS:
        if re.search(pattern, text_lower):
            return "LOW"

    # Short query, no signal → LOW
    if word_count <= 6:
        return "LOW"

    # Default: anything 7–15 words with no pattern → MEDIUM
    return "MEDIUM"


def _detect_domain(text_lower: str) -> str:
    scores = {domain: 0 for domain in DOMAINS}
    for domain, keywords in DOMAINS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[domain] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def _get_reasoning_depth(complexity: str) -> str:
    return {"LOW": "shallow", "MEDIUM": "moderate", "HIGH": "deep"}.get(complexity, "moderate")


def _generate_summary(text: str, task: str, domain: str) -> str:
    truncated = text[:60] + ("..." if len(text) > 60 else "")
    return f"User requesting {task} on {domain} content: {truncated}"
