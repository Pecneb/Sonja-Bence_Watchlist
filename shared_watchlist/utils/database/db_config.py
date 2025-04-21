# db_config.py
from pymongo import MongoClient
import os

# Retrieve the MongoDB URI from environment variables or use a default
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")

# Create a single MongoClient instance
client = MongoClient(MONGODB_URI)

# Access the desired database
db = client["watchlist_db"]
