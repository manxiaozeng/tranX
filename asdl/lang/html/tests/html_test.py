from asdl.lang.html.transition_system import HtmlTransitionSystem
from asdl.asdl import ASDLGrammar

def make_transition_system():
    asdl_text = open('asdl/lang/html/html_asdl.txt').read()
    grammar = ASDLGrammar.from_text(asdl_text)
    return HtmlTransitionSystem(grammar)

def test_ast_to_code_and_back():
    transition_system = make_transition_system()

    code1 = '<video src="foo.com/vid.mp4" autoplay loop></video>'
    ast1 = transition_system.surface_code_to_ast(code1)
    code2 = transition_system.ast_to_surface_code(ast1)
    ast2 = transition_system.surface_code_to_ast(code2)
    assert transition_system.compare_ast(ast1, ast2)

def test_compare_ast_basic():
    """Order of attrs irrelevant"""
    transition_system = make_transition_system()

    code1 = '<video></video>'
    code2 = '<video></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    assert transition_system.compare_ast(ast1, ast2)

def test_compare_ast_order():
    """Order of attrs irrelevant"""
    transition_system = make_transition_system()

    code1 = '<video src="foo.com/vid.mp4" autoplay loop></video>'
    code2 = '<video autoplay src="foo.com/vid.mp4" loop></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    assert transition_system.compare_ast(ast1, ast2)

def test_compare_ast_negative():
    """Order of attrs irrelevant"""
    transition_system = make_transition_system()

    code1 = '<video src="bar" autoplay loop></video>'
    code2 = '<video autoplay src="foo.com/vid.mp4" loop></video>'

    ast1 = transition_system.surface_code_to_ast(code1)
    ast2 = transition_system.surface_code_to_ast(code2)

    assert not transition_system.compare_ast(ast1, ast2)
