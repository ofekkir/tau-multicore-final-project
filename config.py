REMAPPING_INTERVAL_SECONDS = 0.1 # 100 ms

INTER_SOCKET_COHERENCE_THRESHOLD_PER_TASK = 1
INTRA_SOCKET_COHERENCE_THRESHOLD_PER_TASK = INTER_SOCKET_COHERENCE_THRESHOLD_PER_TASK
MEMORY_UTILIZATION_THRESHOLD_PER_TASK = 1
REMOTE_MEMORY_ACCESS_THRESHOLD_PER_TASK = 1

PERF_EVENTS = \
    [
        # Intra socket coherence
        # Retired load uops with L2 cache hits as data sources.
        'mem_load_uops_retired_l2_miss',
        # Retired load uops whose data source is LLC miss.
        'mem_load_uops_retired_l3_miss',
        # Retired load uops whose data source was LLC hit with no snoop required.
        'mem_load_uops_retired_l3_hit',

        # Remote DRAM
        # Retired load uops whose data source was remote DRAM.
        'mem_load_uops_l3_miss_retired_remote_dram',

        # Inter socket coherence
        # Retired load uops whose data source was remote HITM.
        'mem_load_uops_l3_miss_retired_remote_hitm',
        # Retired load uops whose data source was forwards from a remote cache.
        'mem_load_uops_l3_miss_retired_remote_fwd',

        # Memory bandwidth
        'LLC-misses',

        # 'UNHALTED_CYCLES' : 'r003C',

        'instructions',
        'cycles'
    ]

