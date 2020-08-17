from common.registerable import Registrable
from datasets.utils import ExampleProcessor
from datasets.html.dataset import tokenize_english_utterance

@Registrable.register('html_example_processor')
class HtmlExampleProcessor(ExampleProcessor):
    def __init__(self, transition_system):
        self.transition_system = transition_system

    def pre_process_utterance(self, utterance):
        return tokenize_english_utterance(utterance), {}

    def post_process_hypothesis(self, hyp, meta_info, utterance=None):
        code = self.transition_system.ast_to_surface_code(hyp.tree)
        hyp.code = code
