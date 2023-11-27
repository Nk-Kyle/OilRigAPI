from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid

assignment = Blueprint("assignment", __name__)


@assignment.route("/", methods=["POST", "GET", "PUT", "DELETE"])
def assignment_view():
    if request.method == "POST":
        assignment_id = request.json.get("assignment_id", "")
        level_id = request.json.get("level_id", "")
        level_name = request.json.get("level_name", "")
        location_id = request.json.get("location_id", "")
        location_name = request.json.get("location_name", "")
        pdf_link = request.json.get("pdf_link", "")
        creator = request.json.get("creator", "")
        division = request.json.get("division", "")
        work_type = request.json.get("work_type", "")
        priority = request.json.get("priority", 0)
        description = request.json.get("description", "")

        try:
            res = db.assignments.insert_one(
                {
                    "_id": assignment_id,
                    "division": division,
                    "work_type": work_type,
                    "level_id": level_id,
                    "level_name": level_name,
                    "location_id": location_id,
                    "location_name": location_name,
                    "pdf_link": pdf_link,
                    "creator": creator,
                    "description": description,
                    "status": "TO DO",
                    "progress": 0,
                    "priority": int(priority),
                    "logs": [],
                }
            )
        except errors.DuplicateKeyError:
            return {
                "status": 409,
                "message": "An assignment with this code already exists.",
            }, 409

        return {"status": 201}, 201

    elif request.method == "GET":
        res = db.assignments.find({}).sort([("code", 1)])
        data = list(res)

        for assignment in data:
            assignment["id"] = str(assignment["_id"])
            del assignment["_id"]

        return {
            "status": 200,
            "data": data,
        }, 200


@assignment.route("/<assignment_id>", methods=["GET", "PUT", "DELETE"])
def single_assignment(assignment_id):
    if request.method == "GET":
        res = db.assignments.find_one({"_id": assignment_id})
        if res is None:
            return {"status": 404}, 404

        res["id"] = str(res["_id"])
        del res["_id"]

        return {
            "status": 200,
            "data": res,
        }, 200

    elif request.method == "DELETE":
        res = db.assignments.delete_one({"_id": assignment_id})

        if res.deleted_count == 0:
            return {"status": 404}, 404

        return {"status": 200}, 200
