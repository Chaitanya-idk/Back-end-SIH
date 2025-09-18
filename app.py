from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
CORS(app)



client = MongoClient("mongodb+srv://gitftwsih:actkas@clustersih.snppid6.mongodb.net/")
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


# Lookup by serviceNumber or vehicleNumber
@app.route("/api/bus", methods=["GET"])
def get_bus_by_param():
    service_number = request.args.get("serviceNumber", type=int)
    vehicle_number = request.args.get("vehicleNumber")
    query = None
    if service_number is not None:
        query = {"serviceNumber": service_number}
    elif vehicle_number:
        query = {"vehicleNumber": vehicle_number}
    else:
        return jsonify({"error": "Provide serviceNumber or vehicleNumber"}), 400

    doc = main_collection.find_one(query)
    if not doc:
        return jsonify({"error": "Not found"}), 404
    return jsonify(serialize(doc))


# Search by route (source and/or destination)
@app.route("/api/search", methods=["GET"])
def search_by_route():
    source = request.args.get("source")
    destination = request.args.get("destination")
    query = {}
    if source:
        query["source"] = {"$regex": source, "$options": "i"}
    if destination:
        query["destination"] = {"$regex": destination, "$options": "i"}
    docs = list(main_collection.find(query))
    return jsonify([serialize(doc) for doc in docs])


# Update location/status by id/serviceNumber/vehicleNumber
@app.route("/api/location", methods=["PATCH"])
def update_location():
    data = request.json or {}
    lat = data.get("latitude")
    lng = data.get("longitude")
    status = data.get("currentStatus")

    identifier = {}
    if "id" in data:
        try:
            identifier = {"_id": ObjectId(data["id"]) }
        except Exception:
            return jsonify({"error": "Invalid id"}), 400
    elif "serviceNumber" in data:
        identifier = {"serviceNumber": int(data["serviceNumber"]) }
    elif "vehicleNumber" in data:
        identifier = {"vehicleNumber": data["vehicleNumber"] }
    else:
        return jsonify({"error": "Provide id, serviceNumber, or vehicleNumber"}), 400

    update_fields = {}
    if lat is not None:
        update_fields["latitude"] = float(lat)
    if lng is not None:
        update_fields["longitude"] = float(lng)
    if status is not None:
        update_fields["currentStatus"] = status

    if not update_fields:
        return jsonify({"error": "No fields to update"}), 400

    result = main_collection.update_one(identifier, {"$set": update_fields})
    if result.matched_count == 0:
        return jsonify({"error": "Not found"}), 404

    doc = main_collection.find_one(identifier)
    return jsonify(serialize(doc))


# Seed buffer/demo data
@app.route("/api/seed", methods=["POST"]) 
def seed_data():
    sample_docs = [
        {
            "serviceNumber": 1201,
            "vehicleNumber": "TS07-2450",
            "source": "Hyderabad",
            "destination": "Chennai",
            "phoneNumber": "9876543210",
            "latitude": 17.3850,
            "longitude": 78.4867,
            "currentStatus": "On Route"
        },
        {
            "serviceNumber": 1823,
            "vehicleNumber": "AP05-1823",
            "source": "Vijayawada",
            "destination": "Chennai",
            "phoneNumber": "9123456780",
            "latitude": 16.5062,
            "longitude": 80.6480,
            "currentStatus": "Scheduled"
        },
        {
            "serviceNumber": 976,
            "vehicleNumber": "KA03-0976",
            "source": "Bagalkot",
            "destination": "Hyderabad",
            "phoneNumber": "9012345678",
            "latitude": 15.3173,
            "longitude": 75.7139,
            "currentStatus": "On Route"
        }
    ]

    inserted = []
    for doc in sample_docs:
        existing = main_collection.find_one({"serviceNumber": doc["serviceNumber"]})
        if not existing:
            result = main_collection.insert_one(doc)
            inserted.append(str(result.inserted_id))
    return jsonify({"inserted": inserted}), 201

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
