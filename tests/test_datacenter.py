from graphs import *

G, node_to_id, id_to_node = generate_leaf_spine(4,2,seed=42)
print("LeafSpine:", len(G.nodes()), len(G.edges()))

G2, _, _ = generate_fat_tree(k=4,seed=42)
print("FatTree:", len(G2.nodes()), len(G2.edges()))