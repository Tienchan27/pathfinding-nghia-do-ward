import xmltodict
import extract
import sys
import helper

# get the border coordinates of the area
orig_stdout = sys.stdout
f = open("./data/border.txt", "w")
graphml = open("./data/map3.graphml", "+br")
xmldoc = xmltodict.parse(graphml, xml_attribs=True)
sys.stdout = f
ways = ["1418571379","1420672675","1418571380","1413067863","1413067864",
        "1195523592","1413067860","698018289","832454966","1413266890",
        "1413266889","1413266888","1413266886","1413266887","1413266883",
        "1413266885","1413266884","1195450303","1413266891","1418571388",
        "1420672677","1418571371","1413266895","1413266898","1413266897",
        "1413266899","1413266900","11217001379"]

def getBorder(wayId):
    nodes = []
    visited = {}
    for edge in xmldoc["graphml"]["graph"]["edge"]:
        isWay = 0
        for datum in edge["data"]:
            if datum["@key"] == "d9":
                if (datum["#text"] == wayId):
                    location = helper.getLatLon(edge["@source"])
                    if (location not in visited):
                        nodes.append([location[0], location[1]])
                        visited[location] = 1
                    isWay = 1
            if datum["@key"] == "d16" and isWay:
                betweenNodes = extract.extractLineString(datum["#text"])
                for node in betweenNodes:
                    if (node not in visited):
                        nodes.append([node[0], node[1]])
                        visited[node] = 1
        if isWay:
            location = helper.getLatLon(edge["@target"])
            if (location not in visited):
                nodes.append([location[0], location[1]])
                visited[location] = 1
    if (len(nodes)):
        print(nodes)
    

for way in ways:
    getBorder(way)
            