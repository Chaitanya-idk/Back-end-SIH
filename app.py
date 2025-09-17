from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)


MONGO_URI = "mongodb+srv://gitftwsih:actkas@clustersih.snppid6.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["SIH"]  
main_collection = db["main"]  


def serialize(doc):
    return {
        "_id": str(doc["_id"]),
        "serviceNumber": doc.get("serviceNumber"),
        "vehicleNumber": doc.get("vehicleNumber"),
        "source": doc.get("source"),
        "destination": doc.get("destination"),
        "phoneNumber": doc.get("phoneNumber"),
        "latitude": doc.get("latitude"),
        "longitude": doc.get("longitude"),
        "currentStatus": doc.get("currentStatus"),
    }


@app.route("/")
def home():
    return "✅ Flask API is running! Use /api/main"


@app.route("/api/main", methods=["POST"])
def create_entry():
    data = request.json
    result = main_collection.insert_one(data)
    new_doc = main_collection.find_one({"_id": result.inserted_id})
    return jsonify(serialize(new_doc)), 201


@app.route("/api/main", methods=["GET"])
def get_all_entries():
    docs = list(main_collection.find())
    return jsonify([serialize(doc) for doc in docs])


@app.route("/api/main/<id>", methods=["GET"])
def get_entry(id):
    doc = main_collection.find_one({"_id": ObjectId(id)})
    if doc:
        return jsonify(serialize(doc))
    return jsonify({"error": "Not found"}), 404


@app.route("/api/main/<id>", methods=["PUT"])
def update_entry(id):
    data = request.json
    main_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
    updated_doc = main_collection.find_one({"_id": ObjectId(id)})
    return jsonify(serialize(updated_doc))


@app.route("/api/main/<id>", methods=["DELETE"])
def delete_entry(id):
    main_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Deleted successfully"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
