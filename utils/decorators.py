import jwt
from functools import wraps
from flask import request, jsonify, current_app
from db.database import db
from bson.objectid import ObjectId
from bson.json_util import dumps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, current_app.config["SECRET_KEY"])
            current_user = db.users.find_one({"_id": ObjectId(data["id"])})
        except:
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)

    return decorated
