import pickle
import math
import nltk
from asdl.asdl import ASDLGrammar
from asdl.lang.html.transition_system import HtmlTransitionSystem
from asdl.transition_system import GenTokenAction
from components.action_info import get_action_infos
from components.dataset import Example
from components.vocab import Vocab, VocabEntry
from asdl.lang.py.py_utils import tokenize_code
import argparse
import os
import pdb

def make_train_data(data_name, max_query_len=70, vocab_freq_cutoff=10):
    english_file_path = 'datasets/html/dev-data/{0}/english.txt'.format(data_name)
    html_file_path = 'datasets/html/dev-data/{0}/html.txt'.format(data_name)
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

        # _TODO_ XXX do the sanity check on Hypothesis in django/dataset.py

        loaded_examples.append({'src_query_tokens': src_tokens,
                                'tgt_canonical_code': gold_source,
                                'tgt_ast': target_ast,
                                'tgt_actions': target_actions,
                                'raw_code': target_code}) # Do I need a str_map?

    num_examples = len(loaded_examples)
    if num_examples < 10:
        raise Exception("Require at least 10 examples but found ", num_examples)
    num_for_train = math.floor(num_examples * 0.9)
    num_for_dev = math.floor(num_examples * 0.05)
    num_for_test = num_examples - num_for_train - num_for_dev

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
        if 0 <= idx < num_for_train:
            train_examples.append(example)
        elif num_for_train <= idx < (num_for_train + num_for_dev):
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

def process_dataset(data_name):
    vocab_freq_cutoff = 15  # TODO: found the best cutoff threshold
    (train, dev, test), vocab = make_train_data(data_name=data_name, vocab_freq_cutoff=vocab_freq_cutoff)
    dump_dir = 'data/html/{0}'.format(data_name)
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)
    pickle.dump(train, open('data/html/{0}/train.bin'.format(data_name), 'w'))
    pickle.dump(dev, open('data/html/{0}/dev.bin'.format(data_name), 'w'))
    pickle.dump(test, open('data/html/{0}/test.bin'.format(data_name), 'w'))
    pickle.dump(vocab, open('data/html/{0}/vocab.freq%d.bin'.format(data_name) % vocab_freq_cutoff, 'w'))

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--data_name', default=0, type=str, help='Name of directory in datasets/html/dev-data to use')
    args = arg_parser.parse_args()
    process_dataset(args.data_name)
