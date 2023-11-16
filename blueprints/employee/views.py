from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid

employee = Blueprint("employee", __name__)


@employee.route("/", methods=["POST", "GET", "DELETE"])
def assignment_view():
    if request.method == "POST":
        id = request.json.get("id", "")
        password = request.json.get("password", "")
        name = request.json.get("name", "")
        division = request.json.get("division", "")
        work_type = request.json.get("work_type", "")
        photo_url = request.json.get("photo_url", "")

        try:
            db.employees.insert_one(
                {
                    "_id": id,
                    "name": name,
                    "password": password,
                    "division": division,
                    "work_type": work_type,
                    "photo_url": photo_url,
                }
            )
            return {"status": 200, "message": "User created successfully."}, 200

        except errors.DuplicateKeyError:
            return {
                "status": 409,
                "message": "A user with this id already exists.",
            }, 409
    elif request.method == "GET":
        res = db.employees.find({})
        data = list(res)

        for employee in data:
            employee["id"] = str(employee["_id"])
            del employee["_id"]
            del employee["password"]

        return {
            "status": 200,
            "data": data,
        }, 200
