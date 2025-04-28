PACKAGE=purem_sandbox
BENCHMARKS_PLATFORM=Darwin-CPython-3.11-64bit
TEST=00
LAST_TEST_ID=00

all:
	@echo "Nothing to do by default. Use 'make test' or 'make plot'."
.PHONY: all

benchmarks:
	@timestamp=$$(date +%Y%m%d_%H%M%S) && \
    	for size in 30000 50000 100000 150000 200000 300000 500000 1000000 2000000 5000000; do \
    		echo "Running tests for size = $$size"; \
    		ARRAY_SIZE=$$size pytest src/performance_test.py --color=yes -p no:warnings --disable-warnings --benchmark-sort=max --benchmark-disable-gc --benchmark-columns=min,max,mean,stddev,ops --benchmark-min-rounds=35 --benchmark-save=$${timestamp}_$${size}; \
    	done
.PHONY: benchmarks

plot:
	@LAST_TEST_ID=$$(find .benchmarks/Darwin-CPython-3.11-64bit -name '*.json' | sort | tail -n 1 | sed -E 's#.*/([0-9]+)_.*#\1#'); \
    	echo "Benchmarks with LAST_TEST_ID=$$LAST_TEST_ID are plotting..."; \
    	python -m src.performance_plots $$LAST_TEST_ID $$BENCHMARKS_PLATFORM
.PHONY: plot


test: benchmarks plot
	echo "Purem Benchmarks successfully validated various performance."
.PHONY: test