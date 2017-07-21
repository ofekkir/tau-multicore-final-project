from collections import namedtuple
import subprocess
import csv
import re

import config

class Sam(object):
    def __init__(self):
        super(Sam, self).__init__()
        self._available_hardware = []
        self._init_available_hardware()

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

    def _collect_performance_counters(self):
        _PERF_COMMAND_TEMPLATE = 'perf stat {events} {all_cores} {no_aggregate} {create_csv} {use_stdout} ' \
                                 'sleep {interval_seconds}'

        monitored_events = '-e {}'.format(','.join(config.PERF_EVENTS.values()))

        formatted_perf_command = _PERF_COMMAND_TEMPLATE.format(events=monitored_events,
                                                               all_cores='-a',
                                                               no_aggregate='-A',
                                                               create_csv='-x ,',
                                                               use_stdout='--log-fd 1',
                                                               interval_seconds=config.REMAPPING_INTERVAL_SECONDS)

        stdout = subprocess.check_output(formatted_perf_command.split())

        counters = {}

        # Init default counters
        for cpu in range(len(self._available_hardware)):
            counters[cpu] = {}

        inverse_counter_names_map = {v: k for k, v in config.PERF_EVENTS.items()}
        parser = csv.DictReader(stdout.decode('utf-8').splitlines(), fieldnames=['cpu_name', 'value', 'blank', 'event_name', 'timestamp', 'scale'])

        for row in parser:
            counter_name = inverse_counter_names_map[row['event_name']]
            cpu_id = int(re.findall('\d+', row['cpu_name'])[0]) # output is in format CPU#, we want only the #.
            counters[cpu_id][counter_name] = int(row['value'])

        print(counters)

