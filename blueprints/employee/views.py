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
                "is_logged_in": res["is_logged_in"],
                "assigned_tasks": res["assigned_tasks"],
                "task_details": res.get("task_details", []),
            }
            return {"status": 200, "data": res}, 200
        else:
            return {"status": 404, "message": "User not found."}, 404


@employee.route("/login", methods=["POST"])
def employee_login():
    if request.method == "POST":
        id = request.json.get("id", "")
        password = request.json.get("password", "")
        res = db.employees.find_one({"_id": id, "password": password})
        if res:
            # Check if user is already logged in
            if res["is_logged_in"]:
                return {"status": 409, "message": "User already logged in."}, 409

            # Get assignments TO DO for the user
            tasks = (
                db.assignments.find(
                    {
                        "status": "TO DO",
                        "division": res["division"],
                        "work_type": res["work_type"],
                    }
                )
                .sort("priority", 1)
                .limit(3)
            )

            tasks = list(tasks)
            for task in tasks:
                task["id"] = str(task["_id"])

            # Update user's is_logged_in field and set assigned_tasks
            db.employees.update_one(
                {"_id": id},
                {
                    "$set": {
                        "is_logged_in": True,
                        "assigned_tasks": [task["id"] for task in tasks],
                        "task_details": tasks,
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
                {"_id": {"$in": [task["id"] for task in tasks]}},
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
                        }
                    },
                },
            )

            for task in tasks:
                del task["_id"]

            return {"status": 200, "data": tasks}, 200
        else:
            return {"status": 404, "message": "User not found."}, 404


@employee.route("/logout", methods=["POST"])
def employee_logout():
    if request.method == "POST":
        employee_id = request.json.get("id", "")
        password = request.json.get("password", "")
        assignment_statuses = request.json.get("assignment_statuses", [])

        # Check if user exists
        user = db.employees.find_one({"_id": employee_id, "password": password})

        if not user:
            return {"status": 404, "message": "User not found."}, 404

        # Check if user is logged in
        if not user["is_logged_in"]:
            return {"status": 409, "message": "User not logged in."}, 409

        # Find all assigment ids which are assigned to the user noted by user["assigned_tasks"]
        assignments = db.assignments.find({"_id": {"$in": user["assigned_tasks"]}})

        # Check if there is any assignment_status where id is not in assignments
        for assignment_status in assignment_statuses:
            if assignment_status["id"] not in assignments:
                return {"status": 409, "message": "Assignment not found."}, 409

        # Update assignments which are assigned to the user
        for assignment_status in assignment_statuses:
            # Get assignment where _id is assignment_status["id"]
            assignment = next(
                (
                    assignment
                    for assignment in assignments
                    if assignment["_id"] == assignment_status["id"]
                ),
                None,
            )

            # Update assignment status
            db.assignments.update_one(
                {"_id": assignment_status["id"]},
                {
                    "$set": {
                        "status": "DONE"
                        if assignment_status["is_completed"]
                        else "TO DO",
                        "progress": assignment["progress"],
                    },
                    "$push": {
                        "logs": {
                            "id": str(uuid.uuid4()),
                            "timestamp": str(datetime.datetime.now()),
                            "assigned_to": {
                                "id": employee_id,
                                "name": user["name"],
                            },
                            "state": "CHECKED OUT",
                            "progress": assignment["progress"],
                        }
                    },
                },
            )

        # Update user's is_logged_in field and assigned_tasks
        db.employees.update_one(
            {"_id": employee_id},
            {
                "$set": {
                    "is_logged_in": False,
                    "assigned_tasks": [],
                    "task_details": [],
                    "logs": [
                        {
                            "id": str(uuid.uuid4()),
                            "action": "LOGOUT",
                            "timestamp": str(datetime.datetime.now()),
                        }
                    ],
                }
            },
        )

        return {"status": 200, "message": "User logged out successfully."}, 200


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
