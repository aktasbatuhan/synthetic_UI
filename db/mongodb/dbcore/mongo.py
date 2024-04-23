#!/usr/bin/python
# coding:utf8

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def connect2db(mongo_uri):
    _client = None
    _client = MongoClient(mongo_uri, server_api=ServerApi("1"))
    try:
        _client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    return _client


def getDb(client, DB_NAME):
    _db = client[DB_NAME]
    return _db
