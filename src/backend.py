from flask import Flask, request, jsonify
from flask_cors import CORS
import getInput
import astar
import astar_flood
import astar_traffic
import dijkstra
import greedy_BFS
import helper
import json
import time
import dfs
import ids
import bfs
from blocked_edges_storage import append_path, reset_storage, storage_path
import os
import time

app = Flask(__name__)
CORS(app)

def get_path_edges(pathDict, endID):
    """Extract edge list from pathDict for saving to blocked_edges"""
    edges = []
    point = endID
    while pathDict.get(point) is not None:
        prev = pathDict[point]
        edges.append((prev, point))
        point = prev
    return edges

@app.route('/calculate_flood', methods=['GET'])
def calculate_flood():
    raw_input = request.args.get('pntdata').split(',')
    mappedSourceLoc = getInput.getNearestPoint(raw_input[0], raw_input[1])
    mappedDestLoc = getInput.getNearestPoint(raw_input[2], raw_input[3])
    print("Location of the first point " + raw_input[0] + " " + raw_input[1])
    print("Location of the second point " + raw_input[2] + " " + raw_input[3])
    print("nearest of the first point " + str(mappedSourceLoc[0]) + " " + str(mappedSourceLoc[1]))
    print("nearest of the second point " + str(mappedDestLoc[0]) + " " + str(mappedDestLoc[1]))
    start = helper.getOSMId(mappedSourceLoc[0], mappedSourceLoc[1])
    print("Start Id: " + start)
    end = helper.getOSMId(mappedDestLoc[0], mappedDestLoc[1])
    print("End Id: " + end)
    
    if not start or not end:
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": "Không tìm thấy node trên bản đồ"
        }), 400
    
    if start == end:
        return jsonify({
            "coordinates": [[mappedSourceLoc[0], mappedSourceLoc[1]]],
            "edges": []
        })
    
    try:
        pathDict, finalDistance = astar_flood.astar_flood(start, end)
        print("Shortest distance: " + str(finalDistance))
        
        if finalDistance == float('inf') or end not in pathDict:
            return jsonify({
                "coordinates": [],
                "edges": [],
                "error": "Không tìm thấy đường đi giữa hai điểm"
            })
        
        coordinates = helper.getResponseLeafLet(pathDict, end)
        path_edges = get_path_edges(pathDict, end)
        
        return jsonify({
            "coordinates": coordinates,
            "edges": path_edges
        })
    except Exception as e:
        app.logger.error(f"Error in pathfinding: {str(e)}")
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": f"Lỗi khi tìm đường: {str(e)}"
        }), 500

    start_time = time.time()

    pathDict, finalDistance = astar_flood.astar_flood(start, end)

    end_time = time.time()
    elapsed_time = (end_time - start_time)

    print("Shortest distance: " + str(finalDistance))
    path_data = helper.getResponseLeafLet(pathDict, end)    
    return jsonify({
        "path": path_data,
        "time": round(elapsed_time, 2), # Round to 2 decimal places
        "distance": round(finalDistance, 2),
        "visited": 0 
    })

@app.route('/calculate', methods=['GET'])
def calculate():
    algorithm = request.args.get('algorithm', 'astar')
    raw_input = request.args.get('pntdata').split(',')
    mappedSourceLoc = getInput.getNearestPoint(raw_input[0], raw_input[1])
    mappedDestLoc = getInput.getNearestPoint(raw_input[2], raw_input[3])
    print("Location of the first point " + raw_input[0] + " " + raw_input[1])
    print("Location of the second point " + raw_input[2] + " " + raw_input[3])
    print("nearest of the first point " + str(mappedSourceLoc[0]) + " " + str(mappedSourceLoc[1]))
    print("nearest of the second point " + str(mappedDestLoc[0]) + " " + str(mappedDestLoc[1]))
    
    start = helper.getOSMId(mappedSourceLoc[0], mappedSourceLoc[1])
    print("Start Id: " + start)
    end = helper.getOSMId(mappedDestLoc[0], mappedDestLoc[1])
    print("End Id: " + end)

    # Validate start and end nodes
    if not start or not end:
        error_msg = "Không tìm thấy node trên bản đồ"
        if not start:
            error_msg += f" (điểm bắt đầu: {mappedSourceLoc})"
        if not end:
            error_msg += f" (điểm kết thúc: {mappedDestLoc})"
        print("ERROR: " + error_msg)
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": error_msg
        }), 400
    
    if start == end:
        # Same point, return single coordinate
        return jsonify({
            "coordinates": [[mappedSourceLoc[0], mappedSourceLoc[1]]],
            "edges": []
        })
    
    # Check if nodes have edges (connectivity check)
    start_adjacent = helper.getAdjacentNodes(start)
    end_adjacent = helper.getAdjacentNodes(end)
    print(f"Start node has {len(start_adjacent)} adjacent nodes")
    print(f"End node has {len(end_adjacent)} adjacent nodes")
    
    if len(start_adjacent) == 0:
        error_msg = f"Điểm bắt đầu không có đường kết nối (node {start})"
        print("ERROR: " + error_msg)
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": error_msg
        }), 400
    
    if len(end_adjacent) == 0:
        error_msg = f"Điểm kết thúc không có đường kết nối (node {end})"
        print("ERROR: " + error_msg)
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": error_msg
        }), 400
    
    # Normalize algorithm aliases from client
    if algorithm == 'normal':
        algorithm = 'astar'
    if algorithm == 'greedy':
        algorithm = 'greedy_bfs'

    # Route to appropriate algorithm
    try:
        start_time = time.time()

        if algorithm == 'astar':
            pathDict, finalDistance = astar.astar(start, end)
        elif algorithm == 'dijkstra':
            pathDict, finalDistance = dijkstra.dijkstra(start, end)
        elif algorithm == 'greedy_bfs':
            pathDict, finalDistance = greedy_BFS.greedy_best_first(start, end)
        elif algorithm == 'bfs':
            pathDict, finalDistance = bfs.bfs(start, end)
        elif algorithm == 'dfs':
            pathDict, finalDistance = dfs.dfs(start, end)
            if finalDistance is None:
                finalDistance = float('inf')
        elif algorithm == 'ids':
            pathDict, finalDistance = ids.ids(start, end)
        else:
            pathDict, finalDistance = astar.astar(start, end)
        
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000

        print("Shortest distance: " + str(finalDistance))
        
        # Check if path was found
        if finalDistance == float('inf') or end not in pathDict:
            return jsonify({
                "coordinates": [],
                "edges": [],
                "error": "Không tìm thấy đường đi giữa hai điểm"
            })
        
        coordinates = helper.getResponseLeafLet(pathDict, end)
        path_edges = get_path_edges(pathDict, end)
        
        if not coordinates:
            return jsonify({
                "coordinates": [],
                "edges": [],
                "error": "Không thể tạo đường đi"
            })
        
        return jsonify({
            "path": coordinates,
            "time": round(elapsed_time, 2),
            "distance": round(finalDistance, 2),
            "edges": path_edges
        })
    except Exception as e:
        app.logger.error(f"Error in pathfinding: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": f"Lỗi khi tìm đường: {str(e)}"
        }), 500

