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
    r"\d+\s*[\+\-\*\/\^]\s*\d+",
    r"^\d[\d\s\+\-\*\/\^\(\)\.]*$",
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

TASK_COMPLEXITY_HINT = {
    "ask":       "LOW",
    "explain":   "MEDIUM",
    "summarize": "MEDIUM",
    "simplify":  "LOW",
    "analyze":   "HIGH",
    "research":  "HIGH",
}


def analyze_query(text: str, task: str = "ask") -> dict:
    text_lower = text.lower().strip()
    word_count = len(text.split())

    content_complexity = _detect_complexity(text_lower, word_count)
    task_hint = TASK_COMPLEXITY_HINT.get(task, "LOW")

    if content_complexity == "LOW":
        complexity = task_hint
    else:
        complexity = content_complexity

    if _is_trivially_simple(text_lower, word_count):
        complexity = "LOW"

    domain          = _detect_domain(text_lower)
    reasoning_depth = _get_reasoning_depth(complexity)
    summary         = _generate_summary(text, task, domain)

    return {
        "task":            task,
        "domain":          domain,
        "complexity":      complexity,
        "reasoning_depth": reasoning_depth,
        "word_count":      word_count,
        "summary":         summary,
    }


def _is_trivially_simple(text_lower: str, word_count: int) -> bool:
    if re.match(r'^[\d\s\+\-\*\/\^\(\)\.]+$', text_lower.strip()):
        return True
    if re.search(r'\d+\s*[\+\-\*\/]\s*\d+', text_lower):
        return True
    if word_count <= 3:
        return True
    return False


def _detect_complexity(text_lower: str, word_count: int) -> str:
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, text_lower):
            return "HIGH"
    if word_count > 100:
        return "HIGH"
    for pattern in MEDIUM_PATTERNS:
        if re.search(pattern, text_lower):
            return "MEDIUM"
    if word_count > 40:
        return "MEDIUM"
    for pattern in LOW_PATTERNS:
        if re.search(pattern, text_lower):
            return "LOW"
    if word_count <= 10:
        return "LOW"
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