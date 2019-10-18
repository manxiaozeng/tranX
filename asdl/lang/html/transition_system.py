# coding=utf-8
import pdb
import pickle
import ast
from bs4 import BeautifulSoup
from asdl.transition_system import TransitionSystem, GenTokenAction
from asdl.asdl_ast import RealizedField, AbstractSyntaxTree
from asdl.asdl import ASDLGrammar
from common.registerable import Registrable
from asdl.hypothesis import Hypothesis

@Registrable.register('html')
class HtmlTransitionSystem(TransitionSystem):
    def compare_ast(self, hyp_ast, ref_ast):
        code1 = self.ast_to_surface_code(hyp_ast)
        code2 = self.ast_to_surface_code(ref_ast)

        soup1 = BeautifulSoup(code1, 'html.parser')
        soup2 = BeautifulSoup(code2, 'html.parser')

        return soup1 == soup2


    # Given source html, return an asdl ast
    # by first converting the html text to beatiful soup
    #
    # NOTE: Assumes (for now) that we are dealing with a single tag
    #
    def surface_code_to_ast(self, code):
        # I dont know why I need html.parser here, but
        # for going from ast to surface code I need html5lib
        soup_ast = BeautifulSoup(code, 'html.parser')

        #
        # TODO This is highly tailored to assume a single tag
        #
        soup_node = soup_ast.contents[0]
        element_production = self.grammar.get_prod_by_ctr_name('Element')
        first_field = element_production.fields[0]
        asdl_field = RealizedField(first_field)
        field_value = soup_node.name
        asdl_field.add_value(str(field_value))

        asdl_node = AbstractSyntaxTree(element_production, realized_fields=[asdl_field])
        return asdl_node

    # Given an asdl ast, return source html code
    # by first converting asdl to beatiful soup
    #
    def ast_to_surface_code(self, asdl_ast):
        # Get the info for our tag
        realized_field = asdl_ast.fields[0]
        field = realized_field.field
        tag_name = realized_field.value

        # build up the soup (and strip out the <html> etc tags, just leaving our node)
        soup = BeautifulSoup('', 'html5lib')
        body = soup.body
        el = soup.new_tag(tag_name)
        body.append(el)
        return str(el)

    def get_primitive_field_actions(self, realized_field):
        # Mostly copy/pasted from the python example
        # But with the complexities removed, like handling cardinality > 1
        actions = []
        if realized_field.value is not None:
            field_values = [realized_field.value]
            tokens = []
            if realized_field.type.name == 'string':
                for field_val in field_values:
                    tokens.extend(field_val.split(' ') + ['</primitive>'])
            else:
                for field_val in field_values:
                    tokens.append(field_val)

            for tok in tokens:
                actions.append(GenTokenAction(tok))
        return actions

if __name__ == '__main__':
    #
    # Test ast->source and source->ast translation
    #

    asdl_text = open('./html_asdl.txt').read()
    grammar = ASDLGrammar.from_text(asdl_text)
    src_html = '<video></video>'
    transition_sys = HtmlTransitionSystem(grammar)
    asdl_ast = transition_sys.surface_code_to_ast(src_html)

    src_html_from_asdl = transition_sys.ast_to_surface_code(asdl_ast)

    assert src_html == src_html_from_asdl, "Could not go from src to ast and back again"

    #
    # Test get_actions and hypothesis generation
    #
    actions = transition_sys.get_actions(asdl_ast)
    hypothesis = Hypothesis()
    for t, action in enumerate(actions, 1):
        hypothesis.apply_action(action)
    src_from_hyp_tree = transition_sys.ast_to_surface_code(hypothesis.tree).strip()

    assert src_html == src_html_from_asdl == src_from_hyp_tree, "Generated source codes did not all match"
    print("Success")

    # Test 5k dataset output
    # _TODO_
    # decodes = pickle.load(open('../../../decodes/html/5k/model.sup.html.lstm.hidden256.embed128.action128.field64.type64.dropout0.3.lr0.001.lr_decay0.5.beam_size15.vocab.freq15.bin.train.bin.glorot.par_state_w_field_embe.seed0.bin.test.decode'))
    # print(len(decodes))
    # print(decodes[0])
    # pdb.set_trace()
