from src.db.mongodb import connect2db, getDb


class MongoClient:
    def __init__(self, mongo_uri: str, c_type: str):
        self.mongo_uri = mongo_uri
        self.type = c_type

        if self.type == "reader":

            self.mongo_read_client = connect2db(self.mongo_uri)
            print(f"Reader client initialized for DB")
        elif self.type == "writer":
            self.mongo_write_client = connect2db(self.mongo_uri)
            print(f"Writer client initialized for DB")
        else:
            raise Exception(f"No such client type as {self.type} allowed types are reader/writer")


class MongoReader:
    def __init__(self, db_id, collection_id, mongo_client: MongoClient):
        self.db_id = db_id
        self.collection_id = collection_id
        self.read_client = mongo_client

    def read(self, query, returns, limit=5000):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return [p for p in posts.find(query, returns).limit(limit)]

    def read_one(self, query, returns):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return posts.find_one(query, returns)

    def read_sorted_n(self, query, returns, topn, sort_by="_id"):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return [p for p in posts.find(query, returns).sort(sort_by, -1).limit(topn)]

    def read_skipped_sorted_n(self, query, returns, topn, sort_by="_id", skip=0):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return [p for p in posts.find(query, returns).sort(sort_by, -1).limit(topn).skip(skip)]

    def read_skipped_sorted_n_agg(self, q, returns, topn, skip=0):
        pipeline = [
            {
                '$match': q  # Filter documents based on the conditions
            },
            {
                '$addFields': {
                    'liked_users_length': {
                        '$size': {
                            '$ifNull': ['$liked_users', []]  # Use an empty array if 'liked_users' is missing or null
                        }
                    }
                }
            },
            {
                '$sort': {'liked_users_length': -1}
            },
            {
                '$skip': skip
            },
            {
                '$limit': topn
            },
            {
                '$project': returns
            }
        ]

        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return list(posts.aggregate(pipeline))

    def distinct(self, field):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return posts.distinct(field)

    def count(self):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return posts.count_documents({})

    def count_query(self, query):
        _dbw = getDb(self.read_client.mongo_read_client, self.db_id)
        posts = _dbw[self.collection_id]
        return len([p for p in posts.find(query, {"_id": 0})])


class MongoWriter:
    def __init__(self, db_id, collection_id, mongo_client: MongoClient):
        self.db_id = db_id
        self.collection_id = collection_id
        self.write_client = mongo_client

    def write(self, document, update, upsert=True):
        """
        :param upsert:
        :param document:  Document (a python object) to be written
        :param update:  If given doc exists, update these values
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$set': update}, upsert=upsert)

    def unset(self, document, update):
        """
        :param document:  Document (a python object) to be written
        :param update:  If given doc exists, update these values
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$unset': update})

    def update_many(self, document, update, upsert):
        """
        :param document:  Document (a python object) to be written
        :param update:  If given doc exists, update these values
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_many(document, {'$set': update}, upsert=upsert)

    def push(self, document, update):
        """
        :param document:  Document (a python object) to be written
        :param update:  If given doc exists, update these values
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$push': update}, upsert=True)

    def pull(self, document, update):
        """
        :param document:  Remove element from array
        :param update: Removed element
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$pull': update}, upsert=True)

    def overwrite(self, document, update):
        """
        :param document:  Document (a python object) to be written
        :param update:  If given doc exists, update these values
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$set': update}, upsert=False)

    def add_to_set(self, document, update, upsert=True):
        """
        :param upsert:
        :param document:  Document (a python object) to be written
        :param update:  If given doc exists, update these values
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$addToSet': update}, upsert=upsert)

    def remove(self, document):
        """
        :param document:  Document (a python object) to be remove
        :return:
        """
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.delete_one(document)

    def increment(self, document, value):
        _dbw = getDb(self.write_client.mongo_write_client, self.db_id)
        posts_w = _dbw[self.collection_id]
        posts_w.update_one(document, {'$inc': value}, upsert=True)


class ReaderWriter:
    def __init__(self, reader: MongoReader, writer: MongoWriter, name: str):
        self.reader = reader
        self.writer = writer
        self.name = name
