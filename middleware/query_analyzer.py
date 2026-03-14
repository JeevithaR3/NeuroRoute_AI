"""
NeuroRoute Query Analyzer
Analyzes incoming query text to determine task type, domain, and complexity level.

ROUTING LOGIC — when each tier is used:
─────────────────────────────────────────
LOW   → small_model  : simple facts, definitions, short direct questions,
                       single-word answers, math, yes/no, "what is X", "who is X"
                       word count ≤ 10 with no complex signal

MEDIUM → medium_model : explanations, summaries, comparisons, how-things-work,
                        moderate reasoning, 11–40 words, most everyday questions

HIGH  → large_model  : deep analysis, research, coding, critique, philosophy,
                        complex multi-part questions, word count > 40
"""

import re


# ─── LOW complexity patterns ─────────────────────────────────────────────────
# Simple factual lookups — one correct answer, no reasoning needed

LOW_PATTERNS = [
    # Direct fact lookups
    r"\bwhat is\b", r"\bwhat was\b", r"\bwhat are\b(?= the [a-z]+ of)",
    r"\bwho is\b", r"\bwho was\b", r"\bwho invented\b", r"\bwho created\b",
    r"\bwhen did\b", r"\bwhen was\b", r"\bwhen is\b",
    r"\bwhere is\b", r"\bwhere was\b", r"\bwhere are\b",
    r"\bdefine\b", r"\bmeaning of\b", r"\bdefinition of\b",
    r"\bhow many\b", r"\bhow much\b", r"\bhow old\b", r"\bhow tall\b", r"\bhow far\b",
    r"\bwhat year\b", r"\bwhat date\b", r"\bwhat time\b", r"\bwhat day\b",
    r"\bname the\b", r"\blist the\b", r"\bgive me the name\b",
    r"\bcapital of\b", r"\bcurrency of\b", r"\blanguage of\b",
    r"\bspell\b", r"\btranslate\b", r"\bsynonym\b", r"\bantonym\b",
    r"\byes or no\b", r"\bis it true\b", r"\bis it a\b",
    r"\bwhat color\b", r"\bwhat colour\b", r"\bwhat type\b",
    r"\bfull form of\b", r"\babbreviation\b", r"\bacronym\b",
    r"\bformula for\b", r"\bboiling point\b", r"\bmelting point\b",
    # Math
    r"\d+\s*[\+\-\*\/\^]\s*\d+",
    r"^\d[\d\s\+\-\*\/\^\(\)\.]*$",
    # Conversions
    r"\bconvert\b.*\bto\b", r"\bin celsius\b", r"\bin fahrenheit\b",
    r"\bhow many \w+ in\b",
]

# ─── MEDIUM complexity patterns ───────────────────────────────────────────────
# Needs reasoning, explanation, or multi-step thinking — but not deep

MEDIUM_PATTERNS = [
    r"\bexplain\b", r"\bdescribe\b", r"\bsummariz\b", r"\bsimplif\b",
    r"\bparaphrase\b", r"\brewrite\b", r"\boverall\b",
    r"\bhow does\b", r"\bhow do\b", r"\bhow did\b", r"\bhow would\b",
    r"\bwhat causes\b", r"\bwhy does\b", r"\bwhy did\b", r"\bwhy is\b", r"\bwhy are\b",
    r"\bcompare\b", r"\bcontrast\b", r"\bdifference between\b", r"\bsimilarity\b",
    r"\boverview\b", r"\boutline\b", r"\bsummar\b",
    r"\badvantage\b", r"\bdisadvantage\b", r"\bpros and cons\b", r"\bbenefit\b",
    r"\bwhat happens\b", r"\bwhat happened\b", r"\bwhat will happen\b",
    r"\btell me about\b", r"\bgive me information\b", r"\bhelp me understand\b",
    r"\bwhat are the\b", r"\bwhat were the\b",
]

# ─── HIGH complexity patterns ─────────────────────────────────────────────────
# Deep reasoning, multi-step logic, creative, technical, research

HIGH_PATTERNS = [
    r"\banalyze\b", r"\banalysis\b", r"\bevaluate\b", r"\bassess\b",
    r"\bcritique\b", r"\bcritically\b", r"\bargue\b", r"\bdebate\b",
    r"\bprove\b", r"\bdisprove\b", r"\bjustify\b", r"\bdemonstrate\b",
    r"\bdesign\b", r"\barchitect\b", r"\bbuild\b.*\bsystem\b",
    r"\bimplement\b", r"\bdevelop\b.*\bsolution\b",
    r"\bresearch\b", r"\binvestigate\b", r"\bstudy\b.*\bimpact\b",
    r"\bphilosoph\b", r"\bethic\b", r"\bmoral\b.*\bimplication\b",
    r"\bquantum\b", r"\bneural network\b", r"\bdeep learning\b", r"\bmachine learning\b",
    r"\bwrite.*code\b", r"\bwrite a program\b", r"\bdebug\b", r"\brefactor\b",
    r"\bcreate.*\bsystem\b", r"\bcreate.*\bapp\b", r"\bcreate.*\bmodel\b",
    r"\bpredict\b.*\boutcome\b", r"\bforecast\b", r"\bstrategy\b.*\blong.term\b",
    r"\bimplication\b", r"\bconsequence\b.*\bif\b",
    r"\bcomprehensive\b", r"\bin depth\b", r"\bdetailed.*report\b",
    r"\bhistorical.*significance\b", r"\bsocioeconomic\b", r"\bgeopolitic\b",
]


# ─── Domain keywords ──────────────────────────────────────────────────────────

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

# ─── Task complexity HINTS ────────────────────────────────────────────────────
# Applied ONLY when content analysis returns LOW — task can raise but never lower.
# "ask" is now LOW by default — content signals will raise it if needed.

TASK_COMPLEXITY_HINT = {
    "ask":       "LOW",     # ← changed: simple questions default to small model
    "explain":   "MEDIUM",
    "summarize": "MEDIUM",
    "simplify":  "LOW",
    "analyze":   "HIGH",
    "research":  "HIGH",
}


def analyze_query(text: str, task: str = "ask") -> dict:
    text_lower = text.lower().strip()
    word_count = len(text.split())

    # Step 1: detect from content
    content_complexity = _detect_complexity(text_lower, word_count)

    # Step 2: apply task hint only if content said LOW
    # (task can raise to MEDIUM/HIGH, but never lower from MEDIUM/HIGH)
    task_hint = TASK_COMPLEXITY_HINT.get(task, "LOW")
    complexity_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

    if complexity_order.get(task_hint, 0) > complexity_order.get(content_complexity, 0):
        complexity = task_hint
    else:
        complexity = content_complexity

    # Step 3: pure math always stays LOW no matter what
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
    """Pure math expressions always stay LOW."""
    if re.match(r'^[\d\s\+\-\*\/\^\(\)\.]+$', text_lower.strip()):
        return True
    if re.search(r'\d+\s*[\+\-\*\/]\s*\d+', text_lower) and word_count <= 5:
        return True
    return False


def _detect_complexity(text_lower: str, word_count: int) -> str:
    """
    Determine complexity purely from content + word count.

    Priority order:
    1. HIGH patterns → always HIGH
    2. Very long queries → HIGH
    3. MEDIUM patterns → MEDIUM
    4. LOW patterns → LOW  (checked BEFORE word count trap)
    5. Word count:
       - ≤ 10 words → LOW  (raised from 6 — catches more simple questions)
       - 11–40 words → MEDIUM
       - > 40 words → HIGH
    """
    # HIGH always wins
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, text_lower):
            return "HIGH"

    if word_count > 40:
        return "HIGH"

    # MEDIUM patterns
    for pattern in MEDIUM_PATTERNS:
        if re.search(pattern, text_lower):
            return "MEDIUM"

    # LOW patterns — checked BEFORE word count so "what is X in 12 words" stays LOW
    for pattern in LOW_PATTERNS:
        if re.search(pattern, text_lower):
            return "LOW"

    # Word count fallback
    if word_count <= 10:
        return "LOW"
    if word_count <= 40:
        return "MEDIUM"

    return "HIGH"


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