from flask import json,render_template,jsonify, request, Flask
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient("mongodb+srv://pritam:pritam2000@cluster0.po6mutl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

@app.route("/")
def api_root():
    return render_template("index.html")

@app.route("/getdata", methods = ["GET"])
def get_data():
    db = client["webhook"]
    collection = db["actionsdata"]
    data = collection.find({})
    # Convert PyMongo cursor to list
    data_list = list(data)
    # Convert each ObjectId to string
    for item in data_list:
        item["_id"] = str(item["_id"])
    return jsonify(data_list)

@app.route("/github", methods=["POST"])
def hello_world():
    if request.headers['Content-Type'] == 'application/json':
        my_info = json.dumps(request.json)
        db = client["webhook"]
        collection = db["actionsdata"]
        push = request.json.get("repository", {}).get("pushed_at")
        pull = request.json.get("action")
        merge = request.json.get("repository", {}).get("merges_url")

        if push:
            commit = request.json.get("commits", [{}])[0]
            author_name = commit.get("author", {}).get("name")
            timestamp = commit.get("timestamp")
            branch = request.json.get("repository", {}).get("default_branch")
            id = commit.get("id")
            data = {
                "request_id": id,
                "author": author_name,
                "action": "PUSH",
                "from_branch": branch,
                "to_branch": branch,
                "timestamp": timestamp
            }
            collection.insert_one(data)
        if pull:
            pr = request.json.get("pull_request", {})
            author_name = pr.get("head", {}).get("label")
            timestamp = pr.get("created_at")
            branch = pr.get("base", {}).get("repo", {}).get("default_branch")
            id = pr.get("base", {}).get("repo", {}).get("id")
            data = {
                "request_id": id,
                "author": author_name,
                "action": "PULL_REQUEST",
                "from_branch": branch,
                "to_branch": branch,
                "timestamp": timestamp
            }
            collection.insert_one(data)
        if merge:
            head_commit = request.json.get("head_commit", {})
            author_name = head_commit.get("author", {}).get("name")
            timestamp = head_commit.get("timestamp")
            branch = request.json.get("repository", {}).get("master_branch")
            id = request.json.get("commits", [{}])[0].get("id")
            data = {
                "request_id": id,
                "author": author_name,
                "action": "MERGE",
                "from_branch": branch,
                "to_branch": branch,
                "timestamp": timestamp
            }
            collection.insert_one(data)
        return my_info

if __name__ == "__main__":
    app.run(debug=True)
