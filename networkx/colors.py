import networkx as nx
import matplotlib.pyplot as plt
G = nx.star_graph(20)  
pos = nx.spring_layout(G)
colors = range(20) 
nodes = nx.draw_networkx_nodes(G,pos,node_color='k', with_labels=False)
edges = nx.draw_networkx_edges(G,pos,edge_color=colors,width=4,
                               edge_cmap=plt.cm.Blues)
plt.colorbar(edges)
plt.axis('off')
plt.show(block=False)
