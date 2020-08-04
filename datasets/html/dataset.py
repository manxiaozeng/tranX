# coding=utf-8
import pickle
import math
from components.action_info import get_action_infos
from asdl.asdl import ASDLGrammar
from asdl.lang.html.transition_system import HtmlTransitionSystem
from asdl.transition_system import GenTokenAction
from components.dataset import Example
from components.vocab import Vocab, VocabEntry
from asdl.lang.py.py_utils import tokenize_code
import argparse
import os
import re
# For utf-8 encoding dance
import io
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb
from bs4 import BeautifulSoup
from random import shuffle

SRC_ENCODING = 'UTF-8'

# Assumes we are dealing with a single tag
def tokenize_html(html_str):
    soup = BeautifulSoup(html_str, 'html5lib')
    el = soup.body.contents[0]
    tokens = [el.name]
    for k,v in el.attrs.iteritems():
        tokens.append(k)
        if v != None and v != '':
            tokens.append(v)
    return tokens


QUOTED_TOKEN_RE = re.compile(r"(?P<quote>''|[`'\"])(?P<string>.*?)(?P=quote)")
# My custom tokenizer.
# TODO Try using nltk selectively (doesnt handle file names & punctuation very well)
def tokenize_english_utterance(utterance):
    # Remove white space
    str = utterance.strip()

    # Since this is raw user input,
    # exchange 'fancy' quotes (like from MS machines) for normal ones
    str = str.replace("“", '"').replace("”", '"')

    split = str.split(' ')
    res = []
    for token in split:
        # replace quoted values with the unquoted version so its
        # easier for the model to copy the tokens
        match = QUOTED_TOKEN_RE.match(token)
        value = token
        if match:
            # its a quoted value, replace with just the value w/o the quotes
            # if token is '"foo"' then match[1] is 'foo'
            value = match.groups()[1]
        else:
            # Remove punctuation (but keep things like '%')
            # _TODO_ should this instead add the punctuation as a separate
            # token so the model can see the punctuation?
            value = token.strip(",.;")
        res.append(value)
    res = filter(None, res)
    return res

def make_train_data(data_name, max_query_len=70, vocab_freq_cutoff=10):
    english_file_path = 'datasets/html/dev-data/{0}/english.txt'.format(data_name)
    html_file_path = 'datasets/html/dev-data/{0}/html.txt'.format(data_name)
    asdl_file_path = 'asdl/lang/html/html_asdl.txt'

    asdl_text = open(asdl_file_path).read()
    grammar = ASDLGrammar.from_text(asdl_text)
    transition_system = HtmlTransitionSystem(grammar)

    loaded_examples = []
    examples = zip(io.open(english_file_path, encoding=SRC_ENCODING), io.open(html_file_path, encoding=SRC_ENCODING))
    shuffle(examples) # randomize order so file order doesnt impact distrubtion across test/train/dev sets
    for idx, (src_english, target_code) in enumerate(examples):
        target_code = target_code.strip()
        src_tokens = tokenize_english_utterance(src_english)
        # print("src_english: {}", src_english)
        # print("src_tokens: {}", src_tokens)

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

    # TODO Why size=5000?
    src_vocab = VocabEntry.from_corpus([e.src_sent for e in train_examples], size=50000, freq_cutoff=vocab_freq_cutoff)
    primitive_tokens = [map(lambda a: a.action.token,
                        filter(lambda a: isinstance(a.action, GenTokenAction), e.tgt_actions))
                        for e in train_examples]
    primitive_vocab = VocabEntry.from_corpus(primitive_tokens, size=50000, freq_cutoff=vocab_freq_cutoff)

    code_tokens = [tokenize_html(e.tgt_code) for e in train_examples]
    code_vocab = VocabEntry.from_corpus(code_tokens, size=50000, freq_cutoff=vocab_freq_cutoff)

    vocab = Vocab(source=src_vocab, primitive=primitive_vocab, code=code_vocab)

    return (train_examples, dev_examples, test_examples), vocab

def process_dataset(data_name):
    vocab_freq_cutoff = 15 # _TODO_ how to use this properly?
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
