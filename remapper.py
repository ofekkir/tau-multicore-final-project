import psutil
import random
import os
import subprocess

import config

class Remapper(object):
    def __init__(self, hw, classifications):
        super(Remapper, self).__init__()
        self._hw = hw
        self._classifications = classifications

        blacklist = [os.getpid()] # Ignoring sam process
        self._processes = self._init_processes(blacklist)

    @staticmethod
    def _init_processes(blacklist):
        processes = []
        pids = [int(pid) for pid in subprocess.check_output('ps -eTotid='.split()).splitlines()]

        for pid in pids:
            if pid in blacklist:
                continue

            try:
                process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue

            # Ignore root threads
            if process.uids().real == 0:
                continue

            # TODO: remove!
                # TODO: remove!
                if process.uids().real not in config.OPTIMIZE_ONLY_PROCESSES_OF_USER:
                    continue
                continue
            # In the first time sam encounters a process, the process is not pinned yet, thus we use some random cpu as
            # it's cpu.
            if len(process.cpu_affinity()) != 1:
                affinity = random.choice(process.cpu_affinity())
                process.cpu_affinity([affinity])

            processes.append(process)

        return processes

    def move(self, src_list, dst_list):
        src_core = src_list[0]
        dst_core = dst_list[0]

        src_tasks = [p for p in self._processes if p.cpu_affinity()[0] == src_core]

        src_list.remove(src_core)

        print('moving src_core={},dst_core={}'.format(src_core, dst_core))

        for task in src_tasks:
            task.cpu_affinity([dst_core])


    def swap(self, src_list, dst_list):
        src_core = src_list[0]
        dst_core = dst_list[0]

        src_tasks = [p for p in self._processes if p.cpu_affinity()[0] == src_core]
        dst_tasks = [p for p in self._processes if p.cpu_affinity()[0] == dst_core]

        src_list.remove(src_core)
        dst_list.remove(dst_core)


        for task in src_tasks:
            print(task)
            task.cpu_affinity([dst_core])

        for task in dst_tasks:
            print(task)
            task.cpu_affinity([src_core])


    def _remap_inter_socket_coherence(self):
        for socket_i in self._hw:
            if not self._classifications[socket_i].is_inter:
                continue

            for socket_j in self._hw:
                if socket_i == socket_j:
                    continue

                while len(self._classifications[socket_i].is_inter + self._classifications[socket_i].is_intra) < \
                        len(self._hw[socket_i]) \
                        and self._classifications[socket_j].is_inter:

                    while self._classifications[socket_i].is_idle and self._classifications[socket_j].is_inter:
                        self.move(self._classifications[socket_j].is_inter,
                                  self._classifications[socket_i].is_idle)


                    while self._classifications[socket_i].is_cpu_bound and self._classifications[socket_j].is_inter:
                        self.swap(self._classifications[socket_j].is_inter,
                                  self._classifications[socket_i].is_cpu_bound)

                    while self._classifications[socket_i].is_memory_bound and self._classifications[socket_j].is_inter:
                        self.swap(self._classifications[socket_j].is_inter,
                                  self._classifications[socket_i].is_memory_bound)

    def remap_processes(self):
        self._remap_inter_socket_coherence()
