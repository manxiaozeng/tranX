from asdl.asdl import ASDLGrammar
from asdl.lang.html.transition_system import HtmlTransitionSystem

def make_transition_system():
    asdl_text = open('asdl/lang/html/html_asdl.txt').read()
    grammar = ASDLGrammar.from_text(asdl_text)
    return HtmlTransitionSystem(grammar)

CODE_STRS = {
 'empty_vid': '<video></video>',
 'equal_order_different': [
    '<video src="foo.com/vid.mp4" autoplay loop></video>',
    '<video autoplay src="foo.com/vid.mp4" loop></video>'
 ],
 'foo_src': '<video src="foo.mp4"></video>'
}
