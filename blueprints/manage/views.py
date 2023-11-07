from flask import Blueprint, request
from bson.json_util import dumps
from bson.objectid import ObjectId
from db.database import db

manage = Blueprint("manage", __name__)


@manage.route("/levels", methods=["POST", "GET", "PATCH", "DELETE"])
def level():
    if request.method == "POST":
        name = request.json.get("name")
        img_url = request.json.get("img_url")

        res = db.levels.insert_one(
            {
                "name": name,
                "img_url": img_url,
                "locations": [],
            }
        )
        return {"status": 200}, 200
    elif request.method == "GET":
        res = db.levels.find({})
        return {
            "status": 200,
            "data": dumps(list(res)),
        }, 200
    elif request.method == "DELETE":
        id = request.json.get("id")
        # Delete level if it exists else return 404
        res = db.levels.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
    elif request.method == "PUT":
        id = request.json.get("id")
        name = request.json.get("name")
        img_url = request.json.get("img_url")
        # Update level if it exists else return 404
        res = db.levels.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": name, "img_url": img_url}},
        )
        if res.modified_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404


@manage.route("/levels/<level_id>/locations", methods=["POST", "GET", "PUT", "DELETE"])
def locations(level_id):
    if request.method == "POST":
        location = request.json.get("location")
        # Add location if location.name does not exist in locations array
        # In example, if location.name is "tag1" and locations array is [{"name": "tag1", "other": 1}, {"name": "tag2"}]
        # then location will not be added
        res = db.levels.update_one(
            {"_id": ObjectId(level_id), "locations.name": {"$ne": location["name"]}},
            {"$push": {"locations": location}},
        )
        if res.modified_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 403}, 403
    elif request.method == "GET":
        res = db.levels.find_one({"_id": ObjectId(level_id)})
        return {
            "status": 200,
            "data": dumps(res["locations"]),
        }, 200
    elif request.method == "DELETE":
        location = request.json.get("location")
        # Delete location if location.name exists in locations array
        # In example, if location.name is "tag1" and locations array is [{"name": "tag1", "other": 1}, {"name": "tag2"}]
        # then locations after deletion will be [{"name": "tag2"}]
        res = db.levels.update_one(
            {"_id": ObjectId(level_id)},
            {"$pull": {"locations": {"name": {"$eq": location["name"]}}}},
        )
        if res.modified_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
    elif request.method == "PUT":
        location = request.json.get("location")
        # Update location if location.name exists in locations array
        # In example, if location.name is "tag1" and location.name other is 2 and locations array is [{"name": "tag1", "other": 1}, {"name": "tag2"}]
        # then locations after update will be [{"name": "tag1", "other": 2}, {"name": "tag2"}]
        res = db.levels.update_one(
            {"_id": ObjectId(level_id), "locations.name": {"$eq": location["name"]}},
            {"$set": {"locations.$": location}},
        )
        if res.matched_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
