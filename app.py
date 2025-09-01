from flask import Flask
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash
from routes import init_routes
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "fallbacksecret")


db_url = os.getenv("ATLASDB_URL")
if not db_url:
    raise RuntimeError("ATLASDB_URL not found in .env")

print("DB_URL loaded successfully")
app.config["MONGO_URI"] = db_url

# Initialize Mongo
mongo = PyMongo(app)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "SAYAN")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sayan@123")

print("Admin name from env:", ADMIN_USERNAME)

def ensure_admin():
    """Ensure default admin exists in DB"""
    if mongo.db is None:
        raise RuntimeError("MongoDB connection failed. Check ATLASDB_URL.")

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
        raise RuntimeError(f"Failed in ensure_admin: {e}")

ensure_admin()

init_routes(app, mongo)

@app.route("/health")
def health_check():
    try:
        mongo.db.command("ping")
        return {"status": "ok", "db": "connected"}, 200
    except Exception as e:
        return {"status": "error", "db": str(e)}, 500


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
