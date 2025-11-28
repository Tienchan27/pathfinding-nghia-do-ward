import helper as help
import heapq as hq
import time
import numpy as np


def dijkstra(start, end):
    # start: OSMId of the first point
    # end: OSMId of the second point
    # return a tuple of a dictionary to trace the final path and the shortest distance

    blocked_edges = set()
    edge_penalty = {}

    # Đọc danh sách cạnh bị chặn / bị phạt giống như trong A*
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
    dist = {}          # dist[node] = khoảng cách ngắn nhất đã biết từ start đến node
    previous[start] = None

    # Priority queue: (khoảng cách hiện tại từ start, node)
    opened = [(0, start)]
    hq.heapify(opened)

    # Khởi tạo khoảng cách vô cùng cho các node, riêng start = 0
    dist[start] = 0

    max_time = 0   
    loops = 0


    s = time.time()
    while opened:
        s1 = time.time()
        currDist, currNodeId = hq.heappop(opened)

        # Nếu node lấy ra đã có khoảng cách tốt hơn trong dist thì bỏ qua
        if currDist > dist.get(currNodeId, float('inf')):
            continue

        # Nếu đã tới đích thì dừng
        if currNodeId == end:
            break

        # Lấy các node kề
        adjacentNodes = help.getAdjacentNodes(currNodeId)  # mỗi phần tử: (neighborNodeOSMId, length)

        for neighborNodeOSMId, currNodeToNodeLength in adjacentNodes:

            # Bỏ qua cạnh bị chặn do lũ (penalty = inf)
            if (currNodeId, neighborNodeOSMId) in edge_penalty and edge_penalty[(currNodeId, neighborNodeOSMId)] == float('inf'):
                continue

            # Áp dụng hệ số phạt nếu tắc đường
            penalty = edge_penalty.get((currNodeId, neighborNodeOSMId), 1)
            adjustedLength = currNodeToNodeLength * penalty

            newDist = currDist + adjustedLength

            # Cập nhật khoảng cách nếu tốt hơn
            if newDist < dist.get(neighborNodeOSMId, float('inf')):
                dist[neighborNodeOSMId] = newDist
                previous[neighborNodeOSMId] = currNodeId
                hq.heappush(opened, (newDist, neighborNodeOSMId))
            
            t1 = time.time()
            loops = loops + 1
            if(t1 - s1 > max_time):
                max_time = t1 - s1

    time_taken = time.time() - s
    print("Time taken to find path (in second): " + str(time_taken))

    # Nếu không có đường tới end
    finalDistance = dist.get(end, float('inf'))
    if finalDistance == float('inf'):
        print("No path found.")
        path = []
    else:
        path = reconstruct_path(previous, start, end)
        print(path)
        print("Dijsktra length: ", finalDistance)

    return previous, finalDistance


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
