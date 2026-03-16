# plots.py (pure matplotlib version)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# --------------------------
# Settings
# --------------------------
INPUT_CSV = "results/USAroad-NY.csv"
OUTPUT_DIR = "plots"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['font.size'] = 10

# --------------------------
# Load CSV
# --------------------------
df = pd.read_csv(INPUT_CSV)

# Convert memory from KB to MB
df['memory_peak_mb'] = df['memory_peak'] / 1024

# Average over run_id if multiple runs exist
avg_df = df.groupby(["graph_type","n_nodes","n_sources","algorithm","extra_params"]).agg({
    "runtime":"mean",
    "memory_peak_mb":"mean"
}).reset_index()

# --------------------------
# Plotting functions
# --------------------------
def plot_runtime_vs_sources(graph_type):
    """Plot runtime vs number of sources"""
    data = avg_df[avg_df["graph_type"] == graph_type]
    plt.figure(figsize=(10, 6))
    
    for algo in sorted(data["algorithm"].unique()):
        algo_data = data[data["algorithm"] == algo]
        algo_data = algo_data.sort_values("n_sources")
        plt.plot(algo_data["n_sources"], algo_data["runtime"], 
                marker='o', linewidth=2.5, markersize=8, label=algo)
    
    plt.title(f"Runtime vs Number of Sources - {graph_type}", fontsize=12, fontweight='bold')
    plt.xlabel("Number of Sources", fontsize=11)
    plt.ylabel("Runtime (s)", fontsize=11)
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{graph_type}_runtime_vs_sources.png", dpi=150)
    plt.close()

def plot_memory_vs_sources(graph_type):
    """Plot memory vs number of sources"""
    data = avg_df[avg_df["graph_type"] == graph_type]
    plt.figure(figsize=(10, 6))
    
    for algo in sorted(data["algorithm"].unique()):
        algo_data = data[data["algorithm"] == algo]
        algo_data = algo_data.sort_values("n_sources")
        plt.plot(algo_data["n_sources"], algo_data["memory_peak_mb"], 
                marker='s', linewidth=2.5, markersize=8, label=algo)
    
    plt.title(f"Memory Usage vs Number of Sources - {graph_type}", fontsize=12, fontweight='bold')
    plt.xlabel("Number of Sources", fontsize=11)
    plt.ylabel("Peak Memory (MB)", fontsize=11)
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{graph_type}_memory_vs_sources.png", dpi=150)
    plt.close()

def plot_runtime_comparison(graph_type):
    """Bar chart comparing runtime across algorithms and sources"""
    data = avg_df[avg_df["graph_type"] == graph_type]
    data = data.sort_values(["n_sources", "algorithm"])
    
    plt.figure(figsize=(12, 6))
    
    n_sources_vals = sorted(data["n_sources"].unique())
    x = np.arange(len(n_sources_vals))
    width = 0.35
    
    for i, algo in enumerate(sorted(data["algorithm"].unique())):
        algo_data = data[data["algorithm"] == algo].sort_values("n_sources")
        offset = (i - 0.5) * width
        plt.bar(x + offset, algo_data["runtime"], width, label=algo, alpha=0.8)
    
    plt.title(f"Runtime Comparison - {graph_type}", fontsize=12, fontweight='bold')
    plt.xlabel("Number of Sources", fontsize=11)
    plt.ylabel("Runtime (s)", fontsize=11)
    plt.xticks(x, n_sources_vals)
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{graph_type}_runtime_bars.png", dpi=150)
    plt.close()

def plot_memory_comparison(graph_type):
    """Bar chart comparing memory across algorithms and sources"""
    data = avg_df[avg_df["graph_type"] == graph_type]
    data = data.sort_values(["n_sources", "algorithm"])
    
    plt.figure(figsize=(12, 6))
    
    n_sources_vals = sorted(data["n_sources"].unique())
    x = np.arange(len(n_sources_vals))
    width = 0.35
    
    for i, algo in enumerate(sorted(data["algorithm"].unique())):
        algo_data = data[data["algorithm"] == algo].sort_values("n_sources")
        offset = (i - 0.5) * width
        plt.bar(x + offset, algo_data["memory_peak_mb"], width, label=algo, alpha=0.8)
    
    plt.title(f"Memory Usage Comparison - {graph_type}", fontsize=12, fontweight='bold')
    plt.xlabel("Number of Sources", fontsize=11)
    plt.ylabel("Peak Memory (MB)", fontsize=11)
    plt.xticks(x, n_sources_vals)
    plt.legend(fontsize=10, loc='best')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/{graph_type}_memory_bars.png", dpi=150)
    plt.close()

# --------------------------
# Generate plots for all graph types
# --------------------------
for gtype in df["graph_type"].unique():
    print(f"Generating plots for {gtype}...")
    plot_runtime_vs_sources(gtype)
    plot_memory_vs_sources(gtype)
    plot_runtime_comparison(gtype)
    plot_memory_comparison(gtype)

print(f"\n✓ All plots generated in '{OUTPUT_DIR}/' folder")