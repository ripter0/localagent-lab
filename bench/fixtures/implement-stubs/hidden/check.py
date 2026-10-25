from textstats import average_word_length, count_sentences, longest_word

assert count_sentences("Hi. How are you?! Fine") == 3, count_sentences("Hi. How are you?! Fine")
assert count_sentences("") == 0
assert count_sentences("One. Two. Three.") == 3
assert count_sentences("Wait... what?") == 2
assert longest_word("I love Python, really!") == "Python"
assert longest_word("aa bb") == "aa"
assert longest_word("") == ""
assert average_word_length("hi there") == 3.5
assert average_word_length("a bb ccc!") == 2.0
assert average_word_length("") == 0.0
print("OK")
