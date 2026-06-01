import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()

def get_mongo_uri():
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise ValueError("MONGO_URI is not set. Add it to .env or export it in your shell.")
    return uri


def create_client():
    return MongoClient(get_mongo_uri(), server_api=ServerApi("1")) 

def ping_mongodb():
    client = create_client()
    client.admin.command("ping")
    return client


def get_deals_collection():
    client = create_client()
    collection = client["steamscope"]["deals"]
    return client, collection


def insert_deals(records):
    if not records:
        raise ValueError("No records provided for insertion.")

    client, collection = get_deals_collection()
    try:
        result = collection.insert_many(records, ordered=False)
        return len(result.inserted_ids)
    finally:
        client.close()


if __name__ == "__main__":
    try:
        ping_mongodb()
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as exc:
        raise SystemExit(f"MongoDB connection failed: {exc}")