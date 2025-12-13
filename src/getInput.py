import haversine
import os
import helper
import math

# Cache để tránh load lại nhiều lần
_node_coords_cache = None
_adj_cache = None

def _load_graph_data():
    """Load graph data từ helper module một lần"""
    global _node_coords_cache, _adj_cache
    if _node_coords_cache is None:
        # Import helper để lấy access vào _node_coords và _adj
        # Vì helper không export trực tiếp, ta cần access qua các hàm
        # Tuy nhiên, ta có thể build lại từ graphml như helper làm
        import xmltodict
        graphml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/map3.graphml"))
        with open(graphml_path, "rb") as graphml:
            xmldoc = xmltodict.parse(graphml, xml_attribs=True)
        
        _nodes = xmldoc["graphml"]["graph"]["node"]
        _edges = xmldoc["graphml"]["graph"]["edge"]
        
        _node_coords_cache = {}
        _adj_cache = {}
        
        # Build node_coords
        for node in _nodes:
            node_id = node["@id"]
            lat = None
            lon = None
            for datum in node["data"]:
                if datum["@key"] == "d4":
                    lat = float(datum["#text"])
                elif datum["@key"] == "d5":
                    lon = float(datum["#text"])
            if lat is not None and lon is not None:
                _node_coords_cache[node_id] = (lat, lon)
        
        # Build adjacency list
        road = {
            "motorway":0, "trunk":0, "primary":0,"primary_link":0, "secondary":0, "tertiary":0, 
            "secondary_link":0, "tertiary_link":0, "residential":0, "unclassified":0, 
            "service":0, "living_street":0
        }
        
        for edge in _edges:
            src = edge["@source"]
            tgt = edge["@target"]
            
            length = None
            highway_type = None
            
            for datum in edge["data"]:
                if datum["@key"] == "d13":
                    length = float(datum["#text"])
                elif datum["@key"] == "d14":
                    highway_type = datum["#text"]
            
            if highway_type in road and length is not None:
                if src not in _adj_cache:
                    _adj_cache[src] = []
                _adj_cache[src].append((tgt, length))
    
    return _node_coords_cache, _adj_cache

def _point_to_line_distance(point, line_start, line_end):
    """Tính khoảng cách từ điểm đến đoạn thẳng (edge) và trả về điểm gần nhất trên edge"""
    px, py = point[0], point[1]
    x1, y1 = line_start[0], line_start[1]
    x2, y2 = line_end[0], line_end[1]
    
    # Vector từ line_start đến line_end
    dx = x2 - x1
    dy = y2 - y1
    
    # Nếu edge là một điểm
    if dx == 0 and dy == 0:
        return haversine.haversine(point, line_start), line_start
    
    # Tính t (tham số trên đoạn thẳng, 0 <= t <= 1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    
    # Clamp t về [0, 1]
    t = max(0, min(1, t))
    
    # Điểm gần nhất trên edge
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    nearest_point = (nearest_x, nearest_y)
    
    distance = haversine.haversine(point, nearest_point)
    return distance, nearest_point

def getNearestPoint(lat, lon):
    """
    Tìm node gần nhất trên graph từ vị trí user click.
    Ưu tiên các node có edges (không bị cô lập).
    """
    point = (float(lat), float(lon))
    node_coords, adj = _load_graph_data()
    
    min_distance = float('inf')
    best_node_id = None
    best_location = None
    
    min_distance_with_edges = float('inf')
    best_node_id_with_edges = None
    best_location_with_edges = None
    
    # Bước 1: Tìm các candidate nodes trong bán kính hợp lý
    # Tăng bán kính lên 300m để đảm bảo tìm được node
    search_radius = 0.3  # ~300m trong haversine
    candidate_nodes = []
    
    for node_id, node_coord in node_coords.items():
        dist = haversine.haversine(point, node_coord)
        if dist < search_radius:
            candidate_nodes.append((node_id, node_coord, dist))
        # Đồng thời cập nhật node gần nhất để có fallback
        if dist < min_distance:
            min_distance = dist
            best_node_id = node_id
            best_location = node_coord
        
        # Ưu tiên node có edges
        if dist < search_radius and node_id in adj and len(adj[node_id]) > 0:
            if dist < min_distance_with_edges:
                min_distance_with_edges = dist
                best_node_id_with_edges = node_id
                best_location_with_edges = node_coord
    
    # Nếu không tìm thấy node trong bán kính, đã có fallback từ trên
    
    # Bước 2: Với các candidate nodes, kiểm tra xem điểm click có gần edge nào không
    # Nếu có, chọn node của edge đó (ưu tiên node gần điểm click hơn)
    if candidate_nodes:
        # Sắp xếp theo khoảng cách
        candidate_nodes.sort(key=lambda x: x[2])
        
        # Xét top 50 nodes gần nhất và các edges của chúng để tăng độ chính xác
        for node_id, node_coord, node_dist in candidate_nodes[:50]:
            # Kiểm tra node trực tiếp (chỉ nếu có edges)
            if node_id in adj and len(adj[node_id]) > 0:
                if node_dist < min_distance_with_edges:
                    min_distance_with_edges = node_dist
                    best_node_id_with_edges = node_id
                    best_location_with_edges = node_coord
            
            # Kiểm tra các edges từ node này
            if node_id in adj and len(adj[node_id]) > 0:
                for neighbor_id, edge_length in adj[node_id]:
                    if neighbor_id in node_coords:
                        neighbor_coord = node_coords[neighbor_id]
                        edge_dist, nearest_on_edge = _point_to_line_distance(
                            point, node_coord, neighbor_coord
                        )
                        
                        # Nếu điểm click gần edge hơn, chọn node nào gần điểm click hơn
                        if edge_dist < min_distance_with_edges:
                            min_distance_with_edges = edge_dist
                            # Chọn node gần điểm click hơn
                            node_to_point = haversine.haversine(node_coord, point)
                            neighbor_to_point = haversine.haversine(neighbor_coord, point)
                            
                            if node_to_point <= neighbor_to_point:
                                best_node_id_with_edges = node_id
                                best_location_with_edges = node_coord
                            else:
                                best_node_id_with_edges = neighbor_id
                                best_location_with_edges = neighbor_coord
    
    # Ưu tiên node có edges, nếu không có thì dùng node gần nhất
    if best_location_with_edges is not None:
        return best_location_with_edges
    
    # Fallback: nếu vẫn chưa tìm thấy node có edges, tìm node gần nhất trong toàn bộ graph
    if best_location is None:
        for node_id, node_coord in node_coords.items():
            dist = haversine.haversine(point, node_coord)
            if dist < min_distance:
                min_distance = dist
                best_node_id = node_id
                best_location = node_coord
    
    return best_location if best_location else (lat, lon)

def getNearestNodeId(lat, lon):
    """
    Trả về node_id gần nhất thay vì tọa độ.
    Dùng khi cần node_id trực tiếp.
    """
    point = (float(lat), float(lon))
    node_coords, adj = _load_graph_data()
    
    min_distance = float('inf')
    best_node_id = None
    
    # Tìm node gần nhất
    for node_id, node_coord in node_coords.items():
        dist = haversine.haversine(point, node_coord)
        if dist < min_distance:
            min_distance = dist
            best_node_id = node_id
    
    return best_node_id

def getAllPoints():
    node_coords, _ = _load_graph_data()
    ans = []
    for node_id, (lat, lon) in node_coords.items():
        ans.append([lat, lon])
    return ans
        
    
    