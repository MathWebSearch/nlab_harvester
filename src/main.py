#!/usr/bin/python3

""" main for nlab harvester """

import multiprocessing as mp
import queue as q
import os
import filehandler
import harvester
import util


def worker(worker_id, batch_queue, config):
    """ target function for multiprocessing """
    nlab_harvester = harvester.Harvester(config['sourcepath'],
                                         config['harvestpath'])
    nlab_harvester.converter.set_host(config['latexmlhost'])
    nlab_harvester.converter.set_port(config['latexmlport'])
    while True:
        try:
            batch_id, batch = batch_queue.get()
        except q.Empty:
            print(f'process {worker_id} is done, queue is empty')
            break
        else:
            if (batch_id, batch) == (None, None):
                print(f'process {worker_id} swollowed a poison pill')
                break
            # print(f'worker {worker_id} works on batch {batch_id}')
            nlab_harvester.harvest_batch(batch_id, batch)

    print(f'stats of worker {worker_id}:')
    util.print_time_stats()


def read_enviroment():
    """ function to read the enviroment varibales and return a dictonary filled
    with it """
    config = {}
    config['threads'] = os.getenv('NLAB_HARVESTER_THREADS', '8')
    config['sourcepath'] = os.getenv('NLAB_SOURCE',
                                     '../nlab-content-html/pages/')
    config['harvestpath'] = os.getenv('NLAB_HARVESTS', '../harvests/')
    config['latexmlhost'] = os.getenv('LATEXML_ADDRESS', 'localhost')
    config['latexmlport'] = os.getenv('LATEXML_PORT', '8080')
    config['max_queue_length'] = os.getenv('MAX_QUEUE_LENGTH', '0')
    return config


def main():
    """ main of the nLab Harvester """

    config = read_enviroment()

    file_handler = filehandler.Filehandler(config['sourcepath'],
                                           config['harvestpath'])
    file_handler.get_source_updates()
    queue = file_handler.create_new_queue(int(config['max_queue_length']))
    print(f'There are {len(queue)} batches to do')

    threads = int(config['threads'])
    print(f'start nlab_harvesting with {threads} threads')

    if threads > 1:
        batch_queue = mp.Queue()
        for entry in queue:
            batch_queue.put(entry)

        procs = []
        for i in range(0, threads):
            batch_queue.put((None, None))
            proc = mp.Process(target=worker, args=(i, batch_queue, config))
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()
    else:
        # single threaded case
        nlab_harvester = harvester.Harvester(config['sourcepath'],
                                             config['harvestpath'])
        nlab_harvester.converter.set_host(config['latexmlhost'])
        nlab_harvester.converter.set_port(config['latexmlport'])
        for (batchid, batch) in queue:
            nlab_harvester.harvest_batch(batchid, batch)
        util.print_time_stats()


if __name__ == "__main__":
    main()
