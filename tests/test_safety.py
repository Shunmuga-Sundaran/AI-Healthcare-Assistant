import pytest

from modules import safety


@pytest.mark.parametrize("text", [
    "I have severe chest pain and my left arm hurts",
    "chest tightness since morning",
    "I can't breathe properly",
    "shortness of breath while resting",
    "my father collapsed and is unresponsive",
    "she had a seizure",
    "heavy bleeding that won't stop",
    "my throat is swelling after eating peanuts",
    "I think I took an overdose",
    "sudden numbness on one side and slurred speech",
    "worst headache of my life",
    "I want to die",
])
def test_emergency_phrases_detected(text):
    assert safety.check_emergency(text), text


@pytest.mark.parametrize("text", [
    "I have a mild headache and a runny nose",
    "sore throat and cough for two days",
    "feeling tired with a slight fever",
])
def test_common_symptoms_not_flagged(text):
    assert safety.check_emergency(text) == []


def test_empty_text_returns_empty_list():
    assert safety.check_emergency("") == []
    assert safety.check_emergency(None) == []


def test_case_insensitive():
    assert safety.check_emergency("CHEST PAIN") == ["chest pain or pressure"]


def test_self_harm_flag():
    assert safety.is_self_harm(safety.check_emergency("I want to kill myself"))
    assert not safety.is_self_harm(safety.check_emergency("chest pain"))


def test_text_constants_are_present():
    assert "not a substitute" in safety.DISCLAIMER
    assert "emergency" in safety.EMERGENCY_WARNING.lower()
