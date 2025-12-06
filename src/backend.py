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

    t0 = time.time()
    pathDict, finalDistance = astar_flood.astar_flood(start, end)
    t1 = time.time()
    time_taken = t1 - t0

    visited_count = len(pathDict) if isinstance(pathDict, dict) else 0

    print("Shortest distance: " + str(finalDistance))
    response = helper.getResponseLeafLet(pathDict, end)

    return jsonify({
        "path": response,
        "time": time_taken,
        "visited": visited_count,
        "distance": finalDistance
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

    t0 = time.time()
    pathDict, finalDistance = astar.astar(start, end)
    t1 = time.time()
    time_taken = t1 - t0

    visited_count = len(pathDict) if isinstance(pathDict, dict) else 0

    print("Shortest distance: " + str(finalDistance))
    response = helper.getResponseLeafLet(pathDict, end)

    return jsonify({
        "path": response,
        "time": time_taken,
        "visited": visited_count,
        "distance": finalDistance
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

    t0 = time.time()
    pathDict, finalDistance = astar_traffic.astar_traffic(start, end)
    t1 = time.time()
    time_taken = t1 - t0

    visited_count = len(pathDict) if isinstance(pathDict, dict) else 0

    print("Shortest distance: " + str(finalDistance))
    response = helper.getResponseLeafLet(pathDict, end)
    return jsonify({
        "path": response,
        "time": time_taken,
        "visited": visited_count,
        "distance": finalDistance
    })

# Keep original reset endpoint
@app.route('/reset_blocked_edges', methods=['POST'])
def reset_blocked_edges():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        blocked_file = os.path.join(base_dir, 'data', 'blocked_edges.txt')

        with open(blocked_file, 'w', encoding='utf-8') as f:
            f.write('')  

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

# Alias that the frontend calls (was named clear_blocked_edges in JS)
@app.route('/clear_blocked_edges', methods=['POST'])
def clear_blocked_edges_alias():
    return reset_blocked_edges()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
