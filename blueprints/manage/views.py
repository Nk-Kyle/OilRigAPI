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
                "tags": [],
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


@manage.route("/levels/<level_id>/tags", methods=["POST", "GET", "PUT", "DELETE"])
def tags(level_id):
    if request.method == "POST":
        tag = request.json.get("tag")
        # Add tag if tag.tag does not exist in tags array
        # In example, if tag.tag is "tag1" and tags array is [{"tag": "tag1", "other": 1}, {"tag": "tag2"}]
        # then tag will not be added
        res = db.levels.update_one(
            {"_id": ObjectId(level_id), "tags.tag": {"$ne": tag["tag"]}},
            {"$push": {"tags": tag}},
        )
        if res.modified_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 403}, 403
    elif request.method == "GET":
        res = db.levels.find_one({"_id": ObjectId(level_id)})
        return {
            "status": 200,
            "data": dumps(res["tags"]),
        }, 200
    elif request.method == "DELETE":
        tag = request.json.get("tag")
        # Delete tag if tag.tag exists in tags array
        # In example, if tag.tag is "tag1" and tags array is [{"tag": "tag1", "other": 1}, {"tag": "tag2"}]
        # then tag after deletion will be [{"tag": "tag2"}]
        res = db.levels.update_one(
            {"_id": ObjectId(level_id)},
            {"$pull": {"tags": {"tag": {"$eq": tag["tag"]}}}},
        )
        if res.modified_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
    elif request.method == "PUT":
        tag = request.json.get("tag")
        # Update tag if tag.tag exists in tags array
        # In example, if tag.tag is "tag1" and tag.tag other is 2 and tags array is [{"tag": "tag1", "other": 1}, {"tag": "tag2"}]
        # then tag after update will be [{"tag": "tag1", "other": 2}, {"tag": "tag2"}]
        res = db.levels.update_one(
            {"_id": ObjectId(level_id), "tags.tag": {"$eq": tag["tag"]}},
            {"$set": {"tags.$": tag}},
        )
        if res.modified_count == 1:
            return {"status": 200}, 200
        else:
            return {"status": 404}, 404
