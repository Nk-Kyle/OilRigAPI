from pymongo import MongoClient
import dotenv
import os

dotenv.load_dotenv(".env")

password = os.getenv("MONGO_PASSWORD")


class Database:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.client = MongoClient(
            f"mongodb+srv://oilrig:{password}@devcluster.n0mj5id.mongodb.net/?retryWrites=true&w=majority"
        )
        self.db = self.client["test"]


db = Database().db
