import os
import time
from flask import Blueprint, request, session, jsonify, redirect, render_template, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from helpers import verify_signatures

routes = Blueprint("routes", __name__)
mongo = None  

def init_routes(app, mongo_instance):
    global mongo
    mongo = mongo_instance
    app.register_blueprint(routes)


#  Auth


@routes.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"error": "User already exists!"}), 400

    hashed_pw = generate_password_hash(password)
    mongo.db.users.insert_one({
        "username": username,
        "password": hashed_pw,
        "role": "user"
    })
    return jsonify({"message": "Registration successful"}), 201


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")

    if not username or not password or not role:
        return jsonify({"error": "Username, password and role required"}), 400

    user = mongo.db.users.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    if role != user.get("role"):
        return jsonify({"error": "Invalid role selected"}), 403

    session["user_id"] = str(user["_id"])
    session["username"] = user["username"]
    session["role"] = user["role"]

    if user["role"] == "admin":
        return redirect(url_for("routes.admin_dashboard"))
    return redirect(url_for("routes.home"))


@routes.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    if request.method == "POST":
        return jsonify({"message": "Logged out"}), 200
    return redirect(url_for("routes.login"))


# 🔹 Pages


@routes.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))
    if session.get("role") == "admin":
        return redirect(url_for("routes.admin_dashboard"))
    return render_template("index.html")

@routes.route("/login")
def login_page():
    return render_template("login.html")

@routes.route("/register")
def register_page():
    return render_template("register.html")

@routes.route("/user_dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("routes.login"))
    return render_template("user_dashboard.html")

@routes.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("routes.login"))
    return render_template("admin_dashboard.html")


#  Verification


@routes.route("/verify", methods=["POST"])
def verify():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if "original" not in request.files or "test" not in request.files:
        return jsonify({"error": "Both signature files required"}), 400

    original = request.files["original"]
    test = request.files["test"]

    if not original or not test:
        return jsonify({"error": "Invalid files"}), 400

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    original_path = os.path.join(upload_dir, "original_" + original.filename)
    test_path = os.path.join(upload_dir, "test_" + test.filename)

    original.save(original_path)
    test.save(test_path)

    start_time = time.time()
    confidence, match = verify_signatures(original_path, test_path)
    elapsed_time = round(time.time() - start_time, 3)
    confidence = round(confidence * 100, 2)

    log_entry = {
        "user_id": session["user_id"],
        "username": session["username"],
        "original": original.filename,
        "test": test.filename,
        "confidence": confidence,
        "match": match,
        "time": elapsed_time,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    mongo.db.logs.insert_one(log_entry)

    try:
        os.remove(original_path)
        os.remove(test_path)
    except Exception:
        pass

    return jsonify({
        "confidence": confidence,
        "match": match,
        "time": elapsed_time
    })


#  User Logs


@routes.route("/user/logs", methods=["GET", "DELETE"])
def user_logs():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "GET":
        logs = list(mongo.db.logs.find({"user_id": session["user_id"]}).sort("timestamp", -1))
        for log in logs:
            log["_id"] = str(log["_id"])
        return jsonify({"logs": logs})

    if request.method == "DELETE":
        log_id = request.args.get("id")
        if not log_id:
            return jsonify({"error": "Log id required"}), 400
        mongo.db.logs.delete_one({"_id": ObjectId(log_id), "user_id": session["user_id"]})
        return jsonify({"message": "Log deleted"})


@routes.route("/user/logs/<log_id>", methods=["DELETE"])
def user_logs_delete_by_path(log_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        mongo.db.logs.delete_one({"_id": ObjectId(log_id), "user_id": session["user_id"]})
        return jsonify({"message": "Log deleted"})
    except Exception:
        return jsonify({"error": "Invalid log id"}), 400


#  Admin Logs


@routes.route("/admin/logs", methods=["GET", "DELETE"])
def admin_logs():
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    if request.method == "GET":
        logs = list(mongo.db.logs.find().sort("timestamp", -1))
        for log in logs:
            log["_id"] = str(log["_id"])
        return jsonify({"logs": logs})

    if request.method == "DELETE":
        log_id = request.args.get("id")
        if not log_id:
            return jsonify({"error": "Log id required"}), 400
        mongo.db.logs.delete_one({"_id": ObjectId(log_id)})
        return jsonify({"message": "Log deleted"})


@routes.route("/admin/logs/<log_id>", methods=["DELETE"])
def admin_logs_delete_by_path(log_id):
    if "user_id" not in session or session.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403
    try:
        mongo.db.logs.delete_one({"_id": ObjectId(log_id)})
        return jsonify({"message": "Log deleted"})
    except Exception:
        return jsonify({"error": "Invalid log id"}), 400
