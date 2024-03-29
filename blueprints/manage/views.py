from flask import Blueprint, request
from bson.json_util import dumps
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid

manage = Blueprint("manage", __name__)


@manage.route("/levels", methods=["POST", "GET", "PUT", "DELETE"])
def level():
    if request.method == "POST":
        name = request.json.get("name", "")
        img_url = request.json.get("img_url", "")
        try:
            res = db.levels.insert_one(
                {"name": name, "img_url": img_url, "locations": []}
            )
        except errors.DuplicateKeyError:
            return {
                "status": 409,
                "message": "A level with this name already exists.",
            }, 409

        return {"status": 201}, 201

    elif request.method == "GET":
        res = db.levels.find({}).sort([("name", 1)])
        data = list(res)

        for level in data:
            level["id"] = str(level["_id"])
            del level["_id"]

        return {
            "status": 200,
            "data": data,
        }, 200
    elif request.method == "DELETE":
        id = request.json.get("id", "")
        # Delete level if it exists else return 404
        res = db.levels.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 1:
            # Delete all assignments which are assigned to this location
            db.assignments.delete_many({"location_id": {"$eq": id}})
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
    elif request.method == "PUT":
        id = request.json.get("id", "")
        name = request.json.get("name", "")
        img_url = request.json.get("img_url", "")
        # Update level if it exists else return 404
        res = db.levels.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": name, "img_url": img_url}},
        )
        if res.modified_count == 1:
            db.assignments.update_many(
                {"level_id": {"$eq": id}},
                {"$set": {"level_name": name}},
            )
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404


@manage.route("/levels/<level_id>/locations", methods=["POST", "GET", "PUT", "DELETE"])
def locations(level_id):
    if request.method == "POST":
        location = request.json.get("location")
        # Add location if location.name and location.id does not exist in locations array
        # In example, if location.name is "tag1" and locations array is [{"name": "tag1", "other": 1}, {"name": "tag2"}]
        # then location will not be added
        location["id"] = str(uuid.uuid4()).replace("-", "")
        res = db.levels.update_one(
            {"_id": ObjectId(level_id), "locations.name": {"$ne": location["name"]}},
            {"$push": {"locations": location}},
        )
        if res.modified_count == 1:
            return {"status": 201}, 201
        else:
            return {"status": 409}, 409
    elif request.method == "GET":
        res = db.levels.find_one({"_id": ObjectId(level_id)})
        return {
            "status": 200,
            "data": res["locations"],
        }, 200
    elif request.method == "DELETE":
        location = request.json.get("location")
        # Delete location if location.name exists in locations array
        # In example, if location.name is "tag1" and locations array is [{"name": "tag1", "other": 1}, {"name": "tag2"}]
        # then locations after deletion will be [{"name": "tag2"}]
        res = db.levels.update_one(
            {"_id": ObjectId(level_id)},
            {"$pull": {"locations": {"id": {"$eq": location["id"]}}}},
        )
        if res.modified_count == 1:
            # Delete all assignments which are assigned to this location
            db.assignments.delete_many({"location_id": {"$eq": location["id"]}})

            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
    elif request.method == "PUT":
        location = request.json.get("location")
        # Update location if location.id exists in locations array
        # In example, if location.id is "1" and location.other is 2 and locations array is [{"id" : "1", "name": "tag1", "other": 1}, {"id" : "2","name": "tag2"}]
        # then locations after update will be [{"id" : "1", "name": "tag1", "other": 2}, {"id" : "2","name": "tag2"}]

        # Check if location.name already exists in locations array

        res = db.levels.find_one(
            {"_id": ObjectId(level_id), "locations.name": {"$eq": location["name"]}}
        )
        if res is not None:
            return {"status": 409}, 409

        res = db.levels.update_one(
            {"_id": ObjectId(level_id), "locations.id": {"$eq": location["id"]}},
            {"$set": {"locations.$": location}},
        )
        if res.matched_count == 1:
            db.assignments.update_many(
                {"location_id": {"$eq": location["id"]}},
                {"$set": {"location_name": location["name"]}},
            )
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
