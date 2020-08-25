from __future__ import print_function
import six
import argparse
import sys
from flask import Flask, url_for, jsonify, render_template
import json

from components.standalone_parser import StandaloneParser

print("Making app")
app = Flask(__name__)
parsers = dict()

def get_app():
    return app

def init_arg_parser():
    arg_parser = argparse.ArgumentParser()
    return arg_parser


@app.route("/")
def default():
    return render_template('lang-html.html') # Basically the same as default.html but just shows HTML as a lang

@app.route('/parse/<dataset>/<utterance>', methods=['GET'])
def parse(utterance, dataset):

    parser = parsers[dataset]

    if six.PY2:
        utterance = utterance.encode('utf-8', 'ignore')

    hypotheses = parser.parse(utterance, debug=True)

    responses = dict()
    responses['hypotheses'] = []

    for hyp_id, hyp in enumerate(hypotheses):
        print('------------------ Hypothesis %d ------------------' % hyp_id)
        print(hyp.code)
        print(hyp.tree.to_string())
        # print('Actions:')
        # for action_t in hyp.action_infos:
        #     print(action_t)

        actions_repr = [action.__repr__(True) for action in hyp.action_infos]

        hyp_entry = dict(id=hyp_id + 1,
                         value=hyp.code,
                         tree_repr=hyp.tree.to_string(),
                         score=hyp.score,
                         actions=actions_repr)

        responses['hypotheses'].append(hyp_entry)

    return jsonify(responses)

@app.route("/ping")
def ping():
    return "pong"

# args = init_arg_parser().parse_args()
config_dict = json.load(open("server/html-config.json"))

for parser_id, config in config_dict.items():
    # _TODO_ load model from previous floyd run
    parser = StandaloneParser(parser_name=config['parser'],
                              model_path=config['model_path'],
                              example_processor_name=config['example_processor'],
                              beam_size=config['beam_size'],
                              cuda=False) # _TODO_ suppport cuda

    parsers[parser_id] = parser
