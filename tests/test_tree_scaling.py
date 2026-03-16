# test_tree_scaling.py

import csv
from benchmark import benchmark_tree

# =========================
# CONFIGURATION
# =========================

SIZES = [10, 50, 100, 500, 1000, 2000]
REPEATS = 3
WEIGHT_RANGE = (1, 10)
SEED_BASE = 42
OUTPUT_FILE = "tree_scaling_results.csv"


# =========================
# RUN EXPERIMENT
# =========================

all_results = []

for n in SIZES:
    print(f"\nRunning size n = {n}")
    
    for r in range(REPEATS):
        seed = SEED_BASE + r
        
        results = benchmark_tree(
            n_nodes=n,
            weight_range=WEIGHT_RANGE,
            source_node=0,
            seed=seed,
            run_id=r
        )
        
        all_results.extend(results)


# =========================
# SAVE CSV
# =========================

keys = all_results[0].keys()

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    writer.writerows(all_results)

print(f"\nFinished. Results saved to {OUTPUT_FILE}")