from common.registerable import Registrable
from datasets.utils import ExampleProcessor

@Registrable.register('html_example_processor')
class HtmlExampleProcessor(ExampleProcessor):
    def __init__(self, transition_system):
        self.transition_system = transition_system

    def pre_process_utterance(self, utterance):
        return utterance.split(' '), {}

    def post_process_hypothesis(self, hyp, meta_info, utterance=None):
        code = self.transition_system.ast_to_surface_code(hyp.tree)
        hyp.code = code
