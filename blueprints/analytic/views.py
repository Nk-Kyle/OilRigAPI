from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid

analytic = Blueprint("analytic", __name__)


@analytic.route("/", methods=["GET"])
def analytic_view():
    employees_logged_in = list(db.employees.find({"is_logged_in": True}))
    for user in employees_logged_in:
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["password"]
    return {
        "status": 200,
        "data": {
            "count_logged_in": len(employees_logged_in),
            "employees": employees_logged_in,
        },
    }
