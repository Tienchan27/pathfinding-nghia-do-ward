import helper as help
import heapq as hq
import time
import os

# Code mới cho phép đánh dấu nhiều đoạn ngập cùng lúc. Code cũ nếu đánh dấu đoạn ngập mới sẽ xóa đoạn ngập cũ.
# Anh chị cần dùng lại code cũ thì lấy trong phần comment ở dưới ạ.

# =======================================
# Cache LatLon
# =======================================

latlon_cache = {}

def get_latlon_cached(node):
    if node not in latlon_cache:
        latlon_cache[node] = help.getLatLon(node)
    return latlon_cache[node]

# =======================================
# A* flood: KHÔNG dùng penalty, KHÔNG né flood
# chỉ đơn thuần tìm đường ngắn nhất theo độ dài cạnh
# =======================================

def astar_flood(start, end):
    """
    A* dùng cho chức năng 'đánh dấu lụt':
    - Không đọc blocked_edges.txt
    - Không áp dụng penalty traffic/flood
    - Không bỏ qua cạnh nào
    -> Chỉ tìm đường ngắn nhất theo độ dài cạnh hiện tại.

    Sau đó có thể dùng đường tìm được để ghi FLOOD vào blocked_edges.txt.

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
            print("A* flood (improved) time:", t1 - t0, "seconds")
            print("A* flood (improved) distance:", final_distance)
            # mark_flood_on_path(path)  # Removed: chỉ lưu khi user click button
            # print("A* flood path:", path)
            return previous, final_distance

        closed.add(curr_node)

        for neighbor_id, edge_length in help.getAdjacentNodes(curr_node):
            # KHÔNG kiểm tra flood / blocked ở đây
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
    print("A* flood (improved) time:", t1 - t0, "seconds")
    print("Không tìm được đường (A* flood) từ", start, "tới", end)
    # mark_flood_on_path(path)  # Removed: chỉ lưu khi user click button
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

FILE_PATH = 'data/blocked_edges.txt'

def mark_flood_on_path(path):
    """
    Nhận path là list các cạnh [(u1, v1), (u2, v2), ...]
    Ghi thêm các cạnh 'flood' vào blocked_edges.txt dạng:
        u v flood
    Không xoá dữ liệu cũ, không ghi trùng dòng.
    """

    print("file founded")

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

    # Append các cạnh flood mới
    with open(FILE_PATH, 'a', encoding='utf-8') as f:
        for u, v in path:
            line = f"{u} {v} flood"
            if line not in existing_lines:
                f.write(line + "\n")
                existing_lines.add(line)



"""
def astar_flood(start, end):
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
                edge_line = f"{u} {v} flood"
                if edge_line not in existing_edges:
                    f.write(edge_line + '\n')
                    existing_edges.add(edge_line)
            # Write back any existing traffic edges
            for edge in existing_edges:
                if edge.endswith('traffic'):
                    f.write(edge + '\n')

    except Exception as e:
        print(f"Error handling blocked_edges.txt: {str(e)}")
        # Continue execution even if file operations fail
    
    return path
"""
