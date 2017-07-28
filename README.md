# tau-multicore-final-project

Prerequisites:
1. install psutil (pip3 install psutil)
2. install lscpu

Git structure:
1. root dir - contains operational SAM (pay attention to it's configuration file, specifically the param: OPTIMIZE_ONLY_PROCESSES_OF_USER)
2. benchmarks - contains our src and measurments results. specifically, the intersocket and memory bandwidth thresholds measurment, 
	and the syntethic intersocket coherence benchmark.
3. pmu-tools - intels perf wrapper.
4. threshold-measurments - utils for parsing results.