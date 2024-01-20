from pymongo import MongoClient
from decouple import config

MONGO_URI = config('DATABASE_URL')
DATABASE_NAME = config('DATABASE_NAME')

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

class User:
    def __init__(self, username, role="user", acknowledged=""):
        self.username = username
        self.role = role
        self.acknowledged = acknowledged

    def save_to_db(self):
        # Save the User instance to the database
        db.users.insert_one(self.__dict__)

    # Additional methods as needed
