from components.evaluator import Evaluator
from common.registerable import Registrable
import ast
import astor


@Registrable.register('html_evaluator')
class HtmlEvaluator(Evaluator):
    def __init__(self, transition_system=None, args=None):
        super(HtmlEvaluator, self).__init__()
        self.transition_system = transition_system

    def is_hyp_correct(self, example, hyp):
        # TODO XXX
        # See django/evaluator.py
        return True
