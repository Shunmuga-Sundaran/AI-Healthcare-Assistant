from modules import nlp_processor as nlp


def test_clean_text_collapses_whitespace_and_symbols():
    assert nlp.clean_text("  I   have\n\na   headache!!!  ") == "I have a headache"


def test_clean_text_keeps_decimals_and_apostrophes():
    assert nlp.clean_text("fever of 38.5 and I don't feel well") == "fever of 38.5 and I don't feel well"


def test_normalize_text_lowercases():
    assert nlp.normalize_text("Mild HEADACHE") == "mild headache"


def test_empty_and_none_are_invalid():
    assert nlp.validate_input("")[0] is False
    assert nlp.validate_input("    ")[0] is False
    assert nlp.validate_input(None)[0] is False


def test_too_short_is_invalid():
    ok, message = nlp.validate_input("pain")
    assert ok is False and "too short" in message


def test_numbers_only_is_invalid():
    assert nlp.validate_input("123 456 789")[0] is False


def test_too_long_is_invalid():
    assert nlp.validate_input("headache " * 400)[0] is False


def test_valid_input():
    assert nlp.validate_input("I have a mild headache and a runny nose.") == (True, "")


def test_extract_keywords():
    found = nlp.extract_keywords("I have a mild headache and a runny nose.")
    assert "headache" in found and "runny nose" in found


def test_keywords_need_whole_words():
    assert nlp.extract_keywords("my colder days") == []


def test_preprocess_valid_and_invalid():
    good = nlp.preprocess("Fever and cough for two days!!")
    assert good["is_valid"] and good["cleaned_text"] == "Fever and cough for two days"
    assert set(good["keywords"]) == {"fever", "cough"}
    bad = nlp.preprocess("")
    assert not bad["is_valid"] and bad["cleaned_text"] == "" and bad["keywords"] == []
