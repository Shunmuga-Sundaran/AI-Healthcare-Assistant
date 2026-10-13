
import re
import string

MIN_LENGTH = 5      # minimum characters after cleaning
MIN_WORDS = 2       # minimum number of words
MAX_LENGTH = 2000   # keeps prompts and database rows reasonably small

# Simple vocabulary of common symptom terms. Used only to show which terms
# were noticed in the text. It is NOT used to decide that something is safe.
SYMPTOM_KEYWORDS = [
    "headache", "fever", "cough", "cold", "sore throat", "runny nose",
    "stuffy nose", "sneezing", "fatigue", "tired", "nausea", "vomiting",
    "diarrhea", "constipation", "stomach ache", "stomach pain", "back pain",
    "joint pain", "muscle pain", "body ache", "dizziness", "rash", "itching",
    "chills", "sweating", "shortness of breath", "chest pain", "insomnia",
    "loss of appetite", "bloating", "heartburn", "earache", "toothache",
]


def clean_text(text: str) -> str:
    """Trim, collapse whitespace and remove stray punctuation.

    Letters, digits, spaces and the characters , . ' - are kept because they
    are meaningful in descriptions (for example "38.5" or "don't").
    """
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"\s+", " ", text)  # many spaces/newlines -> one space
    keep = set(string.ascii_letters + string.digits + " ,.'-")
    text = "".join(ch if (ch in keep or ch.isalpha()) else " " for ch in text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_text(text: str) -> str:
    """Clean the text and lowercase it (used for keyword matching)."""
    return clean_text(text).lower()


def validate_input(text: str):
    """Check that the description is usable.

    Returns a tuple (is_valid, message). message is empty when valid.
    """
    if text is None or not text.strip():
        return False, "Please describe your symptoms before submitting."

    cleaned = clean_text(text)
    if len(cleaned) < MIN_LENGTH or len(cleaned.split()) < MIN_WORDS:
        return False, (
            "Your description is too short. Please write a few words, "
            "for example: 'mild headache and runny nose for two days'."
        )
    if len(cleaned) > MAX_LENGTH:
        return False, f"Your description is too long. Please keep it under {MAX_LENGTH} characters."
    if not re.search(r"[A-Za-z]", cleaned):
        return False, "Please describe your symptoms using words, not only numbers or symbols."
    return True, ""


def extract_keywords(text: str):
    """Return the known symptom terms found in the text (in vocabulary order)."""
    normalized = " " + normalize_text(text) + " "
    found = []
    for term in SYMPTOM_KEYWORDS:
        if re.search(r"\b" + re.escape(term) + r"\b", normalized):
            found.append(term)
    return found


def preprocess(text: str) -> dict:
    """Run the full pipeline and return a dictionary of results."""
    is_valid, message = validate_input(text)
    return {
        "is_valid": is_valid,
        "message": message,
        "cleaned_text": clean_text(text) if is_valid else "",
        "keywords": extract_keywords(text) if is_valid else [],
    }
