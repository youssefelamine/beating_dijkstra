# config_stress_topologies.py
"""
Run 4: Stress / worst-case-ish topologies.
Dense (complete), high-degree, and high-diameter structures:
3D grids, tori, fat-tree, leaf–spine, large trees.
Used to understand overheads and limits of BMSSP vs Dijkstra.
"""

# ----------------------------
# General Settings
# ----------------------------
REPEATS = 3          # high-cost graphs
SEED = 42
OUTPUT_CSV = "results/demo_project.csv"

# Stress multi-source as well
SOURCE_COUNT = [1, 8, 16]

# Graph Mode Configuration
# ----------------------------
GRAPH_MODE = "synthetic"  # "synthetic" or "dataset"
DATASET_NAME = None        # Dataset name (only used if GRAPH_MODE="dataset")
DATASET_PATH = "datasets"  # Root directory for datasets


# ----------------------------
# Graph Sizes (stress)
# ----------------------------
# Large trees (unbalanced shortest-path trees)
TREE_SIZES = [10000, 100000]

# Skip random families to keep runtime manageable here
ER_PARAMS = []
BA_PARAMS = []
WS_PARAMS = []

# High-diameter structured graphs
GRID2D_SIZES = []  # covered in Run 2
GRID3D_SIZES = [
    (5, 5, 5),
    (10, 10, 10),
]

# Cyclic regular structures
TORUS_SIZES = [
    (10, 10),
]

# Dense graphs
COMPLETE_SIZES = [
    10,
    50,
]

# Datacenter-like topologies
LEAFSPINE_PARAMS = [
    {"leaves": 10, "spines": 5},
]

FATTREE_SIZES = [8]

# ----------------------------
# Graph-specific parameters
# ----------------------------
ER_P = 0.1
BA_M = 2
WS_K = 4
WS_P = 0.2

# ----------------------------
# Benchmark Algorithms
# ----------------------------
ALGORITHMS = ["Dijkstra", "BMSSP"]
