from common.registerable import Registrable
from datasets.utils import ExampleProcessor

# TODO Just trying to get server.py working, this is basically a stub
@Registrable.register('html_example_processor')
class HtmlExampleProcessor(ExampleProcessor):
    def __init__(self, transition_system):
        self.transition_system = transition_system

    def pre_process_utterance(self, utterance):
        return utterance, {}

    def post_process_hypothesis(self, hyp, meta_info, utterance=None):
        print("skipping")
