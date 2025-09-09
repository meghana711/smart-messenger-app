# init_mongo.py
from pymongo import MongoClient
from datetime import datetime

# Replace with your actual connection string
MONGO_URI = "mongodb+srv://meghana70132:1234@cluster0.ru8caxy.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URI)
db = client["smart_messenger"]
collection = db["api_sentemail"]

# Optional: test insert
collection.insert_one({
    "sender": "test@example.com",
    "recipient": "to@example.com",
    "subject": "Test",
    "message": "This is a test message.",
    "corrected_message": None,
    "timestamp": datetime.now(),
    "file_path": "/path/to/file.pdf"
})

print("✅ MongoDB collection initialized and test document inserted.")
