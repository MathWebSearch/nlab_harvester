#!/usr/bin/python3
""" represents a harvest """
import copy
import subprocess as sp
import bs4
import util


class Harvest:
    """ harvest """
    def __init__(self, output_file):
        string = ('<mws:harvest xmlns:m=\"http://www.w3.org/1998/Math/MathML\"'
                  ' xmlns:mws=\"http://search.mathweb.org/ns\"></mws:harvest>')
        self.tag = bs4.BeautifulSoup(string, 'xml')
        self.output_file = output_file

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.write_to_file()

    def write_to_file(self):
        """ write the member tag to the file """
        with open(self.output_file, 'w') as out_file:
            out_file.write(str(self.tag.prettify()))

    def __repr__(self):
        return self.tag.prettify()

    def insert_data_tag(self, data_id, path):
        """ inserts a data tag """
        string = ('<mws:data xmlns:mws=\"http://search.mathweb.org/ns\">'
                  '<id>' + path + '</id>''</mws:data>')
        tag = bs4.BeautifulSoup(string, 'xml')
        tag.data['mws:data_id'] = str(data_id)
        del tag.data['xmlns:mws']
        self.tag.harvest.append(tag.data)

    def insert_in_data_tag(self, data_id, content):
        """ puts content in a data_tag with that given data_id """
        def find_function(tag):
            assert isinstance(tag, bs4.element.Tag)
            return (tag.name == 'data'
                    and tag.has_attr('mws:data_id')
                    and tag['mws:data_id'] == str(data_id))

        data_tag = self.tag.find_all(find_function)
        if data_tag:
            data_tag[0].append(copy.copy(content))
        else:
            print(f'data_tag with {data_id} does not exist')

    def insert_in_meta_data(self, data_id, content):
        """ insert content in the meta_data tag of the data_tag """
        def find_function(tag):
            assert isinstance(tag, bs4.element.Tag)
            return (tag.name == 'data'
                    and tag.has_attr('mws:data_id')
                    and tag['mws:data_id'] == str(data_id))

        data_tag = self.tag.find_all(find_function)
        if data_tag:
            if not data_tag[0].find_all('metadata'):
                metadata = bs4.BeautifulSoup('<metadata/>', 'lxml')
                data_tag[0].append(metadata.metadata)

            data_tag[0].metadata.append(copy.copy(content))
        else:
            print(f'data_tag with {data_id} does not exist')

    def insert_expr_tag(self, data_id, url, semantics_node):
        """
            inserts a expr tag in the harvest node but just takes the cmml part
            from the semantics node
        """
        string = ('<mws:expr xmlns:mws=\"http://search.mathweb.org/ns\">'
                  '</mws:expr>')
        tag = bs4.BeautifulSoup(string, 'xml')
        tag.expr['mws:data_id'] = str(data_id)
        del tag.expr['xmlns:mws']
        for child in semantics_node.children:
            if child.name != 'annotation-xml':
                tag.expr.append(copy.copy(child))

        tag.expr['url'] = url
        self.tag.harvest.append(tag)

    @util.timer
    def insert_math_tag(self, data_id, local_id, url, math_tag):
        """
            takes a math tag, that was converted, and insert it in the data_tag
            and the cmml part in a expr tag
        """
        assert isinstance(math_tag, bs4.element.Tag)
        assert math_tag.name == 'math'
        math_tag['local_id'] = str(local_id)
        math_tag['url'] = url
        pmml_math = copy.copy(math_tag)
        # keeps only the pmml stuff for the data tag
        # and puts only the cmml part in the expr
        pmml_math.semantics.clear()
        pmml_math.semantics.append(math_tag.semantics.find('annotation-xml'))
        self.insert_in_data_tag(data_id, pmml_math)
        self.insert_expr_tag(data_id, local_id, math_tag.semantics)


def test():
    """ test """
    args = ['latexmlc',
            '--profile=itex',
            'literal:$a \\invamp b$',
            ]
    proc = sp.Popen(args, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    out, _ = proc.communicate()
    tag = bs4.BeautifulSoup(out.decode(), 'xml').math
    with Harvest('test.harvest') as harvest:
        harvest.insert_data_tag(1, 'bla/test/path')
        harvest.insert_math_tag(1, 1, 'testurl', tag)
