import re
from typing import List


# Unicode-aware word splitter for Spanish/English.
# - Includes accented letters and ñ/ü.
# - Optionally includes numbers and hyphens inside tokens.
# - Keeps simple English contractions like don't, it's as one token.


_LETTER_SET = "A-Za-zÁÉÍÓÚÜáéíóúüÑñ"


def _word_pattern_str(include_numbers: bool, keep_hyphens: bool) -> str:
    num = "0-9" if include_numbers else ""
    inner_connector = "-" if keep_hyphens else ""
    # Base token: letters (and optional numbers) with optional internal apostrophe or hyphen sequences.
    # Examples captured: palabras, palabra's, don't, auto-estima (if keep_hyphens=True), ISO9001 (if include_numbers=True)
    pattern = rf"[{_LETTER_SET}{num}]+(?:['{inner_connector}][{_LETTER_SET}{num}]+)*"
    return pattern


def get_word_regex(include_numbers: bool, keep_hyphens: bool) -> re.Pattern:
    """Return a compiled regex that matches a full word token under current options."""
    pat = _word_pattern_str(include_numbers=include_numbers, keep_hyphens=keep_hyphens)
    return re.compile(rf"^(?:{pat})$")


def get_punct_chars(keep_hyphens: bool) -> str:
    """Return the punctuation character class string used by tokenizer.
    If keep_hyphens is False, '-' is considered punctuation.
    """
    punct_chars = r"\?\!¡¿,\.;:…\(\)\[\]\{\}\"“”‘’«»—–_"
    if not keep_hyphens:
        punct_chars = "-" + punct_chars
    return punct_chars


def split_words(
    text: str,
    *,
    include_numbers: bool = True,
    keep_hyphens: bool = False,
    keep_punct: bool = False,
    attach_punct: str = "separate",  # 'separate' | 'left' | 'right' | 'auto'
    lower: bool = False,
    min_len: int = 1,
    unique: bool = False,
    normalize_ellipsis: bool = True,
) -> List[str]:
    if not isinstance(text, str):
        return []

    if normalize_ellipsis:
        # Replace sequences of three or more dots with '…' repeated.
        # e.g., '...' -> '…', '......' -> '……', '....' -> '….', leaving a remainder dot when not multiple of 3
        def _ell_sub(m: re.Match) -> str:
            dots = len(m.group(0))
            return "…" * (dots // 3) + "." * (dots % 3)

        text = re.sub(r"\.{3,}", _ell_sub, text)

    word_pat_str = _word_pattern_str(include_numbers=include_numbers, keep_hyphens=keep_hyphens)
    word_regex = re.compile(rf"^(?:{word_pat_str})$")

    if not keep_punct:
        # Simple path: only words
        tokens = re.findall(word_pat_str, text)

        if lower:
            tokens = [t.lower() for t in tokens]

        if min_len > 1:
            tokens = [t for t in tokens if len(t) >= min_len]

        if unique:
            seen = set()
            ordered: List[str] = []
            for t in tokens:
                if t not in seen:
                    seen.add(t)
                    ordered.append(t)
            tokens = ordered

        return tokens

    # keep_punct=True: include punctuation tokens as separate items, preserving order
    # Punctuation set includes Spanish inverted marks and common punctuation.
    punct_chars = r"\?\!¡¿,\.;:…\(\)\[\]\{\}\"“”‘’«»—–_"
    # If hyphens are not kept inside words, treat '-' as punctuation
    if not keep_hyphens:
        punct_chars = "-" + punct_chars

    combined = re.compile(rf"{word_pat_str}|[{punct_chars}]")

    out: List[str] = []
    for m in combined.finditer(text):
        tok = m.group(0)
        is_word = bool(word_regex.match(tok))
        if is_word:
            if lower:
                tok = tok.lower()
            if len(tok) < min_len:
                continue
        # Punctuation bypasses min_len filtering
        out.append(tok)

    # Optionally attach punctuation to neighboring words
    if attach_punct not in {"separate", "left", "right", "auto"}:
        attach_punct = "separate"

    if keep_punct and attach_punct != "separate":
        opening = {"¿", "¡", "(", "[", "{", "«", "“", "‘"}
        closing = {"?", "!", ")", "]", "}", "»", "”", "’", ",", ".", ";", ":", "…"}
        dashlike = {"—", "–", "_"}
        hyphen = {"-"}

        def is_word_token(t: str) -> bool:
            return bool(word_regex.match(t))

        merged: List[str] = []
        i = 0
        while i < len(out):
            t = out[i]
            if is_word_token(t):
                merged.append(t)
                i += 1
                continue

            # It's punctuation
            if attach_punct == "left":
                if merged and is_word_token(merged[-1]):
                    merged[-1] = merged[-1] + t
                else:
                    merged.append(t)
                i += 1
                continue
            if attach_punct == "right":
                nxt = out[i + 1] if i + 1 < len(out) else None
                if nxt is not None and is_word_token(nxt):
                    merged.append(t + nxt)
                    i += 2
                else:
                    merged.append(t)
                    i += 1
                continue
            # auto mode
            if attach_punct == "auto":
                if t in opening or t in dashlike or (t in hyphen and not keep_hyphens):
                    nxt = out[i + 1] if i + 1 < len(out) else None
                    if nxt is not None and is_word_token(nxt):
                        merged.append(t + nxt)
                        i += 2
                    else:
                        merged.append(t)
                        i += 1
                elif t in closing:
                    if merged and is_word_token(merged[-1]):
                        merged[-1] = merged[-1] + t
                    else:
                        merged.append(t)
                    i += 1
                else:
                    # Unknown punctuation, keep separate
                    merged.append(t)
                    i += 1
                continue

            # Fallback (shouldn't hit): keep as-is
            merged.append(t)
            i += 1

        out = merged

    if unique:
        seen = set()
        ordered2: List[str] = []
        for t in out:
            if t not in seen:
                seen.add(t)
                ordered2.append(t)
        out = ordered2

    return out
