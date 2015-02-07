import networkx as nx
G = nx.Graph()
G.add_node(1)
G.add_nodes_from([2,3])
# G.add_edge(1,2)
# G.add_edge((2,3))
G.add_edges_from([(1,2),(1,3)])
# G.remove_node
# G.remove_edge
# G.clear()
G.number_of_nodes()
G.number_of_nodes()
#H=nx.DiGraph(G)
H=nx.Graph(G)

# G = nx.Graph(day="Friday")

import matplotlib.pyplot as pl
nx.draw(G)
pl.show()
