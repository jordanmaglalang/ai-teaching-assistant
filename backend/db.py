from flask import jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
client = MongoClient(os.getenv("MONGO_DB_KEY"))


db = client["ai-tutor"]

users_collection = db["users"]
tutors_collection = db["tutors"]
assignments_collection = db["assignments"]

def add_tutor(user_id, course_name, resource_content):
    if not user_id or not course_name:
        return jsonify({"error": "Missing userId or courseName"}), 400

    # ✅ For now, just store file names.
    file_names = []
    for file in resource_content:
        file_names.append(file.filename)
        # Optional: file.save(...) to store on disk.

    tutor = {
        "user_id": ObjectId(user_id),
        "course_name": course_name,
        "resources": file_names  # store filenames or paths
    }

    result = tutors_collection.insert_one(tutor)

    return jsonify({"inserted_id": str(result.inserted_id)})


def add_assignment(tutor_id, assignment_name, assignment_content):
    if not tutor_id or not assignment_name:
        return jsonify({"error": "Missing required fields"}), 400

    # Example: store file names or save files
    file_names = []
    for file in assignment_content:
        file_names.append(file.filename)
        # file.save(...) if saving to disk

    # Insert into DB
    assignment = {
        "tutor_id": ObjectId(tutor_id),
        "assignment_name": assignment_name,
        "files": file_names
    }
    result = assignments_collection.insert_one(assignment)

    return jsonify({"inserted_id": str(result.inserted_id)})

 
    return jsonify({"inserted_id": str(result.inserted_id)})