@app.route('/calculate_traffic', methods=['GET'])
def calculate_traffic():
    raw_input = request.args.get('pntdata').split(',')
    mappedSourceLoc = getInput.getNearestPoint(raw_input[0], raw_input[1])
    mappedDestLoc = getInput.getNearestPoint(raw_input[2], raw_input[3])
    print("Location of the first point " + raw_input[0] + " " + raw_input[1])
    print("Location of the second point " + raw_input[2] + " " + raw_input[3])
    print("nearest of the first point " + str(mappedSourceLoc[0]) + " " + str(mappedSourceLoc[1]))
    print("nearest of the second point " + str(mappedDestLoc[0]) + " " + str(mappedDestLoc[1]))
    start = helper.getOSMId(mappedSourceLoc[0], mappedSourceLoc[1])
    print("Start Id: " + start)
    end = helper.getOSMId(mappedDestLoc[0], mappedDestLoc[1])
    print("End Id: " + end)
    
    if not start or not end:
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": "Không tìm thấy node trên bản đồ"
        }), 400
    
    if start == end:
        return jsonify({
            "coordinates": [[mappedSourceLoc[0], mappedSourceLoc[1]]],
            "edges": []
        })
    
    try:
        pathDict, finalDistance = astar_traffic.astar_traffic(start, end)
        print("Shortest distance: " + str(finalDistance))
        
        if finalDistance == float('inf') or end not in pathDict:
            return jsonify({
                "coordinates": [],
                "edges": [],
                "error": "Không tìm thấy đường đi giữa hai điểm"
            })
        
        coordinates = helper.getResponseLeafLet(pathDict, end)
        path_edges = get_path_edges(pathDict, end)
        
        return jsonify({
            "coordinates": coordinates,
            "edges": path_edges
        })
    except Exception as e:
        app.logger.error(f"Error in pathfinding: {str(e)}")
        return jsonify({
            "coordinates": [],
            "edges": [],
            "error": f"Lỗi khi tìm đường: {str(e)}"
        }), 500

    start_time = time.time()

    pathDict, finalDistance = astar_traffic.astar_traffic(start, end)

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000

    print("Shortest distance: " + str(finalDistance))

    path_data = helper.getResponseLeafLet(pathDict, end)

    # 5. Return JSON Object
    return jsonify({
        "path": path_data,
        "time": round(elapsed_time, 2), # Round to 2 decimal places
        "distance": round(finalDistance, 2),
        "visited": 0
    })

@app.route('/reset_blocked_edges', methods=['POST'])
def reset_blocked_edges():
    try:
        reset_storage()
        # Open file in write mode to clear it

        # Tự động lấy đường dẫn đúng tới thư mục data
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blocked_file = os.path.join(base_dir, 'data', 'blocked_edges.txt')

        # Ghi rỗng file
        #with open('C:\\Users\\Nhi Nhi\\Documents\\Code\\intro AI\\pathfinding-nghia-do-ward\\data\\blocked_edges.txt', 'w', encoding='utf-8') as f:
        with open(blocked_file, 'w', encoding='utf-8') as f:
            f.write('')  

        # Return success response
        return jsonify({
            "success": True,
            "message": f"Đã reset file {storage_path().name}"
        })
    except Exception as e:
        app.logger.error(f"Error resetting blocked edges: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"Lỗi khi reset file: {str(e)}"
        }), 500

@app.route('/block_edges', methods=['POST'])
def block_edges():
    data = request.get_json(silent=True) or {}
    edges = data.get('edges')
    reason = data.get('reason', 'traffic')

    if reason not in {'flood', 'traffic'}:
        return jsonify({"success": False, "message": "Reason must be 'flood' or 'traffic'"}), 400

    if not isinstance(edges, list) or not edges:
        return jsonify({"success": False, "message": "Edges payload is missing"}), 400

    normalized = []
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            continue
        source, target = str(edge[0]), str(edge[1])
        if source and target:
            normalized.append((source, target))

    if not normalized:
        return jsonify({"success": False, "message": "No valid edges found"}), 400

    try:
        append_path(normalized, reason)
        return jsonify({"success": True, "message": f"Added {len(normalized)} edges", "count": len(normalized)})
    except Exception as e:
        app.logger.error(f"Error blocking edges: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0')
