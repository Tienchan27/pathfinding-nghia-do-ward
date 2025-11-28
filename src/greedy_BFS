import helper as help
import heapq as hq
import time

def greedy_best_first(start, end):
    """
    Greedy Best-First Search:
    - Ưu tiên mở node có heuristic nhỏ nhất (gần đích nhất theo h),
      không quan tâm tổng độ dài đường đã đi.
    - Có xử lý blocked_edges (flood) giống A*/Dijkstra.
    Trả về:
        previous: dict để truy vết đường đi
        finalDistance: tổng độ dài đường đi theo trọng số (nếu tìm được), 
                       hoặc float('inf') nếu không có đường.
    """

    # Đọc danh sách cạnh bị chặn / bị phạt (phạt chỉ để tính distance,
    # còn thứ tự mở node chỉ dựa trên heuristic)
    blocked_edges = set()
    edge_penalty = {}

    with open('data/blocked_edges.txt', 'r') as f:
        for line in f:
            u, v, reason = line.strip().split()
            blocked_edges.add((u, v))
            blocked_edges.add((v, u))  # đồ thị có thể vô hướng

            if reason == "traffic":
                edge_penalty[(u, v)] = 5  # hệ số phạt cho tắc đường
                edge_penalty[(v, u)] = 5
            elif reason == "flood":
                edge_penalty[(u, v)] = float('inf')  # lũ -> không đi được
                edge_penalty[(v, u)] = float('inf')

    previous = {}
    previous[start] = None

    # lưu khoảng cách thực tế để báo finalDistance (GBFS vẫn cần)
    dist = {start: 0.0}

    startLocation = help.getLatLon(start)
    endLocation = help.getLatLon(end)

    # hàng đợi ưu tiên: (heuristic, nodeId)
    h_start = help.getHeuristic(startLocation, endLocation)
    opened = [(h_start, start)]
    hq.heapify(opened)

    visited = set()

    s = time.time()

    while opened:
        curr_h, currNodeId = hq.heappop(opened)

        if currNodeId in visited:
            continue

        visited.add(currNodeId)

        if currNodeId == end:
            # tìm thấy đích
            break

        adjacentNodes = help.getAdjacentNodes(currNodeId)  # (neighborId, length)
        for neighborNodeOSMId, currNodeToNodeLength in adjacentNodes:

            # Bỏ qua cạnh bị chặn do lũ
            if (currNodeId, neighborNodeOSMId) in edge_penalty and edge_penalty[(currNodeId, neighborNodeOSMId)] == float('inf'):
                continue

            if neighborNodeOSMId in visited:
                continue

            # Áp dụng hệ số phạt để tính distance thực
            penalty = edge_penalty.get((currNodeId, neighborNodeOSMId), 1)
            adjustedLength = currNodeToNodeLength * penalty

            # cập nhật distance thực tế (dùng cho báo cáo finalDistance)
            newDist = dist[currNodeId] + adjustedLength
            oldDist = dist.get(neighborNodeOSMId, float('inf'))
            if newDist < oldDist:
                dist[neighborNodeOSMId] = newDist
                previous[neighborNodeOSMId] = currNodeId

            # heuristic để ưu tiên mở node
            neighborLocation = help.getLatLon(neighborNodeOSMId)
            h_neighbor = help.getHeuristic(neighborLocation, endLocation)

            # Greedy: key trong heap chỉ là heuristic
            hq.heappush(opened, (h_neighbor, neighborNodeOSMId))

    time_taken = time.time() - s
    print("Greedy Best-First Search time (seconds):", time_taken)
    print("Số node đã duyệt (GBFS):", len(visited))

    if end not in dist:
        finalDistance = float('inf')
        path = []
        print("GBFS: không tìm được đường đi từ", start, "đến", end)
    else:
        finalDistance = dist[end]
        path = reconstruct_path(previous, start, end)
        print("GBFS shortest path (theo distance thực mà nó đi được):", path)
        print("GBFS path length:", finalDistance)

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
