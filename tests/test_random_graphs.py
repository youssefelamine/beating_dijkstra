from graphs import *

G, node_to_id, id_to_node = generate_er_graph(10, p=0.3, seed=42)

print("Nodes:", list(G.nodes())[:5])
print("Edges:", list(G.edges(data=True))[:5])

bm = tree_to_bmsspy_format(G, node_to_id)
print("BMSSP sample:", bm[:3])