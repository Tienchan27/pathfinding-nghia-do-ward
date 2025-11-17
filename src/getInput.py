import haversine
import os
dataset_path = os.path.join(os.path.dirname(__file__), "../data/out4.txt")
dataset = open(dataset_path, "+br")
nodes = []
count = 0
for x in dataset:
    [lat, lon] = x.split()
    nodes.append((float(lat), float(lon)))
def getNearestPoint(lat, lon):
    # lat: a float number representing the latitude which was chosen by the user
    # lon: a float number representing the longitude which was chosen by the user
    # return the coordinates of the closest point to the user's selected location.
    location = ()
    curr = 999999999
    for node in nodes:
        point = (float(lat), float(lon))
        distance = haversine.haversine(node, point)
        if (distance == 0):
            return point
        if (distance < curr):
            location = node
            curr = distance
    return (location[0],location[1])
def getAllPoints():
    ans = []
    for x in nodes:
        lat, lon = x
        ans.append([lat, lon])
    return ans
        
    
    