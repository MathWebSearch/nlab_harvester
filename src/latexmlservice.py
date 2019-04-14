#!/usr/bin/python3
""" wrapper for latexml using the ltxmojo plugin """

import requests
import util


class LatexmlService:
    """ just a class to encapsulate the convert request """
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.make_url()

    def set_port(self, port):
        """ setter for port """
        self.port = port
        self.make_url()

    def set_host(self, host):
        """ setter for host """
        self.host = host
        self.make_url()

    def make_url(self):
        """ creates the url for the convert request to the ltxmojo server """
        self.url = 'http://' + self.host + ':' + str(self.port) + '/convert'
        return self.url

    @util.timer
    def convert(self, literal, err_file, log_file):
        """ converts a literal returns None if something goes wrong """
        # data = {'profile': 'nlab', 'tex': '$' + literal + '$'}
        data = {'profile': 'nlab', 'tex': literal}

        try:
            request = requests.post(self.url, data=data)
        except requests.exceptions.RequestException as exception:
            util.log(err_file, literal, str(exception))
            print(f'Excption while Post request: {exception}')
            return None

        if request.status_code == 200:
            result = request.json()
            if log_file is not None:
                util.log(log_file, result['log'])
            return result['result']

        util.log(err_file, literal, str(request.status_code))
        print(f'error with {literal}')
        return None
