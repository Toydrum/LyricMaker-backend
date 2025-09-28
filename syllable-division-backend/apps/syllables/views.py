from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
import re

from apps.syllables.services.syllable_divider import divide_into_syllables
from apps.syllables.services.word_splitter import split_words, get_word_regex, get_punct_chars

@csrf_exempt
def divide_syllables(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST con JSON {'word': '...'}")
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON inválido")

    word = data.get("word")
    if not isinstance(word, str) or not word:
        return HttpResponseBadRequest("El campo 'word' es requerido")

    return JsonResponse({"word": word, "syllables": divide_into_syllables(word)})


@csrf_exempt
def split_text(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST con JSON {'text': '...'}")
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON inválido")

    text = data.get("text")
    if not isinstance(text, str) or not text:
        return HttpResponseBadRequest("El campo 'text' es requerido")

    # Optional flags
    include_numbers = bool(data.get("include_numbers", True))
    keep_hyphens = bool(data.get("keep_hyphens", False))
    keep_punct = bool(data.get("keep_punct", True))
    lower = bool(data.get("lower", False))
    min_len = int(data.get("min_len", 1))
    unique = bool(data.get("unique", False))
    attach_punct = str(data.get("attach_punct", "separate"))
    normalize_ellipsis = bool(data.get("normalize_ellipsis", True))

    tokens = split_words(
        text,
        include_numbers=include_numbers,
        keep_hyphens=keep_hyphens,
        keep_punct=keep_punct,
        lower=lower,
        min_len=min_len,
        unique=unique,
        attach_punct=attach_punct,
        normalize_ellipsis=normalize_ellipsis,
    )

    return JsonResponse({
        "text": text,
        "tokens": tokens,
        "count": len(tokens),
        "options": {
            "include_numbers": include_numbers,
            "keep_hyphens": keep_hyphens,
            "keep_punct": keep_punct,
            "lower": lower,
            "min_len": min_len,
            "unique": unique,
            "attach_punct": attach_punct,
            "normalize_ellipsis": normalize_ellipsis,
        },
    })


@csrf_exempt
def split_and_syllabify(request):
    """Split the text and syllabify only word tokens (skip punctuation).
    Body JSON:
    {
      "text": "...",
      ... same options as split_text ...
    }
    Returns a list of items: { type: 'word'|'punct', token: str, [syllables]: [...] }
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST con JSON {'text': '...'}")
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("JSON inválido")

    text = data.get("text")
    if not isinstance(text, str) or not text:
        return HttpResponseBadRequest("El campo 'text' es requerido")

    include_numbers = bool(data.get("include_numbers", True))
    keep_hyphens = bool(data.get("keep_hyphens", False))
    keep_punct = bool(data.get("keep_punct", True))  # default True for this endpoint
    attach_punct = str(data.get("attach_punct", "auto"))
    normalize_ellipsis = bool(data.get("normalize_ellipsis", True))
    lower = bool(data.get("lower", False))
    min_len = int(data.get("min_len", 1))
    unique = bool(data.get("unique", False))

    tokens = split_words(
        text,
        include_numbers=include_numbers,
        keep_hyphens=keep_hyphens,
        keep_punct=keep_punct,
        attach_punct=attach_punct,
        lower=lower,
        min_len=min_len,
        unique=unique,
        normalize_ellipsis=normalize_ellipsis,
    )

    # Classify tokens and syllabify only words (strip punctuation for syllabifier)
    word_re = get_word_regex(include_numbers=include_numbers, keep_hyphens=keep_hyphens)
    punct_class = get_punct_chars(keep_hyphens=keep_hyphens)
    # Define opening/closing sets for item tagging and counts
    opening = {"¿", "¡", "(", "[", "{", "«", "“", "‘"}
    closing = {"?", "!", ")", "]", "}", "»", "”", "’", ",", ".", ";", ":", "…"}
    if not keep_hyphens:
        closing = set(list(closing) + ["-"])
    items = []
    syllables_total = 0
    for tok in tokens:
        # Split token into prefix punctuation, core, and suffix punctuation
        pre_match = re.match(rf'^[{punct_class}]+', tok)
        suf_match = re.search(rf'[{punct_class}]+$', tok)
        prefix = pre_match.group(0) if pre_match else ""
        suffix = suf_match.group(0) if suf_match else ""

        core_start = len(prefix)
        core_end = len(tok) - len(suffix)
        core = tok[core_start:core_end] if core_end >= core_start else ""
        core_no_hyphen = core.replace("-", "")

        def push_punct_chars(punc: str):
            for ch in punc:
                if ch in opening:
                    ptype = "punct_open"
                elif ch in closing:
                    ptype = "punct_close"
                else:
                    ptype = "punct"
                items.append({"type": ptype, "token": ch})

        # If the core is a word (after removing hyphens), output prefix punct(s), word, then suffix punct(s)
        if core and (word_re.match(core) or word_re.match(core_no_hyphen)):
            if prefix:
                push_punct_chars(prefix)
            sylls = divide_into_syllables(core_no_hyphen)
            items.append({
                "type": "word",
                "token": core_no_hyphen,
                "syllables": sylls
            })
            syllables_total += len(sylls)
            if suffix:
                push_punct_chars(suffix)
        else:
            # Entire token considered punctuation or non-word
            if tok:
                push_punct_chars(tok)

    # Count punctuation in the original text to capture opening signs even if attached
    punct_open_count = sum(1 for ch in text if ch in opening)
    punct_close_count = sum(1 for ch in text if ch in closing)
    punct_total_count = punct_open_count + punct_close_count

    return JsonResponse({
        "text": text,
        "items": items,
        "counts": {
            "total": len(items),
            "words": sum(1 for it in items if it["type"] == "word"),
            "punct": sum(1 for it in items if it["type"] in {"punct", "punct_open", "punct_close"}),
            "punct_open": punct_open_count,
            "punct_close": punct_close_count,
            "punct_total": punct_total_count,
            "syllables_total": syllables_total,
        },
        "options": {
            "include_numbers": include_numbers,
            "keep_hyphens": keep_hyphens,
            "keep_punct": keep_punct,
            "attach_punct": attach_punct,
            "normalize_ellipsis": normalize_ellipsis,
            "lower": lower,
            "min_len": min_len,
            "unique": unique,
        },
    })