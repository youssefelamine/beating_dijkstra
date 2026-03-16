# dataset_loader.py
"""
Dataset loading module for real-world graphs.
Loads weighted edge lists from datasets directory.
Supports: .txt (simple edge list), .gr (DIMACS format), .csv
"""

import networkx as nx
from pathlib import Path
from typing import Tuple, Dict


def load_dataset(
    dataset_name: str,
    dataset_path: str = "datasets"
) -> Tuple[nx.Graph, Dict[int, int], Dict[int, int]]:
    """
    Load a dataset from edge list file and convert to BMSSP format.
    Supports multiple formats: txt, gr (DIMACS), csv
    
    Args:
        dataset_name: Name of the dataset (folder name in datasets/)
        dataset_path: Root path to datasets directory (default: "datasets")
    
    Returns:
        Tuple of (G, node_to_id, id_to_node) where:
            - G: NetworkX undirected weighted graph
            - node_to_id: dict mapping original node labels to integer IDs
            - id_to_node: dict mapping integer IDs back to original labels
    
    Raises:
        FileNotFoundError: If dataset directory or edge list file not found
        ValueError: If edge list file is malformed
        RuntimeError: If resulting graph is empty
    """
    
    # Construct dataset path
    dataset_dir = Path(dataset_path) / dataset_name
    
    # Check if dataset directory exists
    if not dataset_dir.exists():
        raise FileNotFoundError(
            f"Dataset directory not found: {dataset_dir.absolute()}\n"
            f"Expected format: {dataset_path}/{dataset_name}/"
        )
    
    # Look for edge list file (common naming conventions, prioritize by format)
    edge_list_candidates = [
        # DIMACS format (.gr)
        dataset_dir / f"{dataset_name}.gr",
        dataset_dir / "edges.gr",
        dataset_dir / "graph.gr",
        # Simple text format (.txt)
        dataset_dir / "edges.txt",
        dataset_dir / f"{dataset_name}.txt",
        dataset_dir / "edgelist.txt",
        # CSV format
        dataset_dir / "edges.csv",
        dataset_dir / f"{dataset_name}.csv",
        # Fallback
        dataset_dir / f"{dataset_name}.edgelist",
    ]
    
    edge_list_file = None
    for candidate in edge_list_candidates:
        if candidate.exists():
            edge_list_file = candidate
            break
    
    if edge_list_file is None:
        raise FileNotFoundError(
            f"No edge list file found in {dataset_dir.absolute()}\n"
            f"Searched for: .gr (DIMACS), .txt (edge list), .csv formats"
        )
    
    print(f"Loading dataset from: {edge_list_file}")
    
    # Detect format and load accordingly
    if edge_list_file.suffix == ".gr":
        G = _load_dimacs_format(edge_list_file)
    else:
        G = _load_simple_edgelist(edge_list_file)
    
    # Check if graph is non-empty
    if G.number_of_nodes() == 0:
        raise RuntimeError(f"Dataset {dataset_name} resulted in empty graph (0 nodes)")
    
    print(f"Loaded {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Convert node labels to integer IDs (deterministic ordering)
    # Try to convert node labels to int if they're numeric strings
    node_labels = sorted(G.nodes(), key=lambda x: int(x) if isinstance(x, str) and x.isdigit() else str(x))
    original_to_id = {node: i for i, node in enumerate(node_labels)}
    id_to_original = {i: node for node, i in original_to_id.items()}
    
    # Create new graph with integer node IDs
    G_mapped = nx.Graph()
    for u, v, data in G.edges(data=True):
        u_id = original_to_id[u]
        v_id = original_to_id[v]
        G_mapped.add_edge(u_id, v_id, weight=data.get('weight', 1.0))
    
    # Create mappings for integer node IDs in G_mapped
    # node_to_id: maps integer node ID -> integer node ID (identity, for compatibility with benchmark functions)
    # id_to_node: maps integer node ID -> original node label (for reverse mapping)
    node_to_id = {i: i for i in range(G_mapped.number_of_nodes())}
    id_to_node = id_to_original
    
    return G_mapped, node_to_id, id_to_node


def _load_dimacs_format(filepath: Path) -> nx.Graph:
    """
    Load graph from DIMACS format (.gr file).
    Format:
        c comment line
        p sp <nodes> <edges>
        a from to weight
        a from to weight
        ...
    """
    G = nx.Graph()
    edge_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('c') or line.startswith('%'):
                    continue
                
                # Skip problem line
                if line.startswith('p'):
                    continue
                
                # Parse edge line
                if line.startswith('a'):
                    try:
                        parts = line.split()
                        if len(parts) < 3:
                            raise ValueError(f"Line {line_num}: Expected 'a u v [weight]', got {len(parts)} parts")
                        
                        u = parts[1]
                        v = parts[2]
                        weight = float(parts[3]) if len(parts) > 3 else 1.0
                        
                        G.add_edge(u, v, weight=weight)
                        edge_count += 1
                        
                    except (ValueError, IndexError) as e:
                        raise ValueError(f"Malformed edge at line {line_num}: {line}\nError: {str(e)}")
    
    except UnicodeDecodeError as e:
        raise ValueError(f"File encoding error in {filepath}: {str(e)}")
    except IOError as e:
        raise FileNotFoundError(f"Cannot read file {filepath}: {str(e)}")
    
    if edge_count == 0:
        raise RuntimeError(f"No edges found in DIMACS file {filepath}")
    
    return G


def _load_simple_edgelist(filepath: Path) -> nx.Graph:
    """
    Load graph from simple edge list format (.txt or .csv).
    Format:
        u v [weight]
        u v [weight]
        ...
    Ignores lines starting with # or %
    """
    G = nx.Graph()
    edge_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Strip whitespace
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith('%'):
                    continue
                
                # Parse edge
                try:
                    parts = line.split()
                    if len(parts) < 2:
                        raise ValueError(f"Line {line_num}: Expected at least 2 columns (u v [weight]), got {len(parts)}")
                    
                    u = parts[0]
                    v = parts[1]
                    weight = float(parts[2]) if len(parts) > 2 else 1.0
                    
                    # Add weighted edge (undirected)
                    G.add_edge(u, v, weight=weight)
                    edge_count += 1
                    
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Malformed edge at line {line_num}: {line}\nError: {str(e)}")
    
    except UnicodeDecodeError as e:
        raise ValueError(f"File encoding error in {filepath}: {str(e)}")
    except IOError as e:
        raise FileNotFoundError(f"Cannot read file {filepath}: {str(e)}")
    
    if edge_count == 0:
        raise RuntimeError(f"No edges found in edge list file {filepath}")
    
    return G


def validate_dataset(dataset_name: str, dataset_path: str = "datasets") -> bool:
    """
    Check if a dataset exists and is valid.
    
    Args:
        dataset_name: Name of the dataset
        dataset_path: Root path to datasets directory
    
    Returns:
        True if dataset exists and is readable, False otherwise
    """
    try:
        dataset_dir = Path(dataset_path) / dataset_name
        return dataset_dir.exists() and dataset_dir.is_dir()
    except Exception:
        return False


def list_available_datasets(dataset_path: str = "datasets") -> list:
    """
    List all available datasets.
    
    Args:
        dataset_path: Root path to datasets directory
    
    Returns:
        List of dataset names
    """
    datasets_dir = Path(dataset_path)
    if not datasets_dir.exists():
        return []
    
    datasets = []
    for item in datasets_dir.iterdir():
        if item.is_dir():
            # Check if it has any edge list files
            for ext in ['.gr', '.txt', '.csv', '.edgelist']:
                if list(item.glob(f'*{ext}')):
                    datasets.append(item.name)
                    break
    
    return sorted(datasets)
