from tests.html_test_helpers import make_transition_system, CODE_STRS
# this import * is just to prevent the circular dependency
# between HtmlEvaluator<->Evaluator in the import below
from components import *
from datasets.html.evaluator import HtmlEvaluator

def test_partial_compare_basic():
    code1 = "<video></video>"
    code2 = "<video></video>"
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    assert score == 1

def test_partial_compare_same_bool():
    code1 = "<video muted></video>"
    code2 = "<video muted></video>"
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    assert score == 1

def test_partial_compare_bool_wrong():
    code1 = "<video muted></video>"
    code2 = "<video></video>"
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    assert score < 0.5 # 1 / 3


def test_partial_compare_one_field():
    code1 = '<video src="foo"></video>'
    code2 = '<video src="foo"></video>'
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    assert score == 1

def test_partial_compare_field_same_value_different():
    code1 = '<video src="foo"></video>'
    code2 = '<video src="WRONG"></video>'
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    assert score < 1
    assert score > 0.5

def test_partial_compare_missing_field():
    code1 = '<video src="foo"></video>'
    code2 = '<video></video>'
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    # Gets 'video' but misses src and src value
    assert score < 0.5


def test_partial_compare_strings_get_exra_points():
    # Getting `src` correct will give extra weight
    code1 = '<video autoplay src="foo"></video>'
    code2 = '<video src="foo"></video>'
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    # Gets 'video' but misses src and src value
    assert score > 0.7

def test_partial_compare_bad_extra_field():
    code1 = '<video></video>'
    code2 = '<video src="foo"></video>'
    tx_sys = make_transition_system()
    ast1 = tx_sys.surface_code_to_ast(code1)
    ast2 = tx_sys.surface_code_to_ast(code2)
    score = tx_sys.partial_compare(ast1, ast2)
    # Gets 'video' but misses src and src value
    assert score == 0.5 # Gets 'video', penalized for src
