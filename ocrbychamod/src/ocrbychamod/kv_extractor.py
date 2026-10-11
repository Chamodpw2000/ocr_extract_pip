from statistics import mean

from .layout import build_lines, build_phrases
from .models import Pair, Phrase, Word


def _find_separator(text: str) -> int:
    """Index of a key marker: a colon (not in times/URLs) or a trailing '#' after letters (Id#)."""
    for i, ch in enumerate(text):
        if ch == "#" and i > 0 and i == len(text) - 1 and text[:i].isalpha():
            return i
        if ch != ":":
            continue
        prev_ch = text[i - 1] if i > 0 else ""
        next_ch = text[i + 1] if i + 1 < len(text) else ""
        if prev_ch.isdigit() and next_ch.isdigit():
            continue
        if text[i + 1:i + 3] == "//":
            continue
        return i
    return -1


def _is_key(phrase: Phrase) -> bool:
    return any(_find_separator(w.text) != -1 for w in phrase.words)


def _is_label(text: str, min_alpha: float = 0.6) -> bool:
    """True if the text is mostly letters, so 'TICKET' passes and 'EG1C0043323511' does not."""
    alnum = [c for c in text if c.isalnum()]
    return bool(alnum) and sum(c.isalpha() for c in alnum) / len(alnum) >= min_alpha


def _split_at_colon(phrase: Phrase):
    """Split a phrase at its first key marker -> (key_words, key_text, value_words, value_text)."""
    for i, w in enumerate(phrase.words):
        pos = _find_separator(w.text)
        if pos == -1:
            continue
        before, after = w.text[:pos].strip(), w.text[pos + 1:].strip()
        head, tail = list(phrase.words[:i]), list(phrase.words[i + 1:])
        key_words = head + ([w] if before else [])
        value_words = ([w] if after else []) + tail
        key_text = " ".join([x.text for x in head] + ([before] if before else []))
        value_text = " ".join(([after] if after else []) + [x.text for x in tail])
        return key_words, key_text.strip(), value_words, value_text.strip()
    return None


def _overlaps_x(a: Phrase, b: Phrase) -> bool:
    return min(a.x1, b.x1) - max(a.x0, b.x0) > 0


def _find_value_below(key: Phrase, next_line: list[Phrase]) -> Phrase | None:
    for p in sorted(next_line, key=lambda p: p.x0):
        if _is_key(p):
            continue
        if p.y0 - key.y1 < 2 * key.h and _overlaps_x(p, key):
            return p
    return None


def _make_pair(key_text, key_words, value_text, value_words, line) -> Pair:
    used = key_words + value_words
    return Pair(
        key=key_text,
        value=value_text,
        confidence=round(mean(w.conf for w in used), 3),
        bbox=(min(w.x0 for w in used), min(w.y0 for w in used),
              max(w.x1 for w in used), max(w.y1 for w in used)),
        line=line,
    )


def _gap_pair(phrases: list[Phrase]):
    """A line with exactly two phrases (big gap between them) and a label-like left side."""
    if len(phrases) != 2:
        return None
    key, value = phrases
    return (key, value) if _is_label(key.text) else None


def pairs_from_words(words: list[Word], *, gap_factor: float = 1.5,
                     keep_empty: bool = False, min_conf: float = 0.3) -> list[Pair]:
    words = [w for w in words if w.conf >= min_conf]
    lines = [build_phrases(line, gap_factor) for line in build_lines(words)]
    pairs: list[Pair] = []

    for li, phrases in enumerate(lines):
        # No colon or '#' marker on this line: use the gap rule
        if not any(_is_key(p) for p in phrases):
            found = _gap_pair(phrases)
            if found:
                key, value = found
                pairs.append(_make_pair(key.text, list(key.words),
                                        value.text, list(value.words), li))
            continue

        # Marker rule (colon or '#')
        for pi, phrase in enumerate(phrases):
            split = _split_at_colon(phrase)
            if split is None:
                continue
            key_words, key_text, value_words, value_text = split
            if not key_text:
                continue

            if not value_text and pi + 1 < len(phrases) and not _is_key(phrases[pi + 1]):
                nxt = phrases[pi + 1]
                value_words, value_text = list(nxt.words), nxt.text
            if not value_text and li + 1 < len(lines):
                below = _find_value_below(phrase, lines[li + 1])
                if below:
                    value_words, value_text = list(below.words), below.text

            if not value_text and not keep_empty:
                continue
            pairs.append(_make_pair(key_text, key_words, value_text, value_words, li))
    return pairs