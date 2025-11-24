import re


def extractLineString(lineString):
    # return a list of coordinates in LINESTRING
    coordinates = re.findall(r"\d+\.\d+", lineString)
    pairOfCoordinates = []
    for i in range(1, len(coordinates), 2):
        pairOfCoordinates.append((float(coordinates[i]), float(coordinates[i - 1])))
    return pairOfCoordinates