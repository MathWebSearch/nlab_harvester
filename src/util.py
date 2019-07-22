#!/usr/bin/python3
""" just some util functions for the nlab harvester """

import time
import datetime
import os
import subprocess as sp

TIME_STAT = {}


def timer(func):
    """ timer function as a decorator """
    def wrapper(*args, **kwargs):
        before = time.time()
        ret = func(*args, **kwargs)
        after = time.time()

        if func.__name__ not in TIME_STAT:
            TIME_STAT[func.__name__] = [0, 0]

        TIME_STAT[func.__name__][0] += (after - before)
        TIME_STAT[func.__name__][1] += 1
        return ret
    return wrapper


def print_time_stats(name=''):
    """ print the collected time_stats """
    print('-'*10, ' Time Stats:', name, '-'*10)
    for key, value in sorted(TIME_STAT.items(),
                             key=lambda x: x[1][0],
                             reverse=True):
        avg = value[0]/value[1]
        print(f'\t{key}: {value[1]} calls, {value[0]:.2f}s, avg: {avg:.2f}s')
    print('-'*40)


def is_git_repo(path):
    """ checks if path is a git repo """
    if not path:
        return False
    args = ['git', '-C', path, 'status']
    return sp.call(args, stderr=sp.STDOUT, stdout=open(os.devnull, 'w')) == 0


def pull_git_repo(path):
    """ pulls the git repo """
    args = ['git', '-C', path, 'pull']
    try:
        sp.call(args, stderr=sp.STDOUT, stdout=open(os.devnull, 'w'))
    except sp.SubprocessError as err:
        print(f'pulling the repo at {path} went wrong with {err}')
    else:
        print(f'{path} successfully updated')


def clone_git_repo(path, repo_url):
    """ pulls the git repo """
    args = ['git', '-C', path, 'clone', repo_url]
    try:
        sp.call(args, stderr=sp.STDOUT, stdout=open(os.devnull, 'w'))
    except sp.SubprocessError as err:
        print(f'cloning the {repo_url} to {path} went wrong with {err}')
    else:
        print(f'{repo_url} cloned sucessfully to {path}')


@timer
def log(complete_file_path, *contents):
    """ log function, takes complete path and writes contents to
         the file"""
    try:
        log_file = open(complete_file_path, 'a')
        log_file.write('\n' + '-' * 5 + '\n')
        log_file.write(str(datetime.datetime.now()) + '\n')
        for content in contents:
            if content:
                log_file.write(content)
                log_file.write('\n' + '-' * 5 + '\n')
    except OSError:
        print('logging went wrong' + complete_file_path)
