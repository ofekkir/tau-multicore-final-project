from collections import namedtuple
import subprocess
import csv
import re

import config

MEASUREMENTS_FIELDS = 'cpu,inter_socket_coherence,intra_socket_coherence,remote_dram,memory_bandwidth,instructions,cycles'
Measurement = namedtuple('Measurements', MEASUREMENTS_FIELDS)

class Sam(object):
    def __init__(self):
        super(Sam, self).__init__()
        self._available_hardware = []
        self._init_available_hardware()

    def run(selfs):
        while True:
            counters = selfs._collect_performance_counters()
            measurments = selfs._compute_measurements(counters)

            import pprint
            pprint.pprint(measurments)

            return

    def _init_available_hardware(self):
        _CPU_FIELDS = 'CPU,Core,Socket'
        CPU = namedtuple('CPU', _CPU_FIELDS)

        lscpu_commnad = 'lscpu -p={}'.format(_CPU_FIELDS)
        stdout = subprocess.check_output(lscpu_commnad.split())
        for line in stdout.splitlines():
            # Stripping comments from stdout.
            if line.startswith(b'#'):
                continue

            cpu_params_str_format = line.split(b',')
            cpu_params_int_format = map(int, cpu_params_str_format)
            self._available_hardware.append(CPU(*cpu_params_int_format))

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
        for cpu in range(len(self._available_hardware)):
            counters[cpu] = {}

        parser = csv.DictReader(stderr.decode('utf-8').splitlines(), fieldnames=['cpu_name', 'value', 'blank', 'event_name', 'timestamp', 'scale'])

        for row in parser:
            counter_name = row['event_name']
            cpu_id = int(re.findall('\d+', row['cpu_name'])[0]) # output is in format CPU#, we want only the #.
            counters[cpu_id][counter_name] = int(row['value'])

        return counters

