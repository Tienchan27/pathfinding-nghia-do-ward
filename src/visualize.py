import osmnx as ox

G = ox.graph_from_xml("./data/map.osm")
ox.plot_graph(G)