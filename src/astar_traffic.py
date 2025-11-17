
import helper as help
import heapq as hq
import time
import numpy as np
import os


def astar_traffic(start, end):
    # start: OSMId of the first point
    # end: OSMId of the second point
    # return a tuple of a dictionary to trace the final path and the shortest distance
    previous = {} 
    finalDistance = 0
    # a* grade = aGrade
    startLocation = help.getLatLon(start)
    endLocation = help.getLatLon(end)
    previous[start] = None
    startToEnd = help.getHeuristic(startLocation, endLocation)
    opened = [(startToEnd, 0, start)]
    closed = {start: startToEnd}
    hq.heapify(opened)
    s = time.time()
    while (len(opened) > 0):
        currNodeAGrade, distanceToCurrNode, currNodeId = opened[0]
        hq.heappop(opened)
        closed[currNodeId] = currNodeAGrade
        if (currNodeId == end):
            finalDistance = distanceToCurrNode
            break
        adjacentNodes = help.getAdjacentNodes(currNodeId) # node = (nodeId, length)  
        for node in adjacentNodes:
            neighborNodeOSMId, currNodeToNodeLength = node
            neighborNodeLocation = help.getLatLon(neighborNodeOSMId)
            heuristic = help.getHeuristic(neighborNodeLocation, endLocation)
            distanceToNeighborNode = distanceToCurrNode + currNodeToNodeLength
            aGrade = distanceToNeighborNode + heuristic
            value = (aGrade, distanceToNeighborNode, neighborNodeOSMId)
            if (neighborNodeOSMId not in closed):
                opened.append(value)
                closed[neighborNodeOSMId] = aGrade
                previous[neighborNodeOSMId] = currNodeId
        hq.heapify(opened)
    print("Time taken to find path(in second): "+str(time.time()-s))
    path = reconstruct_path(previous, start, end)
    print(path)
    return (previous, finalDistance)

def reconstruct_path(previous, start, end):
    path = []
    current = end
    while current != start:
        prev = previous.get(current)
        if prev is None:
            return []  # Không tìm được đường đi
        path.append((prev, current))  # Đoạn đường từ prev -> current
        current = prev
    path.reverse()

    # Ensure the file exists
    file_path = 'data/blocked_edges.txt'
    if not os.path.exists('data'):
        os.makedirs('data')
    
    try:
        # Read existing content
        existing_edges = set()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    existing_edges.add(line.strip())

        # Write new edges, avoiding duplicates
        with open(file_path, 'w', encoding='utf-8') as f:
            for u, v in path:
                edge_line = f"{u} {v} traffic"
                if edge_line not in existing_edges:
                    f.write(edge_line + '\n')
                    existing_edges.add(edge_line)
            # Write back any existing flood edges
            for edge in existing_edges:
                if edge.endswith('flood'):
                    f.write(edge + '\n')

    except Exception as e:
        print(f"Error handling blocked_edges.txt: {str(e)}")
        # Continue execution even if file operations fail
    
    return path