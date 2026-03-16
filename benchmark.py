# benchmark.py
import time
import tracemalloc
import csv
from bmsspy import Bmssp
import networkx as nx
from graphs import (
    generate_tree, to_bmsspy_format,
    generate_fat_tree, generate_leaf_spine, generate_er_graph, generate_ba_graph, generate_ws_graph,
    generate_grid_2d, generate_grid_3d, generate_torus, generate_complete_graph
)


def measure_runtime_and_memory(func, *args, **kwargs):
    """
    Execute function and measure runtime + peak memory.
    Returns: (result, runtime, memory_peak_kb)
    """
    tracemalloc.start()
    start = time.perf_counter()
    result = func(*args, **kwargs)
    runtime = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, runtime, peak / 1024  # KB


def benchmark_generic(graph_type, gen_func, gen_params, src_nodes=None, source_count=1, run_id=0, seed=None):
    """
    Generic benchmark function for any graph type with multi-source support.
    
    Args:
        graph_type (str): Name for results (e.g., "tree", "ER", "grid_2d")
        gen_func: Graph generator function
        gen_params (dict): Parameters to pass to gen_func
        src_nodes (list): List of source node indices (if None, use first source_count nodes)
        source_count (int): Number of source nodes to benchmark
        run_id (int): Run identifier
        seed (int): Random seed
    
    Returns:
        list of result dicts (one per algorithm)
    """
    # Generate graph
    G, node_to_id, id_to_node = gen_func(**gen_params)
    
    # Determine source nodes
    if src_nodes is None:
        available_nodes = list(G.nodes())
        src_nodes = available_nodes[:min(source_count, len(available_nodes))]
    
    actual_source_count = len(src_nodes)
    src_ids = [node_to_id[node] for node in src_nodes]
    
    # Convert to BMSSP format
    bmssp_graph = to_bmsspy_format(G, node_to_id)
    
    results = []
    
    # Dijkstra benchmark - run for each source and accumulate time/memory
    dijkstra_time_total = 0
    dijkstra_mem_total = 0
    
    for src_node in src_nodes:
        _, time_taken, mem_peak = measure_runtime_and_memory(
            nx.single_source_dijkstra_path_length, G, src_node
        )
        dijkstra_time_total += time_taken
        dijkstra_mem_total = max(dijkstra_mem_total, mem_peak)
    
    results.append({
        "graph_type": graph_type,
        "n_nodes": len(G),
        "n_sources": actual_source_count,
        "n_edges": G.number_of_edges(),
        "run_id": run_id,
        "algorithm": "Dijkstra",
        "runtime": dijkstra_time_total,
        "memory_peak": dijkstra_mem_total,
        "seed": seed
    })
    
    # BMSSP benchmark - run for each source and accumulate time/memory
    bmssp_time_total = 0
    bmssp_mem_total = 0
    
    solver = Bmssp(bmssp_graph)
    for src_id in src_ids:
        _, time_taken, mem_peak = measure_runtime_and_memory(
            solver.solve, origin_id=src_id
        )
        bmssp_time_total += time_taken
        bmssp_mem_total = max(bmssp_mem_total, mem_peak)
    
    results.append({
        "graph_type": graph_type,
        "n_nodes": len(G),
        "n_sources": actual_source_count,
        "n_edges": G.number_of_edges(),
        "run_id": run_id,
        "algorithm": "BMSSP",
        "runtime": bmssp_time_total,
        "memory_peak": bmssp_mem_total,
        "seed": seed
    })
    
    return results

def benchmark_tree(n_nodes, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark tree graph with multi-source support."""
    return benchmark_generic(
        "tree",
        generate_tree,
        {"n_nodes": n_nodes, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )

def run_multiple_trees(sizes, repeats=3, weight_range=(1,10), source_node=0, output_file="results.csv"):
    """
    Run benchmarks on multiple tree sizes and repeat each experiment.
    Stores results in CSV.
    """
    fieldnames = ["graph_type", "n_nodes", "n_edges", "run_id", "algorithm", "runtime", "memory_peak", "seed"]
    with open(output_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for n in sizes:
            for run_id in range(repeats):
                seed = run_id  # optional fixed seed per repeat
                print(f"Running benchmark: tree size={n}, run={run_id}")
                results = benchmark_tree(n, weight_range, source_node, seed, run_id)
                for row in results:
                    writer.writerow(row)


# RANDOM GRAPHS

def benchmark_er(n_nodes, p=0.1, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark Erdős–Rényi graph with multi-source support."""
    return benchmark_generic(
        "ER",
        generate_er_graph,
        {"n_nodes": n_nodes, "p": p, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )


def benchmark_ba(n_nodes, m=2, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark Barabási–Albert graph with multi-source support."""
    return benchmark_generic(
        "BA",
        generate_ba_graph,
        {"n_nodes": n_nodes, "m": m, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )

def benchmark_grid_2d_mesh(rows, cols, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark 2D grid/mesh graph with multi-source support."""
    return benchmark_generic(
        "grid_2d",
        generate_grid_2d,
        {"rows": rows, "cols": cols, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )


def benchmark_grid_3d_mesh(x, y, z, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark 3D grid graph with multi-source support."""
    return benchmark_generic(
        "grid_3d",
        generate_grid_3d,
        {"x": x, "y": y, "z": z, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )


def benchmark_torus(rows, cols, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark torus graph with multi-source support."""
    return benchmark_generic(
        "torus",
        generate_torus,
        {"rows": rows, "cols": cols, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )


def benchmark_complete_graph(n_nodes, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark complete graph with multi-source support."""
    return benchmark_generic(
        "complete",
        generate_complete_graph,
        {"n_nodes": n_nodes, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )


def benchmark_ws(n_nodes, k=4, p=0.2, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark Watts–Strogatz graph with multi-source support."""
    return benchmark_generic(
        "WS",
        generate_ws_graph,
        {"n_nodes": n_nodes, "k": k, "p": p, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )



def benchmark_leafspine(leaves, spines, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark leaf-spine datacenter topology with multi-source support."""
    return benchmark_generic(
        "leafspine",
        generate_leaf_spine,
        {"n_leaf": leaves, "n_spine": spines, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )


def benchmark_fattree(k, weight_range=(1,10), source_count=1, seed=None, run_id=0):
    """Benchmark fat-tree datacenter topology with multi-source support."""
    return benchmark_generic(
        "fattree",
        generate_fat_tree,
        {"k": k, "weight_range": weight_range, "seed": seed},
        source_count=source_count,
        run_id=run_id,
        seed=seed
    )