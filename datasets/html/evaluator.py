import numpy as np

from components.evaluator import Evaluator
from common.registerable import Registrable
from datasets.conala.bleu_score import compute_bleu

@Registrable.register('html_evaluator')
class HtmlEvaluator(Evaluator):
    def __init__(self, transition_system=None, args=None):
        super(HtmlEvaluator, self).__init__()
        self.transition_system = transition_system
        self.default_metric = 'partial_compare'

    def evaluate_dataset(self, examples, decode_results, fast_mode=True):
        tx_sys = self.transition_system
        # Just assume fast mode for now
        example_asts = [e.tgt_ast for e in examples]
        target_asts = [hyp_list[0].tree if hyp_list else [] for hyp_list in decode_results]
        partial_compare_score = self.calc_partial_match(example_asts, target_asts) # small max_order while we have small datasets for now
        return { 'partial_compare': partial_compare_score }

    # Calculate average score for a dataset using custom partial tree compare
    def calc_partial_match(self, example_asts, target_asts):
        tx_sys = self.transition_system
        scores = []
        for idx, (ref_ast, hyp_ast) in enumerate(zip(example_asts, target_asts)):
            score = 0
            if hyp_ast:
                score = tx_sys.partial_compare(ref_ast, hyp_ast)
            scores.append(score)
        return np.average(scores)

    # Get blue score for a set of example -> target asts
    # def calc_bleu(self, asts1, asts2, max_order=4):
    #     tx_sys = self.transition_system
    #
    #     reference_code_strs = [tx_sys.ast_to_bleu_str(ast) for ast in asts1]
    #     hyp_code_strs = [tx_sys.ast_to_bleu_str(ast) for ast in asts2]
    #
    #     ref_tokens = [tokenize_html(html_str) for html_str in reference_code_strs]
    #     hyp_tokens = [tokenize_html(html_str) for html_str in hyp_code_strs]
    #
    #     # ref_tokens array of array (all examples, each tokenized)
    #     bleu_tup = compute_bleu([ref_tokens], hyp_tokens, max_order)
    #     bleu_score = bleu_tup[0]
    #     return bleu_score
