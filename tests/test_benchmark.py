# test_benchmark.py
from benchmark import benchmark_tree

results = benchmark_tree(n_nodes=10, weight_range=(1,5), source_node=0, seed=42, run_id=0)
for r in results:
    print(r)