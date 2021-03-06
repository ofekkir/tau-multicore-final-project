from collections import namedtuple
import subprocess
import csv
import re

import config
from classification import Classification
from remapper import Remapper

MEASUREMENTS_FIELDS = 'cpu,inter_socket_coherence,intra_socket_coherence,remote_dram,memory_bandwidth,instructions,cycles'
Measurement = namedtuple('Measurement', MEASUREMENTS_FIELDS)


class Sam(object):
    def __init__(self):
        super(Sam, self).__init__()
        self._available_hardware = {}
        self._init_available_hardware()

    def run(self):
        i = 0
        while True:
            counters = self._collect_performance_counters()
            measurements = self._compute_measurements(counters)
            classified_measurements = self._classify_measurements(measurements)

            Remapper(self._available_hardware, classified_measurements).remap_processes()
            i += 1
            if i == config.NUMBER_OF_ITERATIONS:
                return

    def _classify_measurements(self, measurements):
        classifications = {}

        for socket in self._available_hardware:

            classifications[socket] = Classification()

            for cpu in self._available_hardware[socket]:

                measurement = measurements[cpu]

                is_cpu_bound = True
                is_inter = measurement.inter_socket_coherence > config.INTER_SOCKET_COHERENCE_THRESHOLD_PER_TASK
                if is_inter:
                    classifications[socket].is_inter.append(cpu)
                    is_cpu_bound = False

                if not is_inter and \
                                measurement.intra_socket_coherence > config.INTRA_SOCKET_COHERENCE_THRESHOLD_PER_TASK:
                    classifications[socket].is_intra.append(cpu)
                    is_cpu_bound = False


                if measurement.remote_dram > config.REMOTE_MEMORY_ACCESS_THRESHOLD_PER_TASK:
                    classifications[socket].is_remote_dram.append(cpu)
                    is_cpu_bound = False

                if measurement.memory_bandwidth > config.MEMORY_UTILIZATION_THRESHOLD_PER_TASK:
                    classifications[socket].is_memory_bound.append(cpu)
                    is_cpu_bound = False

                # if measurement.cycles == 0:
                if measurement.cycles > config.IDLE_THRESHOLD_PER_TASK:
                    classifications[socket].is_idle.append(cpu)
                    is_cpu_bound = False

                if is_cpu_bound:
                    classifications[socket].is_cpu_bound.append(cpu)

        return classifications




    def _init_available_hardware(self):
        _CPU_FIELDS = 'CPU,Socket'
        CPU = namedtuple('CPU', _CPU_FIELDS)

        lscpu_commnad = 'lscpu -p={}'.format(_CPU_FIELDS)
        stdout = subprocess.check_output(lscpu_commnad.split())

        # Stripping comments from stdout.
        cpus = [line for line in stdout.splitlines() if not line.startswith(b'#')]

        for cpu_line in cpus:
            cpu_params_str_format = cpu_line.split(b',')
            cpu_params_int_format = map(int, cpu_params_str_format)
            cpu = CPU(*cpu_params_int_format)

            if cpu.Socket in self._available_hardware:
                self._available_hardware[cpu.Socket].append(cpu.CPU)
            else:
                self._available_hardware[cpu.Socket] = [cpu.CPU]

    def _compute_measurements(self, counters):
        measurements = []
        for cpu in counters:
            inter_socket_coherence = counters[cpu]['mem_load_uops_l3_miss_retired_remote_hitm'] + \
                                            counters[cpu]['mem_load_uops_l3_miss_retired_remote_fwd']

            intra_socket_coherence = counters[cpu]['mem_load_uops_retired_l2_miss'] - \
                                                      (counters[cpu]['mem_load_uops_retired_l3_miss'] +
                                                       counters[cpu]['mem_load_uops_retired_l3_hit'])

            remote_dram = counters[cpu]['mem_load_uops_l3_miss_retired_remote_dram']

            memory_bandwidth = counters[cpu]['LLC-misses']

            instructions = counters[cpu]['instructions']
            cycles = counters[cpu]['cycles']



            measurements.append(Measurement(cpu=cpu,
                                            inter_socket_coherence=inter_socket_coherence,
                                            intra_socket_coherence=intra_socket_coherence,
                                            remote_dram=remote_dram,
                                            memory_bandwidth=memory_bandwidth,
                                            instructions=instructions,
                                            cycles=cycles))

        return measurements

    def _collect_performance_counters(self):
        _PERF_COMMAND_TEMPLATE = './pmu-tools-r106/ocperf.py stat {events} {all_cores} {no_aggregate} {create_csv} ' \
                                 'sleep {interval_seconds}'

        monitored_events = '-e {}'.format(','.join(config.PERF_EVENTS))

        formatted_perf_command = _PERF_COMMAND_TEMPLATE.format(events=monitored_events,
                                                               all_cores='-a',
                                                               no_aggregate='-A',
                                                               create_csv='-x ,',
                                                               interval_seconds=config.REMAPPING_INTERVAL_SECONDS)

        ocperf = subprocess.Popen(formatted_perf_command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = ocperf.communicate()

        if ocperf.returncode != 0:
            raise RuntimeError('ocperf failed!, retcode={}\nstdout={}\nstderr={}'.format(ocperf.returncode,
                                                                                         stdout,
                                                                                         stderr))

        counters = {}

        # Init default counters
        for socket in self._available_hardware:
            for cpu in self._available_hardware[socket]:
                counters[cpu] = {}

        parser = csv.DictReader(stderr.decode('utf-8').splitlines(),
                                fieldnames=['cpu_name', 'value', 'blank', 'event_name', 'timestamp', 'scale'])

        for row in parser:
            counter_name = row['event_name']
            cpu_id = int(re.findall('\d+', row['cpu_name'])[0]) # output is in format CPU#, we want only the #.
            value = row['value']
            # Sometimes, perf output an invalid value. this is meant to handle it.
            try:
                counters[cpu_id][counter_name] = int(value)
            except:
                counters[cpu_id][counter_name] = 0

        return counters

