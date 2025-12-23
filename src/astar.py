import helper as help
import heapq as hq
import time
import numpy as np

from blocked_edges_storage import load_penalties

latlon_cache = {}

def get_latlon_cached(node):
    if node not in latlon_cache:
        latlon_cache[node] = help.getLatLon(node)
    return latlon_cache[node]

def astar(start, end):
    """
    A* chuẩn: có g_score, f_score, cho phép relax lại node nếu tìm được đường tốt hơn.
    Tối ưu: chỉ push node vào heap nếu chưa có trong open_set hoặc có f_score tốt hơn.
    Trả về:
        - previous: dict để reconstruct đường đi
        - final_distance: tổng độ dài đường (đã nhân penalty)
    """

    start_location = get_latlon_cached(start)
    end_location = get_latlon_cached(end)

    # Load penalty/banned-edges *tại thời điểm gọi* để luôn thấy
    # các flood/traffic mới lưu trong blocked_edges.txt
    edge_penalty = load_penalties()

    open_heap = []                     # (f, node)
    open_set = {}                     # Track nodes trong heap: {node: f_score} để tránh duplicate
    g_score = {start: 0.0}             # chi phí từ start đến node
    f_start = help.getHeuristic(start_location, end_location)
    f_score = {start: f_start}
    previous = {start: None}

    hq.heappush(open_heap, (f_start, start))
    open_set[start] = f_start

    closed = set()
    t0 = time.time()

    while open_heap:
        curr_f, curr_node = hq.heappop(open_heap)

        # Nếu node này đã xử lý với f tốt hơn rồi thì bỏ qua (entry cũ trong heap)
        if curr_node in closed:
            continue

        # Kiểm tra xem f_score hiện tại có còn đúng không (có thể đã được cập nhật)
        if curr_node in f_score and curr_f > f_score[curr_node]:
            continue

        if curr_node == end:
            final_distance = g_score[curr_node]
            path = reconstruct_path(previous, start, end)
            t1 = time.time()
            print(f"A* time (seconds): {t1 - t0:.6f}")
            print(f"A* distance: {final_distance:.6f}")
            print(f"A* path: {path}")
            print(f"A* nodes visited: {len(closed)}")
            return previous, final_distance

        closed.add(curr_node)
        if curr_node in open_set:
            del open_set[curr_node]  # Remove khỏi open_set khi đã closed

        for neighbor_id, edge_length in help.getAdjacentNodes(curr_node):
            # Bỏ qua nếu đã closed
            if neighbor_id in closed:
                continue

            # Bỏ qua cạnh bị chặn do lũ (penalty = inf)
            if edge_penalty.get((curr_node, neighbor_id)) == float("inf"):
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

            # Chỉ push vào heap nếu:
            # 1. Node chưa có trong open_set, HOẶC
            # 2. Node đã có trong open_set nhưng f_score tốt hơn đáng kể (giảm duplicate entries)
            if neighbor_id not in open_set or f < open_set.get(neighbor_id, float('inf')):
                hq.heappush(open_heap, (f, neighbor_id))
                open_set[neighbor_id] = f

    # Không tìm được đường
    t1 = time.time()
    print(f"A* time (seconds): {t1 - t0:.6f}")
    print(f"A*: Không tìm thấy đường từ {start} đến {end}")
    print(f"A* nodes visited: {len(closed)}")
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

