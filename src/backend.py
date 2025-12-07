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
import os
import time

app = Flask(__name__)
CORS(app)

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

    start_time = time.time()

    pathDict, finalDistance = astar.astar(start, end)

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000

    path_data = helper.getResponseLeafLet(pathDict, end)

    print("Shortest distance: " + str(finalDistance))

    return jsonify({
        "path": path_data,
        "time": round(elapsed_time, 2), # Round to 2 decimal places
        "distance": round(finalDistance, 2),
        "visited": 0
    })

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
            "message": "Đã reset file blocked_edges.txt"
        })
    except Exception as e:
        app.logger.error(f"Error resetting blocked edges: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"Lỗi khi reset file: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0')
