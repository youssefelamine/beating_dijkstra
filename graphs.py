# graphs.py
import networkx as nx
import random

def generate_tree(n_nodes, weight_range=(1, 10), seed=None, root=0, directed=True):
    """
    Generate a random tree.

    Args:
        n_nodes (int): number of nodes
        weight_range (tuple): min/max edge weights
        seed (int): random seed
        root (int): root node for BFS tree (used if directed=True)
        directed (bool): whether to return a directed BFS tree or undirected tree

    Returns:
        G (networkx.DiGraph or DiGraph): generated tree
        node_to_id (dict): node label -> integer ID mapping
        id_to_node (dict): inverse mapping
    """
    if seed is not None:
        random.seed(seed)

    # Generate an undirected random tree
    T = nx.random_labeled_tree(n_nodes, seed=seed)

    if directed:
        # Convert to directed BFS tree from the root
        G = nx.DiGraph(nx.bfs_tree(T, source=root))
    else:
        # Keep as undirected tree
        G = nx.DiGraph()
        G.add_edges_from(T.edges())

    # Assign random weights to edges
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(*weight_range)
        if not directed:
            # Add reverse edge for undirected mode
            G.add_edge(v, u, weight=G[u][v]['weight'])

    # Node ID mapping for BMSSPy
    node_to_id = {node: i for i, node in enumerate(G.nodes())}
    id_to_node = {i: node for node, i in node_to_id.items()}

    return G, node_to_id, id_to_node


def to_bmsspy_format(G, node_to_id):
    """
    Convert NetworkX graph to BMSSPy format.
    Works for all graph types: trees, random, grids, datacenter.
    Returns: list of dicts, index = BMSSPy node ID
    """
    n = len(G)
    graph_list = [{} for _ in range(n)]

    for node in G.nodes():
        nid = node_to_id[node]
        neighbors = G.successors(node) if G.is_directed() else G.neighbors(node)
        graph_list[nid] = {node_to_id[neigh]: G[node][neigh]["weight"] for neigh in neighbors}

    return graph_list

# =========================
# RANDOM GRAPH GENERATORS
# =========================

def _assign_random_weights(G, weight_range=(1, 10), seed=None):
    if seed is not None:
        random.seed(seed)

    for u, v in G.edges():
        G[u][v]["weight"] = random.randint(*weight_range)


def _make_directed_if_needed(G, directed):
    if directed:
        DG = nx.DiGraph()
        DG.add_nodes_from(G.nodes())
        for u, v, data in G.edges(data=True):
            DG.add_edge(u, v, **data)
        return DG
    return G


def _finalize_graph(G):
    node_to_id = {node: i for i, node in enumerate(G.nodes())}
    id_to_node = {i: node for node, i in node_to_id.items()}
    return G, node_to_id, id_to_node


# ---------------------------------
# Erdős–Rényi Graph
# ---------------------------------
def generate_er_graph(n_nodes, p=0.1, weight_range=(1,10), directed=True, seed=None):
    G = nx.erdos_renyi_graph(n_nodes, p, seed=seed)
    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)


# ---------------------------------
# Barabási–Albert (scale-free)
# ---------------------------------
def generate_ba_graph(n_nodes, m=2, weight_range=(1,10), directed=True, seed=None):
    G = nx.barabasi_albert_graph(n_nodes, m, seed=seed)
    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)


# ---------------------------------
# Watts–Strogatz (small-world)
# ---------------------------------
def generate_ws_graph(n_nodes, k=4, p=0.2, weight_range=(1,10), directed=True, seed=None):
    G = nx.watts_strogatz_graph(n_nodes, k, p, seed=seed)
    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)

# Backward compatibility aliases
random_to_bmsspy_format = to_bmsspy_format
grid_to_bmsspy_format = to_bmsspy_format
dc_to_bmsspy_format = to_bmsspy_format
tree_to_bmsspy_format = to_bmsspy_format

# =========================
# GRID / MESH GENERATORS
# =========================

def generate_grid_2d(rows, cols, weight_range=(1,10), directed=True, seed=None):
    G = nx.grid_2d_graph(rows, cols)
    G = nx.convert_node_labels_to_integers(G)

    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)


def generate_grid_3d(x, y, z, weight_range=(1,10), directed=True, seed=None):
    G = nx.grid_graph(dim=[x, y, z])
    G = nx.convert_node_labels_to_integers(G)

    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)


def generate_torus(rows, cols, weight_range=(1,10), directed=True, seed=None):
    G = nx.grid_2d_graph(rows, cols, periodic=True)
    G = nx.convert_node_labels_to_integers(G)

    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)


def generate_complete_graph(n_nodes, weight_range=(1,10), directed=True, seed=None):
    G = nx.complete_graph(n_nodes)

    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)

# =========================
# DATACENTER TOPOLOGIES
# =========================

def generate_leaf_spine(n_leaf, n_spine, weight_range=(1,10), directed=True, seed=None):
    G = nx.Graph()

    leaf_nodes = range(n_leaf)
    spine_nodes = range(n_leaf, n_leaf + n_spine)

    # connect every leaf to every spine
    for l in leaf_nodes:
        for s in spine_nodes:
            G.add_edge(l, s)

    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)


def generate_fat_tree(k=4, weight_range=(1,10), directed=True, seed=None):
    """
    k must be even
    total nodes = k^3/4 + k^2
    """
    if k % 2 != 0:
        raise ValueError("k must be even for fat-tree")

    G = nx.Graph()
    pods = k
    core_switches = (k//2)**2

    node_id = 0

    # core layer
    core = []
    for _ in range(core_switches):
        core.append(node_id)
        node_id += 1

    # pods
    for _ in range(pods):
        agg = []
        edge = []

        for _ in range(k//2):
            agg.append(node_id)
            node_id += 1

        for _ in range(k//2):
            edge.append(node_id)
            node_id += 1

        # agg <-> edge
        for a in agg:
            for e in edge:
                G.add_edge(a, e)

        # core <-> agg
        for a in agg:
            for c in core:
                G.add_edge(a, c)

    _assign_random_weights(G, weight_range, seed)
    G = _make_directed_if_needed(G, directed)
    return _finalize_graph(G)