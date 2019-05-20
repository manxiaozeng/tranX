# coding=utf-8
import ast
from bs4 import BeautifulSoup
from asdl.transition_system import TransitionSystem
from asdl.asdl_ast import RealizedField, AbstractSyntaxTree
from asdl.asdl import ASDLGrammar
from common.registerable import Registrable


@Registrable.register('html')
class HtmlTransitionSystem(TransitionSystem):
    def tokenize_code(self, code, mode):
        # Think this is required for producing datasets
        raise NotImplementedError

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
    # NOTE: Assumes (for now) that we are dealing with a single tag
    #
    def ast_to_surface_code(self, asdl_ast):
        if asdl_ast.production.constructor.name != 'Element':
            raise NotImplementedError("Only supports constructors of type Element")

        if len(asdl_ast.fields) != 1:
            raise NotImplementedError("Only supports html with a single tag")

        # Get the info for our tag
        realized_field = asdl_ast.fields[0]
        field = realized_field.field
        if field.name != 'tag_name':
            raise NotImplementedError("Only supports tag_name field for now")
        tag_name = realized_field.value

        # build up the soup
        soup = BeautifulSoup('', 'html5lib')
        body = soup.body
        el = soup.new_tag(tag_name)
        body.append(el)
        return str(el)


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

    assert src_html == src_html_from_asdl
