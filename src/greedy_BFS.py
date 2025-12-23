import helper as help
import heapq as hq
import time

from blocked_edges_storage import load_penalties

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

    # Penalty theo NODE (flood/traffic)
    node_penalty = load_penalties()

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

            # Nếu node hiện tại hoặc node kề bị flood -> bỏ cạnh
            if (
                node_penalty.get(currNodeId) == float("inf")
                or node_penalty.get(neighborNodeOSMId) == float("inf")
            ):
                continue

            if neighborNodeOSMId in visited:
                continue

            # Áp dụng hệ số phạt để tính distance thực (traffic)
            penalty = max(
                node_penalty.get(currNodeId, 1.0),
                node_penalty.get(neighborNodeOSMId, 1.0),
            )
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

    if end not in dist:
        finalDistance = float('inf')
        path = []
        print(f"Greedy BFS time (seconds): {time_taken:.6f}")
        print(f"Greedy BFS: Không tìm thấy đường từ {start} đến {end}")
        print(f"Greedy BFS nodes visited: {len(visited)}")
    else:
        finalDistance = dist[end]
        path = reconstruct_path(previous, start, end)
        print(f"Greedy BFS time (seconds): {time_taken:.6f}")
        print(f"Greedy BFS distance: {finalDistance:.6f}")
        print(f"Greedy BFS path: {path}")
        print(f"Greedy BFS nodes visited: {len(visited)}")

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
