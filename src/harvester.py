#!/usr/bin/python3
""" harvests the nlab """

import html
import re
from bs4 import BeautifulSoup
import util
import latexmlservice as ltxs


# helper functions to create bs4 tags
def create_harverst_tag():
    """ creates a the root for a harvest file """

    string = "<mws:harvest xmlns:m=\"http://www.w3.org/1998/Math/MathML\" \
            xmlns:mws=\"http://search.mathweb.org/ns\"></mws:harvest>"
    return BeautifulSoup(string, 'xml')


def create_data_tag(data_id, content):
    """ creates a mws:data tag and fills it with content """

    string = "<mws:data xmlns:mws=\"http://search.mathweb.org/ns\"></mws:data>"
    tag = BeautifulSoup(string, 'xml')
    tag.data['mws:data_id'] = str(data_id)
    if content is not None:
        tag.data.append(content)
    del tag.data['xmlns:mws']
    return tag.data


def create_expr_tag(data_id, content, url):
    """ creates a mws:expr tag and fills it with content and the url """

    string = "<mws:expr xmlns:mws=\"http://search.mathweb.org/ns\"></mws:expr>"
    tag = BeautifulSoup(string, 'xml')
    tag.expr['mws:data_id'] = str(data_id)
    del tag.expr['xmlns:mws']
    tag.expr.append(content)
    tag.expr['url'] = url
    return tag.expr


def generate_url_from_title(title):
    """
    function that takes the the title of an nlab page and genaerates the
    url the nlab. The Title of an nLab Page looks like 'bla bla in nLab' and
    the url is always http://ncatlab.org/nlab/show/bla+bla or
    http://ncatlab.org/nlab/revision/bla+bla/REVISION
    """
    assert isinstance(title, str)
    base = 'http://ncatlab.org/nlab/revision/'
    # some crazy regex magic: it searches for all non-whitespacechars that are
    # maybe followed by a single whitespace, just to remove some unwanted
    # spaces and newlines
    clean = re.search(r'(\S+ ?)+', title).group(0)
    parts = clean.split(' ')
    len_parts = len(parts)
    for i in range(len_parts):
        base += parts[i]
        if i == len_parts - 1 or (parts[i+1] == 'in' and parts[i+2] == 'nLab'):
            break
        base += '+'
    return base


class Harvester:
    """ Harvester """
    def __init__(self, sourcepath, harvestpath,
                 converter=ltxs.LatexmlService()):
        self.sourcepath = sourcepath
        self.harvestpath = harvestpath
        self.logpath = '../logs/'
        self.logging = False
        self.converter = converter

    def set_logpath(self, logpath):
        """ setter for logpath """
        self.logpath = logpath

    def set_converter(self, converter):
        """ setter for converter, needs something that implements a convert
        method """
        self.converter = converter

    @ltxs.util.timer
    def __handle_tags(self, tags, root, data_id, base_url, err_file):
        """ just a helper function that takes the tags and converts them and
            puts them in the root node """
        log_file = None
        if self.logging:
            log_file = self.logpath + '/log' + str(data_id)

        for tag in tags:
            # look at all math tags and try to convert the
            # annotation to  MathML
            if not tag.find('annotation'):
                continue

            if len(tag.annotation.text) < 2:
                # too short
                continue

            cleantag = html.unescape(tag.annotation.text)
            if not cleantag:
                # just to prevent that we are trying to convert an empty string
                continue
            content = self.converter.convert(cleantag, err_file, log_file)

            if content is None:
                continue

            # think about this, cause otherwise non math tags are discarded
            newnode = BeautifulSoup(content, 'xml').math
            if newnode is None:
                util.log(err_file, tag.prettify(), content)
                continue

            # looks for id in tag, there some tags without an id
            url = base_url

            if 'id' in tag.attrs:
                url += ('#' + tag['id'])

            root.append(create_expr_tag(data_id, newnode, url))

    @ltxs.util.timer
    def harvest_file(self, path, data_id, root):
        """
        takes a file creates a datatag and puts all math expr as children
        in root
        """
        err_file = self.logpath + '/err' + str(data_id)
        try:
            cur_file = open(self.sourcepath + '/' + path, 'r')
        except OSError:
            util.log(err_file, 'could not open ' + path)
            return

        soup = BeautifulSoup(cur_file, 'lxml')

        cur_file.close()

        base_url = generate_url_from_title(soup.title.string)
        # datatag = create_data_tag(data_id, self.sourcepath + path)
        datatag = create_data_tag(data_id, None)
        datatag.append(soup.title)
        root.append(datatag)

        # search all Mathtags
        tags = soup.find_all("math", "maruku-mathml")
        self.__handle_tags(tags, root, data_id, base_url, err_file)

    @ltxs.util.timer
    def harvest_batch(self, batchid, batch):
        """
        takes number and a list of filenames and creates a harvest in the
        harvestpath with the name nlab_{batchid}.harvest
        """

        root = create_harverst_tag()

        for file_name in batch:
            number = int(file_name.split('.')[0])
            self.harvest_file(file_name, number, root.harvest)

        # print(f'Batch Number {batchid} is done')
        outfile = self.harvestpath + '/nlab_' + str(batchid) + '.harvest'
        output = open(outfile, "w")
        output.write(str(root))
        output.close()
