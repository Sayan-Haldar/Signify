from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from routes import init_routes
import os

app = Flask(__name__)

# Secret key from environment
app.secret_key = os.getenv("SECRET_KEY", "fallbacksecret")

# MongoDB URI
db_url = os.getenv("ATLASDB_URL")
if not db_url:
    raise RuntimeError("ATLASDB_URL not found in environment")

app.config["MONGO_URI"] = db_url
mongo = PyMongo(app)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "SAYAN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sayan@123")

def ensure_admin():
    """Ensure default admin exists in DB"""
    try:
        admin = mongo.db.users.find_one({"username": ADMIN_USERNAME})
        if not admin:
            mongo.db.users.insert_one({
                "username": ADMIN_USERNAME,
                "password": generate_password_hash(ADMIN_PASSWORD),
                "role": "admin"
            })
            print(f"Inserted default admin (username: {ADMIN_USERNAME})")
        else:
            print("Admin already exists, skipping insert.")
    except Exception as e:
        print(f"Warning: Failed to ensure admin: {e}")

# Initialize routes and create admin
init_routes(app, mongo)
ensure_admin()

@app.route("/health")
def health_check():
    try:
        mongo.db.command("ping")
        return {"status": "ok", "db": "connected"}, 200
    except Exception as e:
        return {"status": "error", "db": str(e)}, 500

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    # debug should be False for production
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
