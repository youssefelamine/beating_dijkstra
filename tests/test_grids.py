from graphs import *

G, node_to_id, id_to_node = generate_grid_2d(3, 3, seed=42)

print("Nodes:", len(G.nodes()))
print("Edges:", len(G.edges()))

bm = tree_to_bmsspy_format(G, node_to_id)
print("BMSSP sample:", bm[:3])