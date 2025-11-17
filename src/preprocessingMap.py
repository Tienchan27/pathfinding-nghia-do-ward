import osmnx as ox
import networkx as nx

# create a graph from the osm file then store the graph as a graphml file 
G = ox.graph_from_xml("../data/map.osm", False, True, True)
ox.save_graphml(G, filepath="../data/map3.graphml")
