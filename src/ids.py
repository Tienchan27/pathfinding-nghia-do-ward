import helper as help
import time

def ids(start, end, max_depth=500):
    """
    Iterative Deepening Search (IDS) trên đồ thị đường đi.
    - start: OSMId điểm bắt đầu
    - end:   OSMId điểm đích
    - max_depth: giới hạn độ sâu tối đa (tránh lặp vô hạn)

    Trả về:
    - previous: dict để truy vết đường đi (previous[node] = parent)
    - final_distance: tổng độ dài đường đi từ start đến end (nếu tìm thấy),
                      hoặc float('inf') nếu không tìm thấy.
    """

    # Đọc danh sách cạnh bị chặn / phạt giống A*, Dijkstra, DFS
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

    overall_start_time = time.time()

    # Thử depth limit từ 0 đến max_depth
    for depth_limit in range(max_depth + 1):
        # Mỗi vòng IDS dùng một previous và visited riêng
        previous = {start: None}
        visited = set()
        found, final_distance = depth_limited_dfs(
            current=start,
            end=end,
            depth=0,
            limit=depth_limit,
            previous=previous,
            visited=visited,
            blocked_edges=blocked_edges,
            edge_penalty=edge_penalty
        )

        if found:
            total_time = time.time() - overall_start_time
            path = reconstruct_path(previous, start, end)
            nodes_visited = len(visited)
            print(f"IDS time (seconds): {total_time:.6f}")
            print(f"IDS distance: {final_distance:.6f}")
            print(f"IDS path: {path}")
            print(f"IDS nodes visited: {nodes_visited}")
            print(f"IDS depth limit: {depth_limit}")
            return previous, final_distance

    # Nếu không tìm được trong mọi depth_limit
    total_time = time.time() - overall_start_time
    print(f"IDS time (seconds): {total_time:.6f}")
    print(f"IDS: Không tìm thấy đường từ {start} đến {end}")
    print(f"IDS max depth: {max_depth}")
    return {}, float('inf')


def depth_limited_dfs(current, end, depth, limit, previous, visited,
                      blocked_edges, edge_penalty):
    """
    DFS có giới hạn độ sâu (Depth-Limited Search) – dùng đệ quy.
    - current: node hiện tại
    - end: node đích
    - depth: độ sâu hiện tại
    - limit: giới hạn độ sâu
    - previous, visited: cấu trúc dùng chung trong 1 vòng IDS
    - blocked_edges, edge_penalty: như trong A*/DFS trước

    Trả về:
    - found: True/False
    - distance: nếu found == True, là độ dài đường đi; ngược lại là float('inf')
    """

    visited.add(current)

    # Nếu đã tới đích → reconstruct path và tính độ dài
    if current == end:
        path = reconstruct_path(previous, start=None, end=end)
        if not path:
            return True, 0.0

        total_dist = 0.0
        for u, v in path:
            neighbors = help.getAdjacentNodes(u)
            for nb, length in neighbors:
                if nb == v:
                    total_dist += length
                    break
        return True, total_dist

    # Nếu đã đạt giới hạn depth -> không đi sâu hơn nữa
    if depth == limit:
        return False, float('inf')

    # Duyệt các hàng xóm
    adjacentNodes = help.getAdjacentNodes(current)  # (neighbor, length)

    for neighbor, length in adjacentNodes:
        # Bỏ qua cạnh bị chặn do lũ
        if (current, neighbor) in edge_penalty and edge_penalty[(current, neighbor)] == float('inf'):
            continue

        if neighbor not in visited:
            previous[neighbor] = current
            found, distance = depth_limited_dfs(
                neighbor,
                end,
                depth + 1,
                limit,
                previous,
                visited,
                blocked_edges,
                edge_penalty
            )
            if found:
                return True, distance

    return False, float('inf')


def reconstruct_path(previous, start, end):
    """
    reconstruct lại path từ previous.
    Ở đây start có thể không cần dùng (vì ta đi ngược từ end về tới None).
    """
    path = []
    current = end
    while True:
        prev = previous.get(current)
        if prev is None:
            break
        path.append((prev, current))
        current = prev

    path.reverse()
    return path
