#!/usr/bin/python3
""" harvests the nlab """

import html
import re
from bs4 import BeautifulSoup
import util
import harvest as hrvst
import latexmlservice as ltxs


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


def generate_url_to_experimental_frontend(page_id):
    """
    this returns the url to the experimental frontend (see
    https://nforum.ncatlab.org/discussion/8321/experimental-static-frontend-for-the-nlab/)
    this seems to vendor the same html files, that are in the git repo
    but seems atm more like diry hack
    """
    assert isinstance(page_id, int)
    return f'https://ncatlab.org/nginx-experimental-frontend/{page_id}.html'


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

    @util.timer
    def harvest_batch(self, batchid, batch):
        """
        takes number and a list of filenames and creates a harvest in the
        harvestpath with the name nlab_{batchid}.harvest
        """
        outfile = f'{self.harvestpath}/nlab_{str(batchid)}.harvest'
        with hrvst.Harvest(outfile) as harvest:
            for file_name in batch:
                number = int(file_name.split('.')[0])
                self.harvest_file(file_name, number, harvest)

    @util.timer
    def harvest_file(self, path, data_id, harvest):
        """ TODO write doc string and make it less complex"""
        assert isinstance(harvest, hrvst.Harvest)
        err_file = f'{self.logpath}/err{str(data_id)}'
        log_file = None
        if self.logging:
            log_file = f'{self.logpath}/log{str(data_id)}'
        try:
            cur_file = open(f'{self.sourcepath}/{path}', 'r')
        except OSError:
            util.log(err_file, 'could not open ' + path)
            return
        # this expolits the fact, that the content of a nlab page is in that
        # tag
        soup = BeautifulSoup(cur_file, 'lxml')
        cur_file.close()

        base_url = generate_url_to_experimental_frontend(data_id)
        harvest.insert_data_tag(data_id, f'{self.sourcepath}{path}')
        harvest.insert_in_meta_data(data_id, soup.title)
        local_id = 1
        relevant = soup.find(id='revision')
        if relevant is None:
            return

        @util.timer
        def handle_math_tag(math_tag):
            if not math_tag.find('annotation'):
                return
            # ignore too short formulae
            if len(math_tag.annotation.text) < 2:
                return
            cleantag = html.unescape(math_tag.annotation.text)
            # just to prevent that we are trying to convert an empty string
            if not cleantag:
                return
            content = self.converter.convert(cleantag, err_file, log_file)
            if content is None:
                return
            newnode = BeautifulSoup(content, 'xml').math
            if newnode is None:
                util.log(err_file, math_tag.prettify(), content)
                return

            # looks for id in tag, there some tags without an id
            url = base_url
            if 'id' in math_tag.attrs:
                url += ('#' + math_tag['id'])

            nonlocal local_id
            harvest.insert_math_tag(data_id, local_id, url, newnode)
            math_tag.replace_with(f'math{local_id}')
            local_id = local_id + 1

        for math_tag in relevant.find_all('math', 'maruku-mathml'):
            handle_math_tag(math_tag)

        text = relevant.getText().replace('\n', ' ')
        text_tag = BeautifulSoup(f'<text>{text}</text>', 'xml')
        harvest.insert_in_data_tag(data_id, text_tag.find('text'))
