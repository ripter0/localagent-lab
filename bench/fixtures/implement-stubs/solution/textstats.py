import re


def count_sentences(text):
    """Number of sentences. A sentence ends with '.', '!' or '?'. Empty pieces don't count."""
    return len([p for p in re.split(r"[.!?]", text) if p.strip()])


def _words(text):
    return re.findall(r"[A-Za-zÀ-ÿ]+", text)


def longest_word(text):
    """The longest word (letters only, punctuation removed). On a tie, the first one. '' if none."""
    return max(_words(text), key=len, default="")


def average_word_length(text):
    """Average length of the words (letters only), rounded to 2 decimals. 0.0 if there are no words."""
    words = _words(text)
    return round(sum(map(len, words)) / len(words), 2) if words else 0.0
