from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
import uuid

analytic = Blueprint("analytic", __name__)


@analytic.route("/", methods=["GET"])
def analytic_view():
    count_logged_in = db.employees.count_documents({"is_logged_in": True})
    return {
        "status": 200,
        "data": {
            "count_logged_in": count_logged_in,
        },
    }, 200
