from pii_benchmarking import run_experiments


def test_is_labeled_strict():
    """Abe Lincoln yada yada."""
    actual_start_char = 0
    actual_end_char = 11
    entities = [{'entity_label': 'PERSON_NAME', 'start_char': 0, 'end_char': 11, 'score': 0.85}]
    assert run_experiments.is_labeled(entities, actual_start_char, actual_end_char) == 'PERSON_NAME'


def test_is_labeled_partial():
    """Abe Lincoln yada yada."""
    actual_start_char = 0
    actual_end_char = 11
    entities = [{'entity_label': 'PERSON_NAME', 'start_char': 1, 'end_char': 7, 'score': 0.85}]
    assert run_experiments.is_labeled(entities, actual_start_char, actual_end_char) == 'NONE'


def test_is_labeled_none():
    """Abe Lincoln yada yada."""
    actual_start_char = 0
    actual_end_char = 11
    entities = [{'entity_label': 'LOCATION', 'start_char': 12, 'end_char': 18, 'score': 0.85}]
    assert run_experiments.is_labeled(entities, actual_start_char, actual_end_char) == 'NONE'


test_is_labeled_strict()
test_is_labeled_partial()
test_is_labeled_none()
