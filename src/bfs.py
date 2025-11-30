import helper as help
import time
from collections import deque

def bfs(start, end):
    """
    BFS trên đồ thị đường đi:
    - start: OSMId điểm bắt đầu
    - end:   OSMId điểm đích

    Trả về:
    - previous: dict để truy vết đường đi (previous[node] = parent)
    - final_distance: tổng độ dài đường đi (cộng các length của cạnh trên path),
                      hoặc float('inf') nếu không tìm thấy đường.
    Lưu ý: BFS trên đồ thị có trọng số KHÔNG đảm bảo ngắn nhất về độ dài,
           chỉ ngắn nhất về số cạnh. Dùng để làm baseline so sánh.
    """

    # Đọc danh sách cạnh bị chặn / bị phạt giống các thuật toán khác
    blocked_edges = set()
    edge_penalty = {}

    try:
        with open('data/blocked_edges.txt', 'r', encoding='utf-8') as f:
            for line in f:
                u, v, reason = line.strip().split()
                blocked_edges.add((u, v))
                blocked_edges.add((v, u))  # đồ thị vô hướng

                if reason == "traffic":
                    edge_penalty[(u, v)] = 5
                    edge_penalty[(v, u)] = 5
                elif reason == "flood":
                    edge_penalty[(u, v)] = float('inf')
                    edge_penalty[(v, u)] = float('inf')
    except FileNotFoundError:
        # Nếu chưa có file thì coi như không có cạnh bị chặn / phạt
        pass

    visited = set()
    previous = {start: None}

    q = deque()
    q.append(start)

    s = time.time()

    found = False

    while q:
        curr = q.popleft()

        if curr in visited:
            continue

        visited.add(curr)

        # Nếu tới đích thì dừng
        if curr == end:
            found = True
            break

        # Duyệt hàng xóm
        adjacentNodes = help.getAdjacentNodes(curr)  # (neighbor, length)

        for neighbor, length in adjacentNodes:
            # Bỏ qua cạnh bị chặn do lũ
            if (curr, neighbor) in edge_penalty and edge_penalty[(curr, neighbor)] == float('inf'):
                continue

            if neighbor not in visited and neighbor not in previous:
                previous[neighbor] = curr
                q.append(neighbor)

    elapsed = time.time() - s

    if not found:
        print(f"BFS time (seconds): {elapsed:.6f}")
        print(f"BFS: Không tìm thấy đường từ {start} đến {end}")
        print(f"BFS nodes visited: {len(visited)}")
        return {}, float('inf')

    # Reconstruct path để tính độ dài
    path = reconstruct_path(previous, start, end)

    total_dist = 0.0
    for u, v in path:
        neighbors = help.getAdjacentNodes(u)
        for nb, length in neighbors:
            if nb == v:
                total_dist += length
                break

    print(f"BFS time (seconds): {elapsed:.6f}")
    print(f"BFS distance: {total_dist:.6f}")
    print(f"BFS path: {path}")
    print(f"BFS nodes visited: {len(visited)}")
    return previous, total_dist


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
