import helper as help
import heapq as hq
import time
import numpy as np

# --- Load blocked edges & penalty một lần ở mức module ---

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))   # folder gốc project
BLOCKED_FILE = os.path.join(BASE_DIR, "data", "blocked_edges.txt")

blocked_edges = set()
edge_penalty = {}

#with open('C:\\Users\\Nhi Nhi\\Documents\\Code\\intro AI\\pathfinding-nghia-do-ward\\data\\blocked_edges.txt', 'r') as f:
with open(BLOCKED_FILE, "r") as f:
    for line in f:
        u, v, reason = line.strip().split()
        blocked_edges.add((u, v))
        blocked_edges.add((v, u))  # vì đồ thị có thể vô hướng

        if reason == "traffic":
            edge_penalty[(u, v)] = 5
            edge_penalty[(v, u)] = 5
        elif reason == "flood":
            edge_penalty[(u, v)] = float('inf')
            edge_penalty[(v, u)] = float('inf')

# --- Cache LatLon để tránh gọi helper nhiều lần ---

latlon_cache = {}

def get_latlon_cached(node):
    if node not in latlon_cache:
        latlon_cache[node] = help.getLatLon(node)
    return latlon_cache[node]

# --- Improved A* ---

def astar(start, end):
    """
    A* chuẩn: có g_score, f_score, cho phép relax lại node nếu tìm được đường tốt hơn.
    Trả về:
        - previous: dict để reconstruct đường đi
        - final_distance: tổng độ dài đường (đã nhân penalty)
    """

    start_location = get_latlon_cached(start)
    end_location = get_latlon_cached(end)

    open_heap = []                     # (f, node)
    g_score = {start: 0.0}             # chi phí từ start đến node
    f_start = help.getHeuristic(start_location, end_location)
    f_score = {start: f_start}
    previous = {start: None}

    hq.heappush(open_heap, (f_start, start))

    closed = set()
    t0 = time.time()

    while open_heap:
        curr_f, curr_node = hq.heappop(open_heap)

        # Nếu node này đã xử lý với f tốt hơn rồi thì bỏ qua (entry cũ trong heap)
        if curr_node in closed:
            continue

        if curr_node == end:
            final_distance = g_score[curr_node]
            path = reconstruct_path(previous, start, end)
            t1 = time.time()
            print("A* time:", t1 - t0, "seconds")
            print("A* distance:", final_distance)
            print(path)
            return previous, final_distance

        closed.add(curr_node)

        for neighbor_id, edge_length in help.getAdjacentNodes(curr_node):
            # Bỏ qua cạnh bị chặn do lũ
            if (curr_node, neighbor_id) in edge_penalty and edge_penalty[(curr_node, neighbor_id)] == float('inf'):
                continue

            penalty = edge_penalty.get((curr_node, neighbor_id), 1)
            adjusted_length = edge_length * penalty

            tentative_g = g_score[curr_node] + adjusted_length

            # Nếu đã có g_score tốt hơn rồi thì bỏ
            if tentative_g >= g_score.get(neighbor_id, float('inf')):
                continue

            # Tìm được đường tốt hơn đến neighbor
            g_score[neighbor_id] = tentative_g
            neighbor_location = get_latlon_cached(neighbor_id)
            f = tentative_g + help.getHeuristic(neighbor_location, end_location)
            f_score[neighbor_id] = f
            previous[neighbor_id] = curr_node

            hq.heappush(open_heap, (f, neighbor_id))

    # Không tìm được đường
    t1 = time.time()
    print("A* time:", t1 - t0, "seconds")
    print("Cannot find a path", start, "to", end)
    return previous, float('inf')

def reconstruct_path(previous, start, end):
    path = []
    current = end
    while current != start:
        prev = previous.get(current)
        if prev is None:
            return []  # không tìm được đường
        path.append((prev, current))
        current = prev
    path.reverse()
    return path

# code cũ, cái này bị lỗi ở tập closed nên chưa cho đường tối ưu (đường dài hơn Dijkstra, sai với lý thuyết)

"""
def astar(start, end):
    # start: OSMId of the first point
    # end: OSMId of the second point
    # return a tuple of a dictionary to trace the final path and the shortest distance
    blocked_edges = set()
    edge_penalty = {}

    with open('data/blocked_edges.txt', 'r') as f:
        for line in f:
            u, v, reason = line.strip().split()
            blocked_edges.add((u, v))
            blocked_edges.add((v, u))  # vì đồ thị có thể vô hướng

            if reason == "traffic":
                edge_penalty[(u, v)] = 5  # hệ số phạt cho tắc đường
                edge_penalty[(v, u)] = 5
            elif reason == "flood":
                edge_penalty[(u, v)] = float('inf')  # lũ -> không đi được
                edge_penalty[(v, u)] = float('inf')
                
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

            # Bỏ qua cạnh bị chặn do lũ
            if (currNodeId, neighborNodeOSMId) in edge_penalty and edge_penalty[(currNodeId, neighborNodeOSMId)] == float('inf'):
                continue

            # Áp dụng hệ số phạt nếu tắc đường
            penalty = edge_penalty.get((currNodeId, neighborNodeOSMId), 1)
            adjustedLength = currNodeToNodeLength * penalty

            neighborNodeLocation = help.getLatLon(neighborNodeOSMId)
            heuristic = help.getHeuristic(neighborNodeLocation, endLocation)
            distanceToNeighborNode = distanceToCurrNode + adjustedLength
            aGrade = distanceToNeighborNode + heuristic
            value = (aGrade, distanceToNeighborNode, neighborNodeOSMId)
            
            if neighborNodeOSMId not in closed:
                opened.append(value)
                closed[neighborNodeOSMId] = aGrade
                previous[neighborNodeOSMId] = currNodeId

        # for node in adjacentNodes:
        #     neighborNodeOSMId, currNodeToNodeLength = node
        #     neighborNodeLocation = help.getLatLon(neighborNodeOSMId)
        #     heuristic = help.getHeuristic(neighborNodeLocation, endLocation)
        #     distanceToNeighborNode = distanceToCurrNode + currNodeToNodeLength
        #     aGrade = distanceToNeighborNode + heuristic
        #     value = (aGrade, distanceToNeighborNode, neighborNodeOSMId)
        #     if (neighborNodeOSMId not in closed):
        #         opened.append(value)
        #         closed[neighborNodeOSMId] = aGrade
        #         previous[neighborNodeOSMId] = currNodeId
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
    return path
    """


        
