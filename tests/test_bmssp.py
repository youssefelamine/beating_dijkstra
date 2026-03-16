import time
import networkx as nx
from bmsspy import Bmssp

# 1) Create a NetworkX graph
G = nx.DiGraph()
edges = [
    ("A", "B", 1),
    ("A", "C", 4),
    ("B", "C", 2),
    ("B", "D", 5),
    ("C", "D", 1),
]
G.add_weighted_edges_from(edges)

# Map nodes to integer IDs
node_to_id = {node: i for i, node in enumerate(G.nodes())}
id_to_node = {i: node for node, i in node_to_id.items()}

# Build list of adjacency dicts
graph_list = []
for node in G.nodes():
    nid = node_to_id[node]
    neigh_dict = {}
    for nbr in G.successors(node):
        neigh_dict[node_to_id[nbr]] = G[node][nbr]["weight"]
    graph_list.append(neigh_dict)

# 2) Run Dijkstra with NetworkX
source = "A"
src_id = node_to_id[source]

start = time.time()
dijkstra_distances = nx.single_source_dijkstra_path_length(G, source)
dijkstra_time = time.time() - start

print("Dijkstra distances:", dijkstra_distances)
print(f"Dijkstra time: {dijkstra_time:.6f} seconds\n")

# 3) BMSSPy solver
bmssp_graph = Bmssp(graph_list)

start = time.time()
result = bmssp_graph.solve(origin_id=src_id)
bmssp_time = time.time() - start

# Convert back to node names
bmssp_distances = {
    id_to_node[i]: dist
    for i, dist in enumerate(result["distance_matrix"])
}

print("BMSSP distances:", bmssp_distances)
print(f"BMSSP time: {bmssp_time:.6f} seconds\n")

# 4) Compare results
print("Comparison:")
for node in G.nodes():
    d = dijkstra_distances.get(node)
    b = bmssp_distances.get(node)
    print(f"{node}: Dijkstra = {d}, BMSSP = {b}")