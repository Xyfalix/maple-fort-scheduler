from pymongo import MongoClient
from decouple import config

MONGO_URI = config('DATABASE_URL')
DATABASE_NAME = config('DATABASE_NAME')

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

class BFList:
    def __init__(self, name):
        self.name = name
        self.topToMid = []
        self.topToBtm = []
        self.midToTop = []
        self.midToBtm = []
        self.btmToMid = []
        self.btmToTop = []
        self.standbys = []

    def save_to_db(self):
        # Save the BFList instance to the database
        db.bf_lists.insert_one(self.__dict__)

    # Additional methods as needed
