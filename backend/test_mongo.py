from pymongo import MongoClient
import os

uri = os.getenv("MONGO_DB_KEY")

client = MongoClient(
    uri,
    tls=True,
    tlsAllowInvalidCertificates=True
)

print(client.list_database_names())