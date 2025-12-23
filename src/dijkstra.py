import helper as help
import heapq as hq
import time
import numpy as np

from blocked_edges_storage import load_penalties

def dijkstra(start, end):
    # start: OSMId of the first point
    # end: OSMId of the second point
    # return a tuple of a dictionary to trace the final path and the shortest distance

    node_penalty = load_penalties()

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

            # Nếu một trong hai node bị flood -> bỏ cạnh
            if (
                node_penalty.get(currNodeId) == float("inf")
                or node_penalty.get(neighborNodeOSMId) == float("inf")
            ):
                continue

            # Áp dụng hệ số phạt theo node tệ hơn
            penalty = max(
                node_penalty.get(currNodeId, 1.0),
                node_penalty.get(neighborNodeOSMId, 1.0),
            )
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
    nodes_visited = len([k for k in dist.keys() if dist[k] != float('inf')])

    # Nếu không có đường tới end
    finalDistance = dist.get(end, float('inf'))
    if finalDistance == float('inf'):
        print(f"Dijkstra time (seconds): {time_taken:.6f}")
        print(f"Dijkstra: Không tìm thấy đường từ {start} đến {end}")
        print(f"Dijkstra nodes visited: {nodes_visited}")
        path = []
    else:
        path = reconstruct_path(previous, start, end)
        print(f"Dijkstra time (seconds): {time_taken:.6f}")
        print(f"Dijkstra distance: {finalDistance:.6f}")
        print(f"Dijkstra path: {path}")
        print(f"Dijkstra nodes visited: {nodes_visited}")

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
