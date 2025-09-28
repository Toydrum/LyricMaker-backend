def divide_into_syllables(word):
    vowels = "aeiouy"
    syllables = []
    current_syllable = ""
    
    for char in word:
        if char.lower() in vowels:
            if current_syllable and current_syllable[-1] not in vowels:
                syllables.append(current_syllable)
                current_syllable = char
            else:
                current_syllable += char
        else:
            current_syllable += char
    
    if current_syllable:
        syllables.append(current_syllable)
    
    return syllables

def is_vowel(char):
    return char.lower() in "aeiouy"