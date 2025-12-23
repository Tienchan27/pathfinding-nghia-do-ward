import helper as help
import time

from blocked_edges_storage import load_penalties

def dfs(start, end=None):
    """
    DFS trên đồ thị đường đi:
    - start: OSMId điểm bắt đầu
    - end: nếu truyền, sẽ dừng khi gặp end; nếu None thì duyệt hết thành phần liên thông của start
    Trả về:
    - previous: dict để truy vết đường đi
    - final_distance: tổng độ dài đường đi từ start tới end (nếu có end), 
                      hoặc None nếu không truyền end hoặc không tìm thấy đường
    """

    # Penalty theo NODE (flood/traffic)
    node_penalty = load_penalties()

    visited = set()
    previous = {}
    stack = [start]
    previous[start] = None

    s = time.time()

    while stack:
        curr = stack.pop()

        if curr in visited:
            continue

        visited.add(curr)

        # Nếu có truyền end và đã tới đích thì dừng luôn
        if end is not None and curr == end:
            break

        # Duyệt tất cả hàng xóm
        adjacentNodes = help.getAdjacentNodes(curr)  # (neighbor, length)

        for neighbor, length in adjacentNodes:
            # Nếu node hiện tại hoặc node kề bị flood -> bỏ cạnh
            if (
                node_penalty.get(curr) == float("inf")
                or node_penalty.get(neighbor) == float("inf")
            ):
                continue

            if neighbor not in visited:
                previous[neighbor] = curr
                stack.append(neighbor)

    elapsed = time.time() - s

    final_distance = None

    # Nếu có end và tìm được đường, reconstruct + tính độ dài
    if end is not None and end in visited:
        path = reconstruct_path(previous, start, end)

        # Tính tổng độ dài đường đi (dùng helper.getAdjacentNodes để lấy weight)
        total_dist = 0.0
        for u, v in path:
            # tìm chiều dài cạnh u-v
            neighbors = help.getAdjacentNodes(u)
            for nb, length in neighbors:
                if nb == v:
                    total_dist += length
                    break
        final_distance = total_dist
        print(f"DFS time (seconds): {elapsed:.6f}")
        print(f"DFS distance: {final_distance:.6f}")
        print(f"DFS path: {path}")
        print(f"DFS nodes visited: {len(visited)}")
    else:
        print(f"DFS time (seconds): {elapsed:.6f}")
        print(f"DFS: Không tìm thấy đường từ {start} đến {end}")
        print(f"DFS nodes visited: {len(visited)}")
    
    return previous, final_distance


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
