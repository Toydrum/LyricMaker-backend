def syllable_divider(word: str):
    """
    Divide a word into syllables using Spanish-oriented heuristics
    (works reasonably for simple English words too).

    Rules covered (simplified):
    - Vowel nuclei include diphthongs/triphthongs with weak vowels (i, u, ü).
    - One consonant between nuclei goes with the next syllable (V-CV).
    - Two consonants between nuclei: if they form a permissible onset cluster
      (pr, pl, br, bl, tr, dr, cr, cl, gr, gl, fr, fl, ch, ll, rr), keep both
      for the next syllable; otherwise split between them.
    - Three consonants: split after the first unless the last two form an
      allowed onset cluster (then split VC1-C2C3).

    This is a heuristic, not a full phonological parser, but it yields
    expected results for common cases like 'palabra' -> ['pa', 'la', 'bra'].
    """
    if not word:
        return []

    # Define vowel sets (Spanish), include accents and dieresis.
    VOWELS = set("aeiouáéíóúüAEIOUÁÉÍÓÚÜ")
    STRONG = set("aáeéoóAÁEÉOÓ")
    WEAK = set("iíuúüIÍUÚÜ")
    ACCENTED = set("áéíóúÁÉÍÓÚ")

    # Allowed onset clusters in Spanish (approx.). Include digraphs as units.
    ALLOWED_CLUSTERS = {
        "pr", "pl", "br", "bl", "tr", "dr",
        "cr", "cl", "gr", "gl", "fr", "fl",
        "ch", "ll", "rr",
    }

    def is_vowel(i: int) -> bool:
        c = word[i]
        return c in VOWELS

    def is_strong(c: str) -> bool:
        return c in STRONG

    def is_weak(c: str) -> bool:
        return c in WEAK

    def is_accented(c: str) -> bool:
        return c in ACCENTED

    def nucleus_end(i: int) -> int:
        """Return the index AFTER the vowel nucleus starting at i.
        Handles diphthongs/triphthongs heuristically.
        """
        # Assume word[i] is a vowel (use with care)
        j = i + 1
        # Helper to fetch char safely
        def ch(k):
            return word[k] if 0 <= k < len(word) else ""

        v1 = ch(i)
        v2 = ch(i + 1)
        v3 = ch(i + 2)

        def is_y_final_vowel(k: int) -> bool:
            c = ch(k)
            return c.lower() == 'y' and k == len(word) - 1 and k > 0 and ch(k - 1) in VOWELS

        # Handle 'y' as a weak vowel only in ending diphthongs like 'buey'.
        def is_vowel_like(k: int) -> bool:
            c = ch(k)
            if not c:
                return False
            if c in VOWELS:
                return True
            if c.lower() == 'y' and k == len(word) - 1 and k > 0 and ch(k - 1) in VOWELS:
                return True
            return False

        # Determine triphthong: weak (no accent) + strong + weak (no accent)
        if is_vowel_like(i) and is_vowel_like(i + 1) and is_vowel_like(i + 2):
            # Standard triphthong weak + strong + weak (no accents)
            if is_weak(v1) and not is_accented(v1) and is_strong(v2) and is_weak(v3) and not is_accented(v3):
                return i + 3
            # Special-case: weak + strong + final 'y' acting as weak (e.g., 'buey')
            if is_weak(v1) and not is_accented(v1) and is_strong(v2) and is_y_final_vowel(i + 2):
                return i + 3

        # Determine diphthong cases (order matters)
        if is_vowel_like(i) and is_vowel_like(i + 1):
            # Two weak vowels together (iu/ui) without accents -> diphthong
            if is_weak(v1) and is_weak(v2) and not is_accented(v1) and not is_accented(v2):
                return i + 2
            # strong + weak (weak not accented) -> diphthong
            if is_strong(v1) and is_weak(v2) and not is_accented(v2):
                return i + 2
            # weak (not accented) + strong -> diphthong
            if is_weak(v1) and not is_accented(v1) and is_strong(v2):
                return i + 2
            # Special-cases with final 'y' acting as weak: 'oy', 'ey', 'ay', 'uy', 'iy'
            if is_strong(v1) and is_y_final_vowel(i + 1):
                return i + 2
            if is_weak(v1) and not is_accented(v1) and is_y_final_vowel(i + 1):
                return i + 2

        # Default: single vowel nucleus
        return j

    # Collect nuclei as (start, end) indices
    nuclei = []
    i = 0
    n = len(word)
    while i < n:
        if is_vowel(i):
            ne = nucleus_end(i)
            nuclei.append((i, ne))
            i = ne
        else:
            i += 1

    if not nuclei:
        return [word]  # No vowels, return the whole word as one syllable

    syllables = []
    # Start of the current syllable
    start_idx = 0

    for idx in range(len(nuclei) - 1):
        cur_start, cur_end = nuclei[idx]
        next_start, _ = nuclei[idx + 1]

        # Consonant sequence between nuclei
        cons_start = cur_end
        cons_end = next_start
        cons_seq = word[cons_start:cons_end]

        # Count consonants (consider digraphs ch/ll/rr as single units)
        units = []
        k = 0
        while k < len(cons_seq):
            two = cons_seq[k:k + 2].lower()
            if two in {"ch", "ll", "rr"}:
                units.append(cons_seq[k:k + 2])
                k += 2
            else:
                units.append(cons_seq[k])
                k += 1

        klen = len(units)

        # Decide the split point according to Spanish rules
        split_at = None  # absolute index in word where current syllable ends
        if klen == 0:
            # V V -> everything stays, split just before next nucleus (V - V)
            split_at = cons_start
        elif klen == 1:
            # V C V -> V - CV (consonant goes with next syllable)
            split_at = cons_start
        elif klen == 2:
            pair = (units[0] + units[1]).lower()
            if pair in ALLOWED_CLUSTERS:
                # V - CCV
                split_at = cons_start
            else:
                # VC - CV (split between consonants)
                split_at = cons_start + len(units[0])
        else:
            # klen >= 3
            last_two = (units[-2] + units[-1]).lower()
            if last_two in ALLOWED_CLUSTERS:
                # VC1 - C2C3V (keep last two as onset)
                split_at = cons_start + sum(len(u) for u in units[:-2])
            else:
                # VC1C2 - C3V (fallback)
                split_at = cons_start + sum(len(u) for u in units[:-1])

        syllables.append(word[start_idx:split_at])
        start_idx = split_at

    # Add the last syllable (from last split to end)
    syllables.append(word[start_idx:])

    # Filter out empty fragments if any (can happen with leading vowels logic)
    syllables = [s for s in syllables if s]

    return syllables

# Alias para mantener compatibilidad con importaciones existentes
def divide_into_syllables(word):
    return syllable_divider(word)

def divide_words(words):
    return {word: syllable_divider(word) for word in words}