import re

DISCLAIMER = (
    "This application provides general health information for educational "
    "purposes only. It is not a medical diagnosis and is not a substitute for "
    "advice from a qualified healthcare professional. AI-generated responses "
    "are not medically verified and may contain mistakes."
)

EMERGENCY_WARNING = (
    "If you think you or someone else may be having a medical emergency, "
    "contact your local emergency number (112 in India) or go to the nearest "
    "emergency department immediately. Do not rely on this chatbot for "
    "emergencies."
)

EMERGENCY_GUIDANCE = (
    "Your description includes symptoms that can sometimes be serious.\n\n"
    "**Please seek emergency medical care now.** Call your local emergency "
    "number (112 in India) or go to the nearest emergency department. If "
    "possible, do not go alone and do not drive yourself.\n\n"
    "This is an automatic safety message based on matching certain phrases. "
    "It is not a diagnosis, and no AI response was generated for this input."
)

# (label, regex) pairs. Labels are shown to the user so the match is transparent.
EMERGENCY_PATTERNS = [
    ("chest pain or pressure", r"\bchest\s+(pain|pains|pressure|tightness|discomfort)\b|\bpain\s+in\s+(my\s+)?chest\b"),
    ("heart attack", r"\bheart\s+attack\b"),
    ("difficulty breathing", r"\b(can'?t|cannot|can\s+not|unable\s+to|trouble|difficulty|struggling\s+to)\s+breath(e|ing)?\b|\bshort(ness)?\s+of\s+breath\b|\bgasping\b"),
    ("stroke signs", r"\bstroke\b|\bface\s+drooping\b|\bslurred\s+speech\b|\bsudden\s+(weakness|numbness)\b"),
    ("loss of consciousness", r"\b(unconscious|unresponsive|passed\s+out|fainted|fainting|collapsed|blacked\s+out)\b"),
    ("seizure", r"\b(seizure|seizures|convulsion|convulsions|convulsing)\b"),
    ("severe bleeding", r"\b(severe|heavy|uncontrolled|won'?t\s+stop)\s+bleeding\b|\bbleeding\s+(heavily|badly|a\s+lot)\b|\bcoughing\s+(up\s+)?blood\b|\bvomiting\s+blood\b|\bblood\s+in\s+(my\s+)?(vomit|stool)\b"),
    ("severe allergic reaction", r"\banaphyla\w*\b|\b(throat|tongue|lips?|face)\s+(is\s+)?(swelling|swollen)\b|\bswelling\s+of\s+(the\s+)?(throat|tongue|face)\b"),
    ("poisoning or overdose", r"\boverdose\w*\b|\bpoison(ed|ing)?\b|\bswallowed\s+(poison|bleach|chemicals?)\b"),
    ("severe head injury", r"\b(severe|serious)\s+head\s+(injury|trauma)\b|\bhit\s+(my\s+)?head\b.*\b(vomit|confus|unconscious)\w*"),
    ("severe sudden pain", r"\b(worst|sudden\s+severe|unbearable|excruciating)\s+(headache|pain)\b|\bsevere\s+(abdominal|stomach)\s+pain\b"),
    ("confusion", r"\b(confused|confusion|disoriented)\b"),
    ("thoughts of self-harm", r"\b(suicid\w*|kill\s+myself|end\s+my\s+life|want\s+to\s+die|hurt\s+myself|self[-\s]?harm)\b"),
]

SELF_HARM_SUPPORT = (
    "If you are thinking about harming yourself, please contact a local "
    "emergency service or a crisis helpline right now, or reach out to a "
    "trusted person near you. You do not have to handle this alone."
)

_COMPILED = [(label, re.compile(pattern, re.IGNORECASE)) for label, pattern in EMERGENCY_PATTERNS]


def check_emergency(text: str) -> list:
    """Return the labels of emergency patterns found in the text.

    An empty list means no pattern matched. It does NOT mean the symptoms are
    safe.
    """
    if not text:
        return []
    return [label for label, regex in _COMPILED if regex.search(text)]


def is_self_harm(matches: list) -> bool:
    """True if the matched labels include the self-harm pattern."""
    return "thoughts of self-harm" in matches
