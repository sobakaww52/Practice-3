def mask_word(word: str, guessed_letters: set) -> str:
    return ''.join(letter if letter in guessed_letters else '\u25A0' for letter in word)

def hearts(count: int) -> str:
    return '♥' * count
