from flask import Blueprint, request, current_app
from bson.json_util import dumps
from bson.objectid import ObjectId
from db.database import db
from hashlib import sha256
from datetime import datetime, timedelta
import dotenv
import os

import jwt

dotenv.load_dotenv(".env")

is_prod = os.getenv("IS_PROD", "true") == "true"

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    # Check if user exists
    res = db.admin.find_one(
        {"username": username, "password": sha256(password.encode()).hexdigest()}
    )
    if res:
        # Generate token
        token = jwt.encode(
            {
                "exp": datetime.now() + timedelta(minutes=120, hours=-7)
                if not is_prod
                else datetime.now() + timedelta(minutes=60),
                "id": str(res.get("_id")),
                "username": res.get("username"),
            },
            current_app.config["SECRET_KEY"],
        )
        return {"status": 200, "token": token}, 200

    else:
        return {"status": 404}, 404


@auth.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")
    # Check if user exists
    res = db.admin.find_one({"username": username})
    if res:
        return {"status": 409}, 409
    else:
        # Add user
        res = db.admin.insert_one(
            {
                "username": username,
                "password": sha256(password.encode()).hexdigest(),
                "display_name": request.json.get("display_name") or username,
            }
        )
        return {"status": 200}, 200
