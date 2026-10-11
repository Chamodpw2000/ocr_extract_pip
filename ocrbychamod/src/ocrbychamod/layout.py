from statistics import median

from .models import Phrase, Word


def build_lines(words: list[Word], tolerance: float = 0.5) -> list[list[Word]]:
    """Group words into lines by vertical position (ignores the engine's own line numbers)."""
    if not words:
        return []
    limit = tolerance * median(w.h for w in words)
    lines: list[list[Word]] = []
    for w in sorted(words, key=lambda w: w.cy):
        if lines and abs(w.cy - sum(x.cy for x in lines[-1]) / len(lines[-1])) <= limit:
            lines[-1].append(w)
        else:
            lines.append([w])
    return [sorted(line, key=lambda w: w.x0) for line in lines]


def build_phrases(line: list[Word], gap_factor: float = 1.5) -> list[Phrase]:
    """Merge neighbouring words into phrases; a wide gap starts a new phrase."""
    if not line:
        return []
    char_w = median(w.w / max(len(w.text), 1) for w in line)
    limit = gap_factor * char_w
    groups = [[line[0]]]
    for prev, cur in zip(line, line[1:]):
        if cur.x0 - prev.x1 > limit:
            groups.append([cur])
        else:
            groups[-1].append(cur)
    return [Phrase(tuple(g)) for g in groups]