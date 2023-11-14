from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid

assignment = Blueprint("assignment", __name__)


def get_seq(prefix: str):
    res = db.counters.find_one_and_update(
        {"_id": prefix}, {"$inc": {"seq": 1}}, return_document=True
    )
    return res["seq"]


@assignment.route("/", methods=["POST", "GET", "PUT", "DELETE"])
def assignment_view():
    if request.method == "POST":
        level_id = request.json.get("level_id", "")
        level_name = request.json.get("level_name", "")
        location_id = request.json.get("location_id", "")
        location_name = request.json.get("location_name", "")
        pdf_link = request.json.get("pdf_link", "")
        creator = request.json.get("creator", "")
        division = request.json.get("division", "")
        work_type = request.json.get("work_type", "")
        description = request.json.get("description", "")
        prefix = request.json.get("prefix", "")

        try:
            res = db.assignments.insert_one(
                {
                    "_id": prefix + str(get_seq(prefix)),
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

    # elif request.method == "DELETE":
    #     id = request.json.get("id", "")
    #     # Delete level if it exists else return 404
    #     res = db.levels.delete_one({"_id": ObjectId(id)})
    #     if res.deleted_count == 1:
    #         return {"status": 200}, 200
    #     else:
    #         return {"status": 404}, 404
    # elif request.method == "PUT":
    #     id = request.json.get("id", "")
    #     name = request.json.get("name", "")
    #     img_url = request.json.get("img_url", "")
    #     # Update level if it exists else return 404
    #     res = db.levels.update_one(
    #         {"_id": ObjectId(id)},
    #         {"$set": {"name": name, "img_url": img_url}},
    #     )
    #     if res.modified_count == 1:
    #         return {"status": 200}, 200
    #     else:
    #         return {"status": 404}, 404
