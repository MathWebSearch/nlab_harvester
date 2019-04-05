#!/usr/bin/python3
"""
    This file contains a class for configuration of the nLab Harvester.
    Mainly it reads the environment variables or sets default values
"""

import os

class Config:
    """
        config class reads the environment and provides them as class variables
    """
    def __init__(self):
        self.read_environment()

    def read_environment(self):
        """
            reads all the environment variables or sets default value
            if not existent
        """
        self.threads = int(os.getenv('NLAB_HARVESTER_THREADS', '1'))
        if self.threads < 1:
            raise ValueError('Your NLAB_HARVESTER_THREADS is not useful!')

        self.sourcepath = os.getenv('NLAB_SOURCE', '../nlab-content-html/pages/')

        self.harvestpath = os.getenv('NLAB_HARVESTS', '../harvests/')
        if not os.path.isdir(self.harvestpath):
            raise ValueError(f'{self.harvestpath} is not a directory!')

        self.latexmlhost = os.getenv('LATEXML_ADDRESS', 'localhost')

        self.latexmlport = int(os.getenv('LATEXML_PORT', '8080'))
        if not 0 < self.latexmlport < 65536:
            raise ValueError('Your LATEXML_PORT is not useful!')

        self.max_queue_length = int(os.getenv('MAX_QUEUE_LENGTH', '0'))
        if self.max_queue_length < 0:
            raise ValueError('Your MAX_QUEUE_LENGTH is not useful!')

        self.update_freq = int(os.getenv('UPDATE_FREQ', '0'))
        if self.update_freq < 0:
            raise ValueError('Your UPDATE_FREQ is not useful!')

    def print_config(self):
        """ prints all the current config variables """
        print('Current config:')
        for (key, value) in self.__dict__.items():
            print(f'{key}: {value}')
