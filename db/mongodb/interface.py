import os
from db.mongodb import MongoClient, MongoReader, ReaderWriter, MongoWriter


class MongoEngine:
    def __init__(self):
        self.__mongo_uri = os.environ["MONGODB_URI"]
        self.__user_client_reader = MongoClient(self.__mongo_uri, "reader")
        self.__user_client_writer = MongoClient(self.__mongo_uri, "writer")

        self.__forms = ReaderWriter(
            MongoReader("dria", "form",
                        self.__user_client_reader),
            MongoWriter("dria", "form",
                        self.__user_client_writer), "form")


    def save_form(self, q):
        try:
            return self.__forms.writer.write(q, q), None
        except Exception as e:
            return None, e
