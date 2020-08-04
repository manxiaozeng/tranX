from datasets.html.dataset import tokenize_english_utterance
import nltk
from nltk.tokenize import TweetTokenizer

def test_tokenize_basic():
    str = "hello"
    res = tokenize_english_utterance(str)
    assert res == ["hello"]

def test_tokenize_whitespace():
    str = " hello   there             foo  "
    res = tokenize_english_utterance(str)
    assert res == ["hello", "there", "foo"]

def test_tokenize_single_quote():
    str = "hello'"
    res = tokenize_english_utterance(str)
    assert res == ["hello'"]

def test_tokenize_remove_quotes():
    str = "'hello'"
    res = tokenize_english_utterance(str)
    assert res == ["hello"]

# TODO better tokenize this
def test_tokenize_no_space_after_sentence():
    str = 'url model.mp4".The poster'
    res = tokenize_english_utterance(str)
    # that single quote after model.mp4 wont get removed
    # AND the 'The' gets tacked onto the token instead of separted
    # nltk.word_tokenize does a pretty good job on this
    assert res == ["url", 'model.mp4".The', "poster"]

def test_tokenize_percents():
    str = "width of 25%"
    res = tokenize_english_utterance(str)
    assert res == ["width", "of", "25%"]

def test_tokenize_percent_with_punctuation():
    str = "width of 25%."
    res = tokenize_english_utterance(str)
    assert res == ["width", "of", "25%"]

def test_multiple_sentences():
    str = "hi there. i am jon."
    res = tokenize_english_utterance(str)
    assert res == ["hi", "there", "i", "am", "jon"]
    debug_str(str)

def test_tokenize_url():
    str = 'the url "http://duarte-garcia.biz/shoulder.mp4" and'
    res = tokenize_english_utterance(str)
    assert res == ['the', 'url', 'http://duarte-garcia.biz/shoulder.mp4', 'and']

def debug_str(str):
    # Try printing some other representations
    print("\n")
    print("nltk.word_tokenize: ")
    print(nltk.word_tokenize(str))
    tknzr = TweetTokenizer()
    print("TweetTokenizer: ")
    print(tknzr.tokenize(str))
