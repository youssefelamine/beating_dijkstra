"""
synthetic_plots.py
Unified visualization for synthetic graph benchmarks across three categories:
  1. Grid topologies (2D grids; plots_grids.py)
  2. Random sparse graphs (ER, BA, WS; plots_random.py)
  3. Stress topologies (trees, 3D grids, torus, complete, leaf-spine, fat-tree; plots_stress.py)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Ensure plots directory exists
Path("plots").mkdir(exist_ok=True)

# ========================
# 1. GRID TOPOLOGIES
# ========================

def plot_grids():
    """Plot runtime, ratio, and memory for 2D grid topologies."""
    print("\n=== Generating Grid Plots ===")
    
    try:
        df_small = pd.read_csv("results/grids_scaling.csv")
        df_large = pd.read_csv("results/grids_scaling_large_rect.csv")
        df = pd.concat([df_small, df_large], ignore_index=True)
    except FileNotFoundError as e:
        print(f"  ⚠ Grid data not found: {e}")
        return
    
    # Filter for grid_2d, single source
    df = df[(df["graph_type"] == "grid_2d") & (df["n_sources"] == 1)]
    
    # Aggregate mean runtimes and memory
    agg = df.groupby(["n_nodes", "algorithm"]).agg(
        runtime_mean=("runtime", "mean"),
        memory_mean=("memory_peak", "mean")
    ).reset_index()
    
    # Pivot for easier plotting
    pivot_rt = agg.pivot(index="n_nodes", columns="algorithm", values="runtime_mean")
    pivot_mem = agg.pivot(index="n_nodes", columns="algorithm", values="memory_mean")
    
    sizes = pivot_rt.index.values
    
    # Plot A: runtime vs n_nodes
    plt.figure(figsize=(10, 6))
    for algo, style in [("Dijkstra", "o-"), ("BMSSP", "s-")]:
        plt.plot(sizes, pivot_rt[algo], style, label=algo, linewidth=2.5, markersize=8)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of nodes (n)")
    plt.ylabel("Runtime (s)")
    plt.title("Runtime of BMSSP and Dijkstra on 2D grids")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("plots/grid_runtime.png", dpi=150)
    plt.close()
    print("  ✓ grid_runtime.png")
    
    # Plot B: ratio vs n_nodes
    ratio = pivot_rt["BMSSP"] / pivot_rt["Dijkstra"]
    
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, ratio, "o-", linewidth=2.5, markersize=8)
    plt.xscale("log")
    plt.xlabel("Number of nodes (n)")
    plt.ylabel("Runtime ratio BMSSP / Dijkstra")
    plt.title("Runtime ratio on 2D grids as size increases")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("plots/grid_ratio.png", dpi=150)
    plt.close()
    print("  ✓ grid_ratio.png")
    
    # Plot C: memory vs n_nodes
    plt.figure(figsize=(10, 6))
    for algo, style, alpha in [("Dijkstra", "o-", 0.7), ("BMSSP", "s--", 0.7)]:
        plt.plot(
            sizes,
            pivot_mem[algo] / 1024,
            style,
            label=algo,
            linewidth=2.5,
            markersize=8,
            alpha=alpha
        )
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Number of nodes (n)")
    plt.ylabel("Peak memory (MB)")
    plt.title("Peak memory usage of BMSSP and Dijkstra on 2D grids")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("plots/grid_memory.png", dpi=150)
    plt.close()
    print("  ✓ grid_memory.png")


# ========================
# 2. RANDOM SPARSE GRAPHS
# ========================

def plot_random():
    """Plot runtime, memory, and multi-source scaling for random sparse graphs."""
    print("\n=== Generating Random Sparse Plots ===")
    
    try:
        df = pd.read_csv("results/random_sparse.csv")
    except FileNotFoundError as e:
        print(f"  ⚠ Random graph data not found: {e}")
        return
    
    # Filter for 1 source to keep plots clean
    df1 = df[df["n_sources"] == 1]
    
    # Aggregate mean runtime and memory
    agg = df1.groupby(["graph_type", "n_nodes", "algorithm"]).agg(
        runtime_mean=("runtime", "mean"),
        memory_mean=("memory_peak", "mean")
    ).reset_index()
    
    # Compute ratio = BMSSP / Dijkstra
    pivot_rt = agg.pivot(index=["graph_type", "n_nodes"], columns="algorithm", values="runtime_mean")
    pivot_rt["ratio"] = pivot_rt["BMSSP"] / pivot_rt["Dijkstra"]
    ratio_df = pivot_rt.reset_index()
    
    graph_order = ["ER", "BA", "WS"]
    size_order = sorted(ratio_df["n_nodes"].unique())
    
    # Plot A: Runtime ratio bar chart
    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=ratio_df,
        x="graph_type",
        y="ratio",
        hue="n_nodes",
        order=graph_order,
        hue_order=size_order
    )
    plt.yscale("log")
    plt.xlabel("Graph type")
    plt.ylabel("Runtime ratio BMSSP / Dijkstra")
    plt.title("BMSSP vs Dijkstra on random sparse graphs (n_sources=1)")
    plt.legend(title="n_nodes")
    plt.tight_layout()
    plt.savefig("plots/random_ratio_bar.png", dpi=150)
    plt.close()
    print("  ✓ random_ratio_bar.png")
    
    # Plot B: Runtime trends per graph type
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    
    for ax, g in zip(axes, graph_order):
        sub = agg[(agg["graph_type"] == g)]
        for algo, style in [("Dijkstra", "o-"), ("BMSSP", "s-")]:
            sdata = sub[sub["algorithm"] == algo].sort_values("n_nodes")
            ax.plot(sdata["n_nodes"], sdata["runtime_mean"], style, label=algo, linewidth=2, markersize=7)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(g)
        ax.set_xlabel("n_nodes")
        ax.grid(True, which="both", ls=":", alpha=0.3)
    
    axes[0].set_ylabel("Runtime (s)")
    axes[0].legend()
    fig.suptitle("Runtime vs size on random sparse graphs (n_sources=1)")
    plt.tight_layout()
    plt.savefig("plots/random_runtime_trends.png", dpi=150)
    plt.close()
    print("  ✓ random_runtime_trends.png")
    
    # Plot C: Memory ratio
    pivot_mem = agg.pivot(index=["graph_type", "n_nodes"], columns="algorithm", values="memory_mean")
    pivot_mem["mem_ratio"] = pivot_mem["BMSSP"] / pivot_mem["Dijkstra"]
    mem_df = pivot_mem.reset_index()
    
    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=mem_df,
        x="graph_type",
        y="mem_ratio",
        hue="n_nodes",
        order=graph_order,
        hue_order=size_order
    )
    plt.yscale("log")
    plt.xlabel("Graph type")
    plt.ylabel("Memory ratio BMSSP / Dijkstra")
    plt.title("Peak memory ratio on random sparse graphs (n_sources=1)")
    plt.legend(title="n_nodes")
    plt.tight_layout()
    plt.savefig("plots/random_memory_ratio.png", dpi=150)
    plt.close()
    print("  ✓ random_memory_ratio.png")
    
    # Plot D: Multi-source scaling (pick largest size per graph type: n_nodes = 500)
    df500 = df[df["n_nodes"] == 500]
    
    agg_ns = df500.groupby(["graph_type", "n_sources", "algorithm"]).agg(
        runtime_mean=("runtime", "mean")
    ).reset_index()
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    
    for ax, g in zip(axes, graph_order):
        sub = agg_ns[agg_ns["graph_type"] == g]
        for algo, style in [("Dijkstra", "o-"), ("BMSSP", "s-")]:
            sd = sub[sub["algorithm"] == algo].sort_values("n_sources")
            ax.plot(sd["n_sources"], sd["runtime_mean"], style, label=algo, linewidth=2, markersize=7)
        ax.set_xticks(sorted(sub["n_sources"].unique()))
        ax.set_xlabel("n_sources")
        ax.set_yscale("log")
        ax.set_title(f"{g}, n=500")
        ax.grid(True, which="both", ls=":", alpha=0.3)
    
    axes[0].set_ylabel("Runtime (s)")
    axes[0].legend()
    fig.suptitle("Scaling with number of sources on random graphs")
    plt.tight_layout()
    plt.savefig("plots/random_multisource.png", dpi=150)
    plt.close()
    print("  ✓ random_multisource.png")


# ========================
# 3. STRESS TOPOLOGIES
# ========================

def plot_stress():
    """Plot runtime, memory, and ratio analysis for stress topologies."""
    print("\n=== Generating Stress Topology Plots ===")
    
    try:
        df = pd.read_csv("results/stress_topologies.csv")
    except FileNotFoundError as e:
        print(f"  ⚠ Stress topology data not found: {e}")
        return
    
    # Single-source only
    df1 = df[df["n_sources"] == 1]
    
    # Representative sizes per topology
    keep = {
        ("tree", 10000),
        ("tree", 100000),
        ("grid_3d", 125),
        ("grid_3d", 1000),
        ("torus", 100),
        ("complete", 10),
        ("complete", 50),
        ("leafspine", 15),
        ("fattree", 80),
    }
    
    df1 = df1[df1.apply(lambda r: (r["graph_type"], r["n_nodes"]) in keep, axis=1)]
    
    # Aggregate runtime
    agg = df1.groupby(["graph_type", "n_nodes", "algorithm"]).agg(
        runtime_mean=("runtime", "mean")
    ).reset_index()
    
    # Pivot to get Dijkstra/BMSSP together
    pivot = agg.pivot(index=["graph_type", "n_nodes"], columns="algorithm", values="runtime_mean")
    pivot = pivot.dropna()
    pivot["ratio"] = pivot["BMSSP"] / pivot["Dijkstra"]
    ratio_df = pivot.reset_index()
    
    # For clearer legend, turn n_nodes into string
    ratio_df["n_label"] = ratio_df["n_nodes"].astype(int).astype(str)
    
    topo_order = ["tree", "grid_3d", "torus", "complete", "leafspine", "fattree"]
    size_order = sorted(ratio_df["n_label"].unique(), key=lambda x: int(x))
    
    # Plot A: Runtime ratio by topology
    plt.figure(figsize=(9, 5))
    sns.barplot(
        data=ratio_df,
        x="graph_type",
        y="ratio",
        hue="n_label",
        order=topo_order,
        hue_order=size_order
    )
    plt.yscale("log")
    plt.xlabel("Topology")
    plt.ylabel("Runtime ratio BMSSP / Dijkstra")
    plt.title("Runtime ratio by topology and size (n_sources = 1)")
    plt.legend(title="n_nodes")
    plt.tight_layout()
    plt.savefig("plots/stress_ratio.png", dpi=150)
    plt.close()
    print("  ✓ stress_ratio.png")
    
    # Plot B: Runtime on trees and 3D grids
    sub = df1[df1["graph_type"].isin(["tree", "grid_3d"])]
    
    agg2 = sub.groupby(["graph_type", "n_nodes", "algorithm"]).agg(
        runtime_mean=("runtime", "mean")
    ).reset_index()
    
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    
    for ax, g in zip(axes, ["tree", "grid_3d"]):
        part = agg2[agg2["graph_type"] == g].sort_values("n_nodes")
        for algo, style in [("Dijkstra", "o-"), ("BMSSP", "s-")]:
            sd = part[part["algorithm"] == algo]
            ax.plot(sd["n_nodes"], sd["runtime_mean"], style, label=algo, linewidth=2, markersize=8)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(g)
        ax.set_xlabel("n_nodes")
        ax.grid(True, which="both", ls=":", alpha=0.3)
    
    axes[0].set_ylabel("Runtime (s)")
    axes[0].legend()
    fig.suptitle("Runtime on trees and 3D grids (n_sources = 1)")
    plt.tight_layout()
    plt.savefig("plots/stress_runtime.png", dpi=150)
    plt.close()
    print("  ✓ stress_runtime.png")
    
    # Plot C: Peak memory usage (combined plot)
    sub_mem = df1[df1["graph_type"].isin(["tree", "grid_3d"])]
    
    agg_mem = sub_mem.groupby(["graph_type", "n_nodes", "algorithm"]).agg(
        memory_mean=("memory_peak", "mean")
    ).reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for g in ["tree", "grid_3d"]:
        part = agg_mem[agg_mem["graph_type"] == g].sort_values("n_nodes")
        for algo, style, alpha in [("Dijkstra", "o-", 0.7), ("BMSSP", "s--", 0.7)]:
            sd = part[part["algorithm"] == algo]
            label = f"{g.upper()} - {algo}"
            ax.plot(
                sd["n_nodes"],
                sd["memory_mean"] / 1024,
                style,
                label=label,
                linewidth=2.5,
                markersize=8,
                alpha=alpha
            )
    
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n_nodes", fontsize=11, fontweight='bold')
    ax.set_ylabel("Peak Memory (MB)", fontsize=11, fontweight='bold')
    ax.set_title("Peak Memory Usage: Trees and 3D Grids (n_sources = 1)", fontsize=12, fontweight='bold')
    ax.grid(True, which="both", ls=":", alpha=0.3)
    ax.legend(fontsize=10, loc='best')
    
    plt.tight_layout()
    plt.savefig("plots/stress_memory.png", dpi=150)
    plt.close()
    print("  ✓ stress_memory.png")


# ========================
# MAIN
# ========================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Synthetic Benchmark Visualization")
    print("="*60)
    
    plot_grids()
    plot_random()
    plot_stress()
    
    print("\n" + "="*60)
    print("✓ All synthetic plots generated in 'plots/' directory")
    print("="*60 + "\n")
