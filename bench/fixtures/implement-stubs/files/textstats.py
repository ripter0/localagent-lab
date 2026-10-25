def count_sentences(text):
    """Number of sentences. A sentence ends with '.', '!' or '?'. Empty pieces don't count.

    count_sentences("Hi. How are you?! Fine") == 3   ("Fine" counts: text after the last mark)
    count_sentences("") == 0
    """
    raise NotImplementedError


def longest_word(text):
    """The longest word (letters only, punctuation removed). On a tie, the first one. '' if none.

    longest_word("I love Python, really!") == "Python"
    """
    raise NotImplementedError


def average_word_length(text):
    """Average length of the words (letters only), rounded to 2 decimals. 0.0 if there are no words.

    average_word_length("hi there") == 3.5
    """
    raise NotImplementedError
