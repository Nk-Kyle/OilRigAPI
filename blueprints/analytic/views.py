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

    division_data = defaultdict(lambda: {"sum_progress": 0, "total": 0})
    for assignment in assignments:
        division_data[assignment["division"]]["sum_progress"] += assignment["progress"]
        division_data[assignment["division"]]["total"] += 1

    for division in division_data:
        division_data[division]["average_progress"] = (
            division_data[division]["sum_progress"] / division_data[division]["total"]
        )
        division_data[division]["average_progress"] = round(
            division_data[division]["average_progress"], 2
        )

    print(division_data)

    return {
        "status": 200,
        "data": {
            "count_logged_in": len(employees_logged_in),
            "employees": employees_logged_in,
            "division_data": division_data,
        },
    }
