from ocrbychamod.models import Word
from ocrbychamod.kv_extractor import pairs_from_words


def line(y, *items):
    return [Word(t, x, y, x + 10 * len(t), y + 20, 0.9) for t, x in items]


def kv(words, **kw):
    return [(p.key, p.value) for p in pairs_from_words(words, **kw)]


def test_value_in_same_phrase():
    assert kv(line(0, ("Total:", 0), ("45.00", 70))) == [("Total", "45.00")]


def test_value_right_after_wide_gap():
    assert kv(line(0, ("Date:", 0), ("01/02/2026", 200))) == [("Date", "01/02/2026")]


def test_two_pairs_on_one_line():
    words = line(0, ("Date:", 0), ("01/02/2026", 120), ("PO", 400), ("No:", 430), ("1234", 600))
    assert kv(words) == [("Date", "01/02/2026"), ("PO No", "1234")]


def test_value_below_key():
    words = line(0, ("Address:", 0)) + line(30, ("12", 0), ("Main", 30), ("St", 80))
    assert kv(words) == [("Address", "12 Main St")]


def test_time_is_not_a_key():
    assert kv(line(0, ("Opened", 0), ("12:30", 70))) == []
    assert kv(line(0, ("Time:", 0), ("12:30", 70))) == [("Time", "12:30")]
    assert kv(line(0, ("Opened", 0), ("12:30", 70))) == []

def test_empty_value_dropped_unless_requested():
    words = line(0, ("Note:", 0))
    assert kv(words) == []
    assert kv(words, keep_empty=True) == [("Note", "")]
    
    
def test_big_gap_two_phrases_is_a_pair():
    assert kv(line(0, ("TICKET", 0), ("#15504621", 200))) == [("TICKET", "#15504621")]


def test_normal_gap_is_just_text():
    assert kv(line(0, ("Sales", 0), ("Receipt", 60))) == []


def test_three_phrase_row_is_not_a_pair():
    assert kv(line(0, ("Kenevo", 0), ("1", 300), ("$10999.99", 500))) == []


def test_code_like_key_is_not_a_pair():
    assert kv(line(0, ("EG1C0043323511", 0), ("$0.00", 300))) == []


def test_hash_marker():
    assert kv(line(0, ("Id#", 0), ("1277", 40))) == [("Id", "1277")]