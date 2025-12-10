from backend import app
from flask import session, send_from_directory, redirect, url_for
import webbrowser
import threading

# Set secret key for sessions
app.secret_key = 'dev'

@app.before_request
def ensure_role():
    if 'role' not in session:
        session['role'] = 'user'

@app.route('/pathfinding-nghia-do-ward/data/map2.html')
def get_role():
    return send_from_directory('data', 'map2.html')

@app.route('/swap_role')
def swap_role():
    session['role'] = 'admin' if session.get('role', 'user') == 'user' else 'user'
    return redirect(url_for('get_role'))

@app.route('/pathfinding-nghia-do-ward/data/map2_flooded')
def get_flooded_map():
    role = session.get('role', 'user')
    if role != 'admin':
        return "Access denied", 403
    return send_from_directory('data', 'map2_flooded.html')

@app.route('/pathfinding-nghia-do-ward/data/map2_traffic')
def get_traffic_map():
    role = session.get('role', 'user')
    if role != 'admin':
        return "Access denied", 403
    return send_from_directory('data', 'map2_traffic.html')

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5500/pathfinding-nghia-do-ward/data/map2.html")

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run('0.0.0.0')