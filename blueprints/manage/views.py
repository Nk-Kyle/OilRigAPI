from flask import Blueprint, request
from bson.json_util import dumps
from bson.objectid import ObjectId
from db.database import db

manage = Blueprint("manage", __name__)


@manage.route("/levels", methods=["POST", "GET", "PATCH", "DELETE"])
def level():
    if request.method == "POST":
        # get data from request
        name = request.json.get("name")
        img_url = request.json.get("img_url")

        res = db.levels.insert_one(
            {
                "name": name,
                "img_url": img_url,
                "tags": [],
            }
        )
        return {"status": 200}
    elif request.method == "GET":
        res = db.levels.find({})
        return {
            "status": 200,
            "data": dumps(list(res)),
        }
    elif request.method == "DELETE":
        id = request.json.get("id")
        # Delete level if it exists else return 404
        res = db.levels.delete_one({"_id": ObjectId(id)})
        if res.deleted_count == 1:
            return {"status": 200}
        else:
            return {"status": 404}
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
            return {"status": 200}
        else:
            return {"status": 404}
