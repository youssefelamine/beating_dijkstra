# test_graphs.py
from graphs import generate_tree, tree_to_bmsspy_format

G, node_to_id, id_to_node = generate_tree(10, weight_range=(1,5), seed=42)
bmssp_graph = tree_to_bmsspy_format(G, node_to_id)

print("Nodes:", G.nodes())
print("Edges with weights:", [(u,v,G[u][v]['weight']) for u,v in G.edges()])
print("BMSSPy format:", bmssp_graph)