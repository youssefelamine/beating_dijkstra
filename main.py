# main.py
import csv
import config
import argparse
from pathlib import Path
from benchmark import (
    benchmark_tree, benchmark_er, benchmark_ba, benchmark_ws,
    benchmark_grid_2d_mesh, benchmark_grid_3d_mesh, benchmark_torus, benchmark_complete_graph,
    benchmark_leafspine, benchmark_fattree, benchmark_generic
)
from dataset_loader import load_dataset

# --------------------------
# CLI Argument Parser
# --------------------------
parser = argparse.ArgumentParser(
    description="Graph benchmark suite with synthetic and dataset support"
)
parser.add_argument(
    "--synthetic",
    action="store_true",
    help="Run synthetic graph benchmarks (default)"
)
parser.add_argument(
    "--dataset",
    type=str,
    default=None,
    help="Run benchmarks on a dataset (name of dataset in datasets/ directory)"
)
args = parser.parse_args()

# Determine mode
if args.dataset:
    MODE = "dataset"
    DATASET_NAME = args.dataset
elif args.synthetic:
    MODE = "synthetic"
    DATASET_NAME = None
else:
    # Default to config values
    MODE = config.GRAPH_MODE
    DATASET_NAME = config.DATASET_NAME
    # If config says synthetic or no dataset specified, use synthetic
    if not DATASET_NAME:
        MODE = "synthetic"

print(f"\n{'='*60}")
print(f"Mode: {MODE.upper()}")
if MODE == "dataset":
    print(f"Dataset: {DATASET_NAME}")
print(f"{'='*60}\n")

# --------------------------
# Configuration from config.py
# --------------------------
repeats = config.REPEATS
source_counts = config.SOURCE_COUNT
dataset_path = config.DATASET_PATH

# Set output file based on mode
if MODE == "dataset":
    output_file = f"results/{DATASET_NAME}.csv"
else:
    output_file = config.OUTPUT_CSV

# Ensure results directory exists
Path("results").mkdir(exist_ok=True)

# Synthetic parameters
tree_sizes = config.TREE_SIZES
er_params = config.ER_PARAMS
ba_params = config.BA_PARAMS
ws_params = config.WS_PARAMS
grid2d_sizes = config.GRID2D_SIZES
grid3d_sizes = config.GRID3D_SIZES
torus_sizes = config.TORUS_SIZES
complete_sizes = config.COMPLETE_SIZES
leafspine_params = config.LEAFSPINE_PARAMS
fattree_sizes = config.FATTREE_SIZES

# --------------------------
# Helper function to append results
# --------------------------
def append_results_to_csv(results, extra_params=None):
    fieldnames = ["graph_type","n_nodes","n_sources","n_edges","run_id","algorithm","runtime","memory_peak","seed","extra_params"]
    write_header = False
    try:
        with open(output_file, "r"):
            pass
    except FileNotFoundError:
        write_header = True

    with open(output_file, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for row in results:
            row_copy = row.copy()
            row_copy["extra_params"] = extra_params
            writer.writerow(row_copy)

# --------------------------
# Main benchmark loop
# --------------------------

if MODE == "dataset":
    # ========================
    # DATASET MODE
    # ========================
    try:
        G, node_to_id, id_to_node = load_dataset(DATASET_NAME, dataset_path)
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        exit(1)
    
    print(f"Dataset loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges\n")
    
    for run_id in range(repeats):
        seed = run_id
        print(f"=== Dataset Run {run_id+1}/{repeats} ===")
        
        for source_count in source_counts:
            print(f"--- Source Count: {source_count} ---")
            
            # Adjust source count to dataset size
            actual_source_count = min(source_count, G.number_of_nodes())
            
            # Create a loader function that returns the pre-loaded graph
            def dataset_loader(**kwargs):
                return G, node_to_id, id_to_node
            
            # Run generic benchmark with dataset graph
            res = benchmark_generic(
                graph_type=DATASET_NAME,
                gen_func=dataset_loader,
                gen_params={},
                source_count=actual_source_count,
                run_id=run_id,
                seed=seed
            )
            
            append_results_to_csv(res, extra_params=f"dataset={DATASET_NAME}")

else:
    # ========================
    # SYNTHETIC MODE
    # ========================
    for run_id in range(repeats):
        seed = run_id
        print(f"=== Repetition {run_id+1}/{repeats} ===")

        for source_count in source_counts:
            print(f"\n--- Source Count: {source_count} ---")

            # --- Trees ---
            for n in tree_sizes:
                print(f"Running Tree n={n}, sources={source_count}")
                res = benchmark_tree(n_nodes=n, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res)

            # --- ER ---
            for params in er_params:
                print(f"Running ER n={params['n_nodes']} p={params['p']}, sources={source_count}")
                res = benchmark_er(**params, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"p={params['p']}")

            # --- BA ---
            for params in ba_params:
                print(f"Running BA n={params['n_nodes']} m={params['m']}, sources={source_count}")
                res = benchmark_ba(**params, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"m={params['m']}")

            # --- WS ---
            for params in ws_params:
                print(f"Running WS n={params['n_nodes']} k={params['k']} p={params['p']}, sources={source_count}")
                res = benchmark_ws(**params, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"k={params['k']},p={params['p']}")

            # --- Grid 2D ---
            for rows, cols in grid2d_sizes:
                print(f"Running Grid 2D {rows}x{cols}, sources={source_count}")
                res = benchmark_grid_2d_mesh(rows, cols, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"rows={rows},cols={cols}")

            # --- Grid 3D ---
            for x, y, z in grid3d_sizes:
                print(f"Running Grid 3D {x}x{y}x{z}, sources={source_count}")
                res = benchmark_grid_3d_mesh(x, y, z, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"x={x},y={y},z={z}")

            # --- Torus ---
            for rows, cols in torus_sizes:
                print(f"Running Torus {rows}x{cols}, sources={source_count}")
                res = benchmark_torus(rows, cols, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"rows={rows},cols={cols}")

            # --- Complete Graph ---
            for n in complete_sizes:
                print(f"Running Complete Graph n={n}, sources={source_count}")
                res = benchmark_complete_graph(n, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res)

            # --- Leaf-Spine ---
            for params in leafspine_params:
                print(f"Running Leaf-Spine n_leaves={params['leaves']} n_spines={params['spines']}, sources={source_count}")
                res = benchmark_leafspine(**params, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"n_leaves={params['leaves']},n_spines={params['spines']}")

            # --- Fat-Tree ---
            for k in fattree_sizes:
                print(f"Running Fat-Tree k={k}, sources={source_count}")
                res = benchmark_fattree(k, source_count=source_count, seed=seed, run_id=run_id)
                append_results_to_csv(res, extra_params=f"k={k}")

print("\n=== All benchmarks completed ===")