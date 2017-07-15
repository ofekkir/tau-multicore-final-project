from collections import namedtuple
import subprocess


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
