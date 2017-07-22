class Classification(object):
    def __init__(self, is_inter, is_intra, is_remote_dram, is_memory_bound, is_idle, is_cpu_bound):
        self.is_inter = is_inter
        self.is_intra = is_intra
        self.is_remote_dram = is_remote_dram
        self.is_memory_bound = is_memory_bound
        self.is_idle = is_idle
        self.is_cpu_bound = is_cpu_bound

