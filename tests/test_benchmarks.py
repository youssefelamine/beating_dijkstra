# test_benchmarks.py
from benchmark import (
    benchmark_tree, benchmark_er, benchmark_ba, benchmark_ws,
    benchmark_grid_2d_mesh, benchmark_grid_3d_mesh, benchmark_torus, benchmark_complete_graph,
    benchmark_leafspine, benchmark_fattree
)

def run_all_tests():
    tests = [
        ("Tree", benchmark_tree, {"n_nodes": 10, "seed": 42}),
        ("ER", benchmark_er, {"n_nodes": 20, "p": 0.2, "seed": 42}),
        ("BA", benchmark_ba, {"n_nodes": 20, "m": 2, "seed": 42}),
        ("WS", benchmark_ws, {"n_nodes": 20, "k": 4, "p": 0.3, "seed": 42}),
        ("Grid 2D", benchmark_grid_2d_mesh, {"rows": 3, "cols": 3, "seed": 42}),
        ("Grid 3D", benchmark_grid_3d_mesh, {"x": 2, "y": 2, "z": 2, "seed": 42}),
        ("Torus", benchmark_torus, {"rows": 3, "cols": 3, "seed": 42}),
        ("Complete Graph", benchmark_complete_graph, {"n_nodes": 5, "seed": 42}),
        ("Leaf-Spine", benchmark_leafspine, {"leaves": 3, "spines": 2, "seed": 42}),
        ("Fat-Tree", benchmark_fattree, {"k": 4, "seed": 42}),
    ]

    for name, func, params in tests:
        print(f"\n=== Running {name} benchmark ===")
        results = func(**params)
        for res in results:
            print(res)

if __name__ == "__main__":
    run_all_tests()