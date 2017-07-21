REMAPPING_INTERVAL_SECONDS = 0.1 # 100 ms

INTER_SOCKET_COHERENCE_THRESHOLD_PER_TASK = 1
MEMORY_UTILIZATION_THRESHOLD_PER_TASK = 1
REMOTE_MEMORY_ACCESS_THRESHOLD_PER_TASK = 1

PERF_EVENTS = \
    {
        # Intra socket coherence
        'MEM_LOAD_UOPS_RETIRED_L2_MISS' : 'rD110',
        'MEM_LOAD_UOPS_RETIRED_L3_MISS' : 'rD120',
        'MEM_LOAD_UOPS_RETIRED_L3_HIT' : 'rD104',
        # Remote DRAM
        'MEM_LOAD_UOPS_LLC_MISS_RETIRED_REMOTE_DRAM' : 'rD304',
        # Inter socket coherence
        'MEM_LOAD_UOPS_LLC_MISS_RETIRED_REMOTE_HITM' : 'rD310',
        'MEM_LOAD_UOPS_LLC_MISS_RETIRED_REMOTE_FWD' : 'rD320',
        # Memory bandwidth
        'LLC_MISSES' : 'LLC-misses',

        # 'UNHALTED_CYCLES' : 'r003C',

        'INSTRUCTIONS' : 'instructions',
        'CYCLES' : 'cycles'
    }

