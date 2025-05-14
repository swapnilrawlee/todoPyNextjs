import os
from urllib.parse import urlparse
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load DB URI from environment
DB_URI = os.environ.get("DB_URI")
if not DB_URI:
    raise Exception("DB_URI environment variable not set")

url = urlparse(DB_URI)

db = psycopg2.connect(
    dbname=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


@app.route('/', methods=["GET"])
def hello():
    return "Hello, World!"

# Add a new task
@app.route('/todo', methods=['POST'])
def add_task():
    data = request.json
    task = data.get("task")
    user_id = data.get("user_id")

    if not task or not user_id:
        return jsonify({"error": "Task and user_id are required"}), 400

    query = "INSERT INTO todos (task, completed, user_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (task, False, user_id))
    db.commit()

    return jsonify({"message": "Task added", "task": task}), 201

# Get all tasks for a specific user
@app.route('/todos', methods=['GET'])
def get_tasks():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    cursor.execute("SELECT id, task, completed FROM todos WHERE user_id = %s", (user_id,))
    rows = cursor.fetchall()
    return jsonify(rows)

# Delete a task
@app.route('/todo/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    cursor.execute("DELETE FROM todos WHERE id = %s", (task_id,))
    db.commit()
    return jsonify({"message": "Task deleted"}), 200

# Toggle task completion
@app.route('/todo/<int:task_id>', methods=['PUT'])
def toggle_task(task_id):
    cursor.execute("UPDATE todos SET completed = NOT completed WHERE id = %s", (task_id,))
    db.commit()
    return jsonify({"message": "Task toggled"}), 200

if __name__ == '__main__':
    app.run(debug=True)
