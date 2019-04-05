#!/usr/bin/python3
"""
    parses the files from the nlab html sources
    needs that the files have the pattern [1,2,...].html
    https://github.com/ncatlab/nlab-content-html
"""
from multiprocessing import Queue
import os
import fnmatch
import util

REPO_URL = 'https://github.com/ncatlab/nlab-content-html'


class Filehandler:
    """ handels the the source files in path and creates batches """
    def __init__(self, sourcepath, harvestpath, batchsize=10):
        self.sourcepath = sourcepath
        self.harvestpath = harvestpath
        self.batchsize = batchsize

    def set_batchsize(self, batchsize):
        """ setter for batchsize """
        self.batchsize = batchsize

    def set_sourcepath(self, sourcepath):
        """ setter for sourcepath """
        self.sourcepath = sourcepath

    def set_harvestpath(self, harvestpath):
        """ setter for harvestpath """
        self.harvestpath = harvestpath

    # @util.timer
    def get_source_updates(self):
        """ pulls the updates from the Gitrepo to sourcepath, if not there
        clones the repo to sourcepath """
        if util.is_git_repo(self.sourcepath):
            util.pull_git_repo(self.sourcepath)
            return

        if not os.path.isdir(self.sourcepath):
            path_parts = self.sourcepath.split('/')
            new_path = ''
            for part in path_parts:
                if part == 'nlab-content-html':
                    break
                new_path += part + '/'
            print(new_path)
            util.clone_git_repo(new_path, REPO_URL)
            return
        print(f'no chance to update {self.sourcepath}')

    # @util.timer
    def create_filelist(self):
        """ returns a sorted list of the files in the dir """
        files_list = os.listdir(self.sourcepath)
        files_list = fnmatch.filter(files_list, '[0-9]*.html')
        files_list = sorted(files_list, key=lambda f: int(f.split('.')[0]))
        return files_list

    # @util.timer
    def create_a_batch(self, number, files_list):
        """ returns a list of all files for batch with number """
        # think about this, this is a lil' bit slow
        ret = [x for x in files_list
               if (int(x.split('.')[0])//self.batchsize) == number]
        return ret

    # @util.timer
    def is_outdated(self, number, files):
        """ returns False if the harvest is uptodate, if not returns true """

        cur_harvest = self.harvestpath + '/nlab_' + str(number) + '.harvest'
        if not os.path.isfile(cur_harvest):
            return True

        harvest_time = os.path.getmtime(cur_harvest)
        for file_name in files:
            cur_file = self.sourcepath + file_name
            if os.path.isfile(cur_file):
                file_time = os.path.getmtime(cur_file)
                if file_time > harvest_time:
                    return True

        return False

    # @util.timer
    def create_new_queue(self, max_batches=0, total_new=False):
        """
        creates a queue with all batches that needs to be harvested
        returns it as a tuple of batch_id and a list of the file_names
        with max_batches it is possible the queue length and with total_new set
        to True every harvest is made new althought it is not outdated
        """
        files_list = self.create_filelist()
        max_filename = int(files_list[-1].split('.')[0])

        queue = Queue()
        counter = 0
        for i in range(0, max_filename//self.batchsize):
            cur_batch = []
            for _ in range(0, self.batchsize):
                file_number = int(files_list[0].split('.')[0])
                if i == (file_number//self.batchsize):
                    cur_batch.append(files_list[0])
                    del files_list[0]

            # check if cur_batch is empty
            if not cur_batch:
                continue
            if total_new or self.is_outdated(i, cur_batch):
                queue.put((i, cur_batch))
                counter += 1
            if 0 < max_batches <= counter:
                break

        return queue
