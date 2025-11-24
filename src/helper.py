
import xmltodict
import haversine
import extract
import os

graphml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/map3.graphml"))
graphml = open(graphml_path, "+br")
xmldoc = xmltodict.parse(graphml, xml_attribs=True)

road = {
    "motorway":0, "trunk":0, "primary":0,"primary_link":0, "secondary":0, "tertiary":0, "secondary_link":0, "tertiary_link":0,
    "residential":0, "unclassified":0, "service":0, "living_street":0, "footway":0, "path":0
}

# --------- TIỀN XỬ LÝ: BUILD INDEX CHO NODE & EDGE ---------

_nodes = xmldoc["graphml"]["graph"]["node"]
_edges = xmldoc["graphml"]["graph"]["edge"]

# id -> (lat, lon)
_node_coords = {}

# id -> list[(neighbor_id, length)]
_adj = {}

# Build node_coords
for node in _nodes:
    node_id = node["@id"]
    lat = None
    lon = None
    for datum in node["data"]:
        if datum["@key"] == "d4":
            lat = float(datum["#text"])
        elif datum["@key"] == "d5":
            lon = float(datum["#text"])
    if lat is not None and lon is not None:
        _node_coords[node_id] = (lat, lon)

# Build adjacency list
for edge in _edges:
    src = edge["@source"]
    tgt = edge["@target"]

    length = None
    highway_type = None

    for datum in edge["data"]:
        if datum["@key"] == "d13":
            length = float(datum["#text"])
        elif datum["@key"] == "d14":
            highway_type = datum["#text"]

    # chỉ thêm nếu là loại đường hợp lệ và có length
    if highway_type in road and length is not None:
        if src not in _adj:
            _adj[src] = []
        _adj[src].append((tgt, length))

# --------- HÀM PUBLIC GIỮ NGUYÊN TÊN ---------

def getLatLon(OSMId):
    return _node_coords[OSMId]

def getOSMId(lat, lon):

    for node_id, (la, lo) in _node_coords.items():
        if la == lat and lo == lon:
            return node_id
    return ""

def getAdjacentNodes(OSMId):
    return _adj.get(OSMId, [])

def getHeuristic(point1, point2):
    return haversine.haversine(point1, point2)

def getLineString(start, end):
    ans = []
    for edge in _edges:
        if (edge["@source"] == start and edge["@target"] == end):
            for datum in edge["data"]:
                if datum["@key"] == "d15":
                    ans = extract.extractLineString(datum["#text"])
                    return ans
    return ans

def getResponseLeafLet(pathDict, endID):
    response = []
    point = endID
    visited = {}
    while (pathDict[point] != None):
        betweenNodes = getLineString(pathDict[point], point)
        betweenNodes.reverse()
        pointLocation = getLatLon(point)
        if (pointLocation not in visited):
            response.append([pointLocation[0], pointLocation[1]])
            visited[pointLocation] = 1
        for i in betweenNodes:
            if (i not in visited):
                visited[i] = 1
                response.append([i[0], i[1]])
        point = pathDict[point]
    pointLocation = getLatLon(point)
    if (pointLocation not in visited):
        response.append([pointLocation[0], pointLocation[1]])
    return response

