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

    # should stabily print attrs in alphabetical
    # order to ensure comparison between two asts is
    # consistent regardless of order of attrs in the src code
    # NOTE: This is dead code now
    def ast_to_bleu_str(self, ast):
        soup_el = self.ast_to_soup(ast)
        return soup_el.prettify()

    # Given source html, return an asdl ast
    # by first converting the html text to beatiful soup
    #
    # NOTE: Assumes (for now) that we are dealing with a single tag
    #
    def surface_code_to_ast(self, code):
        soup_ast = BeautifulSoup(code, 'html.parser')
        # Assumes we're just dealing with a single tag
        tag = soup_ast.contents[0]

        def add_opt_str(attr_name, field, realized):
            if tag.has_attr(attr_name):
                realized.add_value(str(tag[attr_name]))
            else:
                realized.add_value(None)

        def add_realized(field):
            realized = RealizedField(field)
            if field.name == 'tag_name':
                realized.add_value(str(tag.name))
            elif field.name == 'src':
                add_opt_str('src', field, realized)
            elif field.name == 'autoplay':
                realized.add_value(tag.has_attr('autoplay'))
            elif field.name == 'loop':
                realized.add_value(tag.has_attr('loop'))
            elif field.name == 'muted':
                realized.add_value(tag.has_attr('muted'))
            elif field.name == 'poster':
                add_opt_str('poster', field, realized)
            elif field.name == 'width':
                add_opt_str('width', field, realized)
            elif field.name == 'height':
                add_opt_str('height', field, realized)
            else:
                raise Exception("Warning: Found unrecognized field: {0}".format(field.name))
            return realized

        element_production = self.grammar.get_prod_by_ctr_name('Element')
        realized_fields = [add_realized(field) for field in element_production.fields]
        asdl_node = AbstractSyntaxTree(element_production, realized_fields=realized_fields)
        return asdl_node

    # Given an asdl ast, return source html code
    # by first converting asdl to beatiful soup
    #
    def ast_to_surface_code(self, asdl_ast):
        el = self.ast_to_soup(asdl_ast)
        return str(el)

    def ast_to_soup(self, asdl_ast):
        soup = BeautifulSoup('', 'html5lib')
        body = soup.body

        def process_opt_str(field, el):
            if field.value != None:
                el[field.name] = field.value

        def process_field(field, el):
            if field.name == 'src':
                process_opt_str(field, el)
            elif field.name == 'autoplay':
                if field.value:
                    # Use None so the output looks like 'autoplay' not 'autoplay=""'
                    el['autoplay'] = None
            elif field.name == 'loop':
                if field.value:
                    # Use None so the output looks like 'autoplay' not 'autoplay=""'
                    el['loop'] = None
            elif field.name == 'muted':
                if field.value:
                    # Use None so the output looks like 'autoplay' not 'autoplay=""'
                    el['muted'] = None
            elif field.name == 'poster':
                process_opt_str(field, el)
            elif field.name == 'width':
                process_opt_str(field, el)
            elif field.name == 'height':
                process_opt_str(field, el)
            else:
                raise Exception("Warning: Unrecognized field: {0}".format(field.name))

        # First get the tag name, which we assume is always there
        for field in asdl_ast.fields:
            if field.name == 'tag_name':
                el = soup.new_tag(field.value)
                break
        [process_field(field, el) for field in asdl_ast.fields if field.name != 'tag_name']
        return el

    # Given 2 asdl asts compute a partial comparison between 0-1
    def partial_compare(self, ref_ast, hyp_ast):
        ref_tag = self.ast_to_soup(ref_ast)
        hyp_tag = self.ast_to_soup(hyp_ast)

        points_scored = 0
        total_possible_points = 0

        # Check tag is the same
        if ref_tag.name == hyp_tag.name:
            points_scored += 1
        total_possible_points += 1

        # Check all fields
        element_production = self.grammar.get_prod_by_ctr_name('Element')
        for field in element_production.fields:
            # TODO There will be a field tag_name which never exists on BS (its just 'name')
            field_name = field.name
            # Check that if the field is in ast1 its also in ast2
            ref_has_field = ref_tag.has_attr(field_name)
            hyp_has_field = hyp_tag.has_attr(field_name)

            if ref_has_field:
                total_possible_points += 2
                if hyp_has_field:
                    points_scored += 1
                    # Now check if value is the same
                    value_same = ref_tag[field_name] == hyp_tag[field_name]
                    if value_same:
                        # Give extra weight to getting a string correct
                        if isinstance(ref_tag[field_name], str):
                            points_scored += 3 # 2 points more than normal
                            total_possible_points += 2 # above we assumed just 1, so bump up to get to 3
                        else:
                            points_scored += 1
            else:
                if hyp_has_field:
                    # penalize for fields it shouldnt have
                    total_possible_points += 1

        # TODO: Penalize for fields that hyp_ast has that ref_ast doesnt
        score = points_scored / float(total_possible_points) # force a float, python2...
        print("scored ref and hyp: ")
        print(ref_tag)
        print(hyp_tag)
        print("score: ")
        print(score)
        return score

    def is_valid_hypothesis(self, hyp, **kwargs):
        try:
            hyp_code = self.ast_to_surface_code(hyp.tree)
            self.surface_code_to_ast(hyp_code)
        except:
            return False
        return True

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
    # Test get_actions and hypothesis generation
    #
    actions = transition_sys.get_actions(asdl_ast)
    hypothesis = Hypothesis()
    for t, action in enumerate(actions, 1):
        hypothesis.apply_action(action)
    src_from_hyp_tree = transition_sys.ast_to_surface_code(hypothesis.tree).strip()

    assert src_html == src_html_from_asdl == src_from_hyp_tree, "Generated source codes did not all match"
    print("Success")
