import sys

from src.benchmarks_analysis import BenchmarksAnalysis

if __name__ == "__main__":
    test_id = sys.argv[1]
    print(f"Working with file: {test_id}")

    BenchmarksAnalysis(test_id).run()