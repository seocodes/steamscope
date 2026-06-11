import os

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
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
        collection.create_index("idempotency_key", unique=True, sparse=True)

        operations = [
            UpdateOne(
                {"idempotency_key": record["idempotency_key"]},  # Filter by idempotency key
                {"$setOnInsert": record},  # Only sets idempotency key on insert, not on update
                upsert=True)  # Insert if not exists - upsert = update + insert (depends)
            for record in records
        ]
        
        result = collection.bulk_write(operations, ordered=False)
        return result.upserted_count
    finally:
        client.close()

def read_deals():
    client, collection = get_deals_collection()
    try:
        return list(collection.find())
    finally:
        client.close()

def list_games_titles():
    client, collection = get_deals_collection()
    try:
        return list(collection.distinct("title"))
    finally:
        client.close()

def query_deals_by_title(title):
    client, collection = get_deals_collection()
    try:
        return list(collection.find({"title": title}).sort("scraped_at", -1))
    finally:
        client.close()

if __name__ == "__main__":
    try:
        ping_mongodb()
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as exc:
        raise SystemExit(f"MongoDB connection failed: {exc}") from exc
