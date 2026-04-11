"""Pronunciation substitution map for Iris TTS."""

SUBSTITUTIONS = {
    "Ka\'tuar\'el": "Kah twar ell",
    "ka\'tuar\'el": "Kah twar ell",
    "Ka\'tuar\'el\'s": "Kah twar ell\'s",
    "Adriaan": "Ah-dree-ahn",
    "adriaan": "Ah-dree-ahn",
    "Adge": "Ahdj",
    "adge": "Ahdj",
    "Seraphe": "Sarah-fee",
    "seraphe": "Sarah-fee",
    "Mythos": "Mythoase",
    "mythos": "Mythoase",
}

def apply(text):
    text = " ".join(text.split())
    for word, phonetic in SUBSTITUTIONS.items():
        text = text.replace(word, phonetic)
    return text
