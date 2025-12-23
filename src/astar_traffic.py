import helper as help
import heapq as hq
import time
import numpy as np
import os

latlon_cache = {}

def get_latlon_cached(node):
    if node not in latlon_cache:
        latlon_cache[node] = help.getLatLon(node)
    return latlon_cache[node]

def astar_traffic(start, end):
    """
    A* dùng cho chức năng 'đánh dấu đường tắc (traffic)':
    - KHÔNG đọc blocked_edges.txt
    - KHÔNG bỏ qua cạnh nào
    - KHÔNG áp dụng penalty
    -> chỉ tìm đường ngắn nhất theo độ dài cạnh hiện tại.

    Sau đó dùng đường tìm được để ghi TRAFFIC vào blocked_edges.txt.

    Trả về:
        previous: dict {node: parent}
        final_distance: tổng độ dài đường đi
    """

    start_location = get_latlon_cached(start)
    end_location = get_latlon_cached(end)

    g_score = {start: 0.0}
    f_start = help.getHeuristic(start_location, end_location)
    f_score = {start: f_start}
    previous = {start: None}

    open_heap = []  # (f, node)
    hq.heappush(open_heap, (f_start, start))

    closed = set()
    t0 = time.time()

    while open_heap:
        curr_f, curr_node = hq.heappop(open_heap)

        if curr_node in closed:
            continue

        if curr_node == end:
            final_distance = g_score[curr_node]
            path = reconstruct_path(previous, start, end)
            t1 = time.time()
            print("A* traffic time:", t1 - t0, "seconds")
            print("A* traffic distance:", final_distance)
            return previous, final_distance

        closed.add(curr_node)

        for neighbor_id, edge_length in help.getAdjacentNodes(curr_node):
            # KHÔNG kiểm tra traffic / flood ở đây
            adjusted_length = edge_length

            tentative_g = g_score[curr_node] + adjusted_length

            if tentative_g >= g_score.get(neighbor_id, float('inf')):
                continue

            g_score[neighbor_id] = tentative_g
            neighbor_location = get_latlon_cached(neighbor_id)
            f = tentative_g + help.getHeuristic(neighbor_location, end_location)
            f_score[neighbor_id] = f
            previous[neighbor_id] = curr_node

            hq.heappush(open_heap, (f, neighbor_id))

    # Không tìm được đường
    t1 = time.time()
    print("A* traffic (improved) time:", t1 - t0, "seconds")
    print("Không tìm được đường (A* traffic) từ", start, "tới", end)
    return previous, float('inf')

def reconstruct_path(previous, start, end):
    path = []
    current = end
    while current != start:
        prev = previous.get(current)
        if prev is None:
            return []
        path.append((prev, current))
        current = prev
    path.reverse()
    return path

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_PATH = os.path.join(BASE_DIR, "data", "blocked_edges.txt")

def mark_flood_on_path(path):
    """
    Nhận path là list các cạnh [(u1, v1), (u2, v2), ...]
    Ghi thêm các cạnh 'flood' vào blocked_edges.txt dạng:
        u v flood
    Không xoá dữ liệu cũ, không ghi trùng dòng.
    """

    # Đảm bảo thư mục/file tồn tại
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists(FILE_PATH):
        open(FILE_PATH, 'a', encoding='utf-8').close()

    # Đọc toàn bộ nội dung hiện tại để tránh ghi trùng
    existing_lines = set()
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            existing_lines.add(line.strip())

    # Append các cạnh traffic mới, tránh ghi trùng
    with open(FILE_PATH, 'a', encoding='utf-8') as f:
        for u, v in path:
            line = f"{u} {v} traffic"
            if line not in existing_lines:
                f.write(line + "\n")
                existing_lines.add(line)



