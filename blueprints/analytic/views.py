from flask import Blueprint, request
from bson.objectid import ObjectId
from db.database import db
from pymongo import errors
from collections import defaultdict
import uuid

analytic = Blueprint("analytic", __name__)


@analytic.route("/", methods=["GET"])
def analytic_view():
    employees_logged_in = list(db.employees.find({"is_logged_in": True}))
    for user in employees_logged_in:
        user["id"] = str(user["_id"])
        del user["_id"]
        del user["password"]

    assignments = list(db.assignments.find({}))

    work_type_data = defaultdict(lambda: {"sum_progress": 0, "total": 0})
    for assignment in assignments:
        work_type_data[assignment["work_type"]]["sum_progress"] += assignment[
            "progress"
        ]
        work_type_data[assignment["work_type"]]["total"] += 1

    for work_type in work_type_data:
        work_type_data[work_type]["average_progress"] = (
            work_type_data[work_type]["sum_progress"]
            / work_type_data[work_type]["total"]
        )
        work_type_data[work_type]["average_progress"] = round(
            work_type_data[work_type]["average_progress"], 2
        )

    return {
        "status": 200,
        "data": {
            "count_logged_in": len(employees_logged_in),
            "employees": employees_logged_in,
            "work_type_data": work_type_data,
        },
    }
