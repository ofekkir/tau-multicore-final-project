REMAPPING_INTERVAL_SECONDS = 0.1 # 100 ms

INTER_SOCKET_COHERENCE_THRESHOLD_PER_TASK = 1
MEMORY_UTILIZATION_THRESHOLD_PER_TASK = 1
REMOTE_MEMORY_ACCESS_THRESHOLD_PER_TASK = 1

PERF_EVENTS = \
    [
        # Intra socket coherence
        'mem_load_uops_retired_l2_miss',
        'mem_load_uops_retired_l3_miss',
        'mem_load_uops_retired_l3_hit',
        # Remote DRAM
        'mem_load_uops_l3_miss_retired_remote_dram',
        # Inter socket coherence
        'mem_load_uops_l3_miss_retired_remote_hitm',
        'mem_load_uops_l3_miss_retired_remote_fwd',
        # Memory bandwidth
        'LLC-misses',

        # 'UNHALTED_CYCLES' : 'r003C',

        'instructions',
        'cycles'
    ]

