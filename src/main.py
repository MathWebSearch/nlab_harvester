#!/usr/bin/python3

""" main for nlab harvester """

import time
import multiprocessing as mp
import queue as q
import filehandler
import harvester
import util
import config_reader


def worker(worker_id, batch_queue, config):
    """ target function for multiprocessing """
    nlab_harvester = harvester.Harvester(config.sourcepath, config.harvestpath)
    nlab_harvester.converter.set_host(config.latexmlhost)
    nlab_harvester.converter.set_port(config.latexmlport)
    while True:
        try:
            batch_id, batch = batch_queue.get()
        except q.Empty:
            print(f'process {worker_id} is done, queue is empty')
            break
        else:
            if (batch_id, batch) != (None, None):
                print(f'worker {worker_id} works on batch {batch_id}')
                nlab_harvester.harvest_batch(batch_id, batch)
                continue

            print(f'process {worker_id} swollowed a poison pill')
            break

    # print(f'stats of worker {worker_id}:')
    util.print_time_stats()

def start_worker(config, queue):
    """ starts the processes for the work """

    threads = int(config.threads)
    threads = min(len(queue), threads)
    print(f'start nlab_harvesting with {threads} processes')

    if threads > 1:
        batch_queue = mp.Queue()
        for entry in queue:
            batch_queue.put(entry)

        procs = []
        for i in range(0, threads):
            # insert a poison pill in the queue
            batch_queue.put((None, None))
            proc = mp.Process(target=worker, args=(i, batch_queue, config))
            proc.start()
            procs.append(proc)

        for proc in procs:
            proc.join()
    else:
        # single threaded case
        nlab_harvester = harvester.Harvester(config.sourcepath,
                                             config.harvestpath)
        nlab_harvester.converter.set_host(config.latexmlhost)
        nlab_harvester.converter.set_port(config.latexmlport)
        for (batchid, batch) in queue:
            nlab_harvester.harvest_batch(batchid, batch)
        util.print_time_stats()
    print('The work is done for now.')


def main():
    """ main function for harvester """
    # config = util.read_enviroment()

    config = config_reader.Config()

    file_handler = filehandler.Filehandler(config.sourcepath, config.harvestpath)

    sleep_timeout = int(config.update_freq)*60
    while True:
        file_handler.get_source_updates()
        queue = file_handler.create_new_queue(int(config.max_queue_length))
        if queue:
            print(f'There are {len(queue)} batches to do')
            start_worker(config, queue)
        else:
            print('Nothing to do yet')

        if sleep_timeout == 0:
            break
        else:
            time.sleep(sleep_timeout)

    print('end of nlab_harvesting')


if __name__ == "__main__":
    main()
