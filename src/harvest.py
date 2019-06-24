#!/usr/bin/python3
""" represents a harvest """
import copy
import subprocess as sp
# from xml.sax.saxutils import escape
import bs4
import util


def make_find_func(data_id):
    """ TODO: """
    def find_function(tag):
        assert isinstance(tag, bs4.element.Tag)
        return (tag.name == 'data'
                and tag.has_attr('mws:data_id')
                and tag['mws:data_id'] == str(data_id))
    return find_function


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
            out_file.write(self.tag.prettify())

    def __repr__(self):
        return self.tag.prettify()

    def insert_data_tag(self, data_id, path):
        """ inserts a new data tag into to the harvest tag"""
        string = ('<mws:data xmlns:mws=\"http://search.mathweb.org/ns\">'
                  '<id>' + path + '</id>''</mws:data>')
        tag = bs4.BeautifulSoup(string, 'xml')
        tag.data['mws:data_id'] = str(data_id)
        del tag.data['xmlns:mws']
        self.tag.harvest.append(tag.data)

    @util.timer
    def insert_in_data_tag(self, data_id, content):
        """ puts content in a data_tag with that given data_id """

        data_tag = self.tag.find_all(make_find_func(data_id))
        assert len(data_tag) == 1
        if data_tag:
            data_tag[0].append(copy.copy(content))
        else:
            print(f'data_tag with {data_id} does not exist')

    def insert_math_in_data_tag(self, data_id, math_tag, local_id, url):
        """ TODO """
        data_tag = self.tag.find_all(make_find_func(data_id))
        assert len(data_tag) == 1
        new_math = bs4.BeautifulSoup('<math/>', 'xml')
        new_math.math['local_id'] = str(local_id)
        new_math.math['url'] = str(url)
        new_math.math.append(copy.copy(math_tag))
        # escaped_math = escape(str(math_tag))
        # new_math.math.append(escaped_math.replace('\n', ''))
        data_tag[0].append(new_math.math)

    @util.timer
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

    @util.timer
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
        assert math_tag.name == 'math' or math_tag.name == 'Math'
        math_tag['local_id'] = str(local_id)
        math_tag['url'] = url
        # self.insert_in_data_tag(data_id, math_tag)
        self.insert_math_in_data_tag(data_id, math_tag, local_id, url)
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
