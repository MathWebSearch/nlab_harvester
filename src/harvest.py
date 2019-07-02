#!/usr/bin/python3
""" represents a harvest """
import copy
import subprocess as sp
import re
from bs4.dammit import EntitySubstitution
# from xml.sax.saxutils import escape, quoteattr
import bs4
import util


def make_find_func(data_id):
    """Returns a function that looks for a tag with data_id """
    def find_function(tag):
        assert isinstance(tag, bs4.element.Tag)
        return (tag.name == 'data'
                and tag.has_attr('mws:data_id')
                and tag['mws:data_id'] == str(data_id))
    return find_function


def xml_escape(string):
    """ formatter function for writing to file """
    # it seems to be a problem form bs to escape stuff and selfclosing tags
    ret = EntitySubstitution.substitute_xml(string)
    ret = ret.replace('"', '&quot;')
    ret = ret.replace("'", '&apos;')
    return ret


def convert_tag_to_string(tag):
    """ converts the complete tag to string and strips out clutter """
    assert isinstance(tag, bs4.element.Tag)
    ret = tag.decode()
    ret = ret.replace('\n', '')
    ret = ret.strip(' \n\t\r')
    # print(ret)
    return ret


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

    def insert_math_in_data_tag(self, data_id, math_tag, local_id):
        """ TODO """
        data_tag = self.tag.find_all(make_find_func(data_id))
        assert len(data_tag) == 1
        new_math = bs4.BeautifulSoup('<math/>', 'xml')
        new_math.math['local_id'] = str(local_id)
        # new_math.math['url'] = str(url)
        # new_math.math.append(copy.copy(math_tag))
        escaped_math = convert_tag_to_string(math_tag.math)
        new_math.math.append(escaped_math)
        data_tag[0].append(new_math.math)

    @util.timer
    def insert_in_meta_data(self, data_id, content):
        """ insert content in the meta_data tag of the data_tag """

        data_tag = self.tag.find_all(make_find_func(data_id))
        assert len(data_tag) == 1
        if data_tag:
            if not data_tag[0].find_all('metadata'):
                metadata = bs4.BeautifulSoup('<metadata/>', 'xml')
                data_tag[0].append(metadata.metadata)

            if isinstance(content, bs4.element.Tag):
                escaped = convert_tag_to_string(content)
                data_tag[0].metadata.append(escaped)
            else:
                data_tag[0].metadata.append(content)

        else:
            print(f'data_tag with {data_id} does not exist')

    @util.timer
    def insert_expr_tag(self, data_id, url, semantics_node):
        """
            inserts a expr tag in the harvest node but just takes the cmml part
            from the semantics node
        """
        assert semantics_node
        string = ('<mws:expr xmlns:mws=\"http://search.mathweb.org/ns\">'
                  '</mws:expr>')
        tag = bs4.BeautifulSoup(string, 'xml')
        tag.expr['mws:data_id'] = str(data_id)
        del tag.expr['xmlns:mws']
        # here it depends on the order of the parameter of ltx if cmml then the
        # annontation ist pmml and vice verse
        # i hope that it stays compatible to both orders
        cmml = semantics_node.find('annotation-xml', encoding='MathML-Content')
        if cmml:
            for child in cmml.children:
                tag.expr.append(copy.copy(child))
        else:
            for child in semantics_node.children:
                print(child.name)
                if not re.match('annotation.*', child.name):
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
        semantics = math_tag.find('m:semantics')
        if not semantics:
            math_tag.find('semantics')
        # math_tag['local_id'] = str(local_id)
        math_tag.math['url'] = url
        # self.insert_in_data_tag(data_id, math_tag)
        self.insert_math_in_data_tag(data_id, math_tag, local_id)
        self.insert_expr_tag(data_id, local_id, semantics)


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
