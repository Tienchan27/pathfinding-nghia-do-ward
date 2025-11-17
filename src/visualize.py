import osmnx as ox

G = ox.graph_from_xml("../data/map.osm", False, True, True)
ox.plot_graph(G)