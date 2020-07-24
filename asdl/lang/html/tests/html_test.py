from tests.html_test_helpers import make_transition_system, CODE_STRS

def test_ast_to_code_and_back():
    transition_system = make_transition_system()

    code1 = '<video src="foo.com/vid.mp4" autoplay loop></video>'
    ast1 = transition_system.surface_code_to_ast(code1)
    code2 = transition_system.ast_to_surface_code(ast1)
    ast2 = transition_system.surface_code_to_ast(code2)
    assert transition_system.compare_ast(ast1, ast2)

def test_compare_ast_basic():
    transition_system = make_transition_system()

    code1 = CODE_STRS['empty_vid']
    code2 = CODE_STRS['empty_vid']

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    assert transition_system.compare_ast(ast1, ast2)

def test_compare_ast_order():
    transition_system = make_transition_system()

    code1 = CODE_STRS['equal_order_different'][0]
    code2 = CODE_STRS['equal_order_different'][1]

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    assert transition_system.compare_ast(ast1, ast2)

def test_compare_ast_negative():
    transition_system = make_transition_system()

    code1 = '<video src="bar" autoplay loop></video>'
    code2 = '<video autoplay src="foo.com/vid.mp4" loop></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    assert not transition_system.compare_ast(ast1, ast2)

def test_ast_to_bleu_str_basic():
    transition_system = make_transition_system()

    code1 = '<video></video>'
    code2 = '<video></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    bleu_str1 = transition_system.ast_to_bleu_str(ast1)
    bleu_str2 = transition_system.ast_to_bleu_str(ast2)

    assert bleu_str1 == bleu_str2

def test_ast_to_bleu_str_basic_negative():
    transition_system = make_transition_system()

    code1 = CODE_STRS['foo_src']
    code2 = '<video></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    bleu_str1 = transition_system.ast_to_bleu_str(ast1)
    bleu_str2 = transition_system.ast_to_bleu_str(ast2)

    assert bleu_str1 != bleu_str2

def test_ast_to_bleu_str_basic_order():
    transition_system = make_transition_system()

    code1 = '<video src="foo.com/vid.mp4" autoplay loop></video>'
    code2 = '<video autoplay src="foo.com/vid.mp4" loop></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    bleu_str1 = transition_system.ast_to_bleu_str(ast1)
    bleu_str2 = transition_system.ast_to_bleu_str(ast2)

    assert bleu_str1 == bleu_str2
