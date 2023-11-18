from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid
import datetime

employee = Blueprint("employee", __name__)


@employee.route("/", methods=["POST", "GET"])
def employee_view():
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
                    "is_logged_in": False,
                    "logs": [],
                    "assigned_tasks": [],
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

        return {
            "status": 200,
            "data": data,
        }, 200


@employee.route("/info", methods=["POST"])
def employee_info():
    if request.method == "POST":
        id = request.json.get("id", "")
        res = db.employees.find_one({"_id": id})
        if res:
            res["id"] = str(res["_id"])
            res = {
                "id": res["id"],
                "name": res["name"],
                "division": res["division"],
                "work_type": res["work_type"],
                "photo_url": res["photo_url"],
            }
            return {"status": 200, "data": res}, 200
        else:
            return {"status": 404, "message": "User not found."}, 404


@employee.route("/login", methods=["POST"])
def employee_assign():
    if request.method == "POST":
        id = request.json.get("id", "")
        password = request.json.get("password", "")
        res = db.employees.find_one({"_id": id, "password": password})
        if res:
            # Check if user is already logged in
            if res["is_logged_in"]:
                return {"status": 409, "message": "User already logged in."}, 409

            # Get assignments TO DO for the user
            tasks = db.assignments.find(
                {
                    "status": "TO DO",
                    "division": res["division"],
                    "work_type": res["work_type"],
                }
            ).limit(3)

            tasks = list(tasks)

            # Update user's is_logged_in field and set assigned_tasks
            db.employees.update_one(
                {"_id": id},
                {
                    "$set": {
                        "is_logged_in": True,
                        "assigned_tasks": [task["_id"] for task in tasks],
                        "logs": [
                            {
                                "id": str(uuid.uuid4()),
                                "action": "LOGIN",
                                "timestamp": str(datetime.datetime.now()),
                            }
                        ],
                    }
                },
            )

            # Update assignments which are assigned to the user to IN PROGRESS
            db.assignments.update_many(
                {"_id": {"$in": [task["_id"] for task in tasks]}},
                {
                    "$set": {
                        "status": "IN PROGRESS",
                    },
                    "$push": {
                        "logs": {
                            "id": str(uuid.uuid4()),
                            "timestamp": str(datetime.datetime.now()),
                            "assigned_to": {
                                "id": id,
                                "name": res["name"],
                            },
                            "state": "CHECKED IN",
                            "progress": 0,
                        }
                    },
                },
            )

            for task in tasks:
                task["id"] = str(task["_id"])
                del task["_id"]

            return {"status": 200, "data": tasks}, 200
        else:
            return {"status": 404, "message": "User not found."}, 404


@employee.route("/<id>", methods=["GET", "DELETE"])
def employee_by_id(id):
    if request.method == "GET":
        res = db.employees.find_one({"_id": id})
        if res:
            res["id"] = str(res["_id"])
            del res["_id"]
            return {"status": 200, "data": res}, 200
        else:
            return {"status": 404, "message": "User not found."}, 404
    elif request.method == "DELETE":
        res = db.employees.delete_one({"_id": id})
        if res.deleted_count == 1:
            return {"status": 200, "message": "User deleted successfully."}, 200
        else:
            return {"status": 404, "message": "User not found."}, 404
