import xmltodict
import haversine
import extract
import os
graphml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/map3.graphml"))
graphml = open(graphml_path, "+br")
xmldoc = xmltodict.parse(graphml, xml_attribs=True)

# node: list of {'@id': '11337806829', 'data': [{'@key': 'd3', '#text': '21.0287243'}, {'@key': 'd4', '#text': '105.8598932'}]}
# edge: list of {'@source': '11337806829', '@target': '11337806828', '@id': '0', 'data': [{'@key': 'd7', '#text': '1222445909'}, {'@key': 'd15', '#text': 'service'}, {'@key': 'd8', '#text': 'False'}, {'@key': 'd9', '#text': 'True'}, {'@key': 'd10', '#text': '66.57'}]}]

road = {
    "motorway":0, "trunk":0, "primary":0,"primary_link":0, "secondary":0, "tertiary":0, "secondary_link":0, "tertiary_link":0,
    "residential":0, "unclassified":0, "service":0, "living_street":0, "footway":0, "path":0
}

def getLatLon(OSMId):
    # return the coordinate of the node with the given OSMId
    nodes = xmldoc["graphml"]["graph"]["node"]
    size = len(nodes)
    lat = ""
    lon = ""
    for i in range(size):
        node = nodes[i]
        if (node["@id"] == OSMId):
            data = node["data"]
            for datum in data:
                if datum["@key"] == "d4":
                    lat = datum["#text"] #string
                if datum["@key"] == "d5":
                    lon = datum["#text"] #string
                    break
            break
    return (float(lat), float(lon))


def getOSMId(lat, lon):
    # return the OSMId of the node with the given latitude and longitude
    nodes = xmldoc["graphml"]["graph"]["node"]
    id = ""
    for node in nodes:
        for datum in node["data"]:
            if (datum["@key"] == "d4"):
                nodeLat = datum["#text"]
            if (datum["@key"] == "d5"):
                nodeLon = datum["#text"]
                break
        if (lat == float(nodeLat) and lon == float(nodeLon)):
            id = node["@id"]
            break
    return id


def getAdjacentNodes(OSMId):
    # return a list of nodes that are neighboring the node identified by the specified OSMId
    edges = xmldoc["graphml"]["graph"]["edge"]
    adjacentNodes = []
    length = 0
    isRoad = 0
    for edge in edges:
        if (edge["@source"] == OSMId):
            for datum in edge["data"]:
                if (datum["@key"] == "d11"):
                    length = float(datum["#text"]) #string
                    break
                elif (datum["@key"] == "d9"):
                    if (datum["#text"] in road):
                        isRoad = 1
            if (isRoad):
                adjacentNodes.append((edge["@target"], length))
                isRoad = 0
    return adjacentNodes


def getHeuristic(point1, point2):
    # point1: a tuple of two float numbers respresenting the coordinate of the first point
    # point2: a tuple of two float number representing the coordinate of the second point
    # return the great-circle distance between the two points on the Earth surface
    return haversine.haversine(point1, point2)


def getLineString(start, end):
    # start: the OSMId of the source node
    # end: the OSMId of the target node
    # return a list of coordinates in the LINESTRING, if it is present
    ans = []
    for edge in xmldoc["graphml"]["graph"]["edge"]:
        if (edge["@source"] == start and edge["@target"] == end):
            for datum in edge["data"]:
                if datum["@key"] == "d13":
                    ans = extract.extractLineString(datum["#text"])
                    return ans
    return ans
def getResponseLeafLet(pathDict, endID):
    # pathDict: a dictionary which will be used to trace the shortest path
    # endID: the OSMId of the destination node
    # return a list of coordinates that defines the shortest path
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

