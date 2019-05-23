import pickle
import nltk
from asdl.asdl import ASDLGrammar
from asdl.lang.html.transition_system import HtmlTransitionSystem
from asdl.transition_system import GenTokenAction
from components.action_info import get_action_infos
from components.dataset import Example
from components.vocab import Vocab, VocabEntry
from asdl.lang.py.py_utils import tokenize_code

def make_train_data(max_query_len=70, vocab_freq_cutoff=10):
    english_file_path = 'datasets/html/dev-data/english.txt'
    html_file_path = 'datasets/html/dev-data/html.txt'
    asdl_file_path = 'asdl/lang/html/html_asdl.txt'

    asdl_text = open(asdl_file_path).read()
    grammar = ASDLGrammar.from_text(asdl_text)
    transition_system = HtmlTransitionSystem(grammar)

    loaded_examples = []
    examples_enum = enumerate(zip(open(english_file_path), open(html_file_path)))
    for idx, (src_english, target_code) in examples_enum:
        src_english = src_english.strip()
        target_code = target_code.strip()
        # TODO In django dataset they do a fancy string replacement in canonicalize_query
        src_tokens = nltk.word_tokenize(src_english)

        target_ast = transition_system.surface_code_to_ast(target_code)
        gold_source = transition_system.ast_to_surface_code(target_ast)
        target_actions = transition_system.get_actions(target_ast)

        # TODO XXX do the sanity check on Hypothesis in django/dataset.py

        loaded_examples.append({'src_query_tokens': src_tokens,
                                'tgt_canonical_code': gold_source,
                                'tgt_ast': target_ast,
                                'tgt_actions': target_actions,
                                'raw_code': target_code}) # Do I need a str_map?

    train_examples = []
    dev_examples = []
    test_examples = []
    for idx, e in enumerate(loaded_examples):
        example = Example(idx=idx,
                          src_sent=e['src_query_tokens'][:max_query_len],
                          tgt_actions=get_action_infos(e['src_query_tokens'], e['tgt_actions']),
                          tgt_code=e['tgt_canonical_code'],
                          tgt_ast=e['tgt_ast'],
                          meta={'raw_code': e['raw_code']})

        # train, valid, test split
        if 0 <= idx < 4:
            train_examples.append(example)
        elif 4 <= idx < 6:
            dev_examples.append(example)
        else:
            test_examples.append(example)

    src_vocab = VocabEntry.from_corpus([e.src_sent for e in train_examples], size=5000, freq_cutoff=vocab_freq_cutoff)
    primitive_tokens = [map(lambda a: a.action.token,
                        filter(lambda a: isinstance(a.action, GenTokenAction), e.tgt_actions))
                        for e in train_examples]
    primitive_vocab = VocabEntry.from_corpus(primitive_tokens, size=5000, freq_cutoff=vocab_freq_cutoff)

    # Just using the python tokenize_code for now.
    code_tokens = [tokenize_code(e.tgt_code, mode='decoder') for e in train_examples]
    code_vocab = VocabEntry.from_corpus(code_tokens, size=5000, freq_cutoff=vocab_freq_cutoff)

    vocab = Vocab(source=src_vocab, primitive=primitive_vocab, code=code_vocab)

    return (train_examples, dev_examples, test_examples), vocab

def process_dataset():
    vocab_freq_cutoff = 15  # TODO: found the best cutoff threshold
    (train, dev, test), vocab = make_train_data(vocab_freq_cutoff=vocab_freq_cutoff)
    pickle.dump(train, open('data/html/train.bin', 'w'))
    pickle.dump(dev, open('data/html/dev.bin', 'w'))
    pickle.dump(test, open('data/html/test.bin', 'w'))
    pickle.dump(vocab, open('data/html/vocab.freq%d.bin' % vocab_freq_cutoff, 'w'))

if __name__ == '__main__':
    process_dataset()
