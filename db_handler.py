# In db_handler.py

from pymongo import MongoClient
import os
from dotenv import load_dotenv
# We no longer need datetime here as it's passed from main.py

load_dotenv()

def store_metadata(partner_id, meeting_id, start_time, end_time, gcs_url):
    """
    Connects to MongoDB and stores the detailed recording metadata.
    """
    try:
        mongo_uri = os.environ.get("MONGO_URI")
        db_name = os.environ.get("DATABASE_NAME")
        collection_name = os.environ.get("COLLECTION_NAME")

        if not all([mongo_uri, db_name, collection_name]):
            print("❌ Error: MongoDB environment variables not set.")
            return

        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]

        # --- THIS IS THE NEW METADATA STRUCTURE ---
        metadata = {
            "partner_id": partner_id,
            "meeting_id": meeting_id, # This is now the meet URL
            "start_time_utc": start_time,
            "end_time_utc": end_time,
            "gcs_url": gcs_url,
        }
        
        collection.insert_one(metadata)
        print("📝 Detailed metadata successfully stored in MongoDB.")
    except Exception as e:
        print(f"❌ Failed to store metadata in MongoDB. Error: {e}")