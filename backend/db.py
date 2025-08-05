from flask import jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
from vector_db import prepare_vector_index
from extract_content import get_text_from_pdf
from questions import extract_questions
import fitz  # 
client = MongoClient(os.getenv("MONGO_DB_KEY"), tls=True,tlsAllowInvalidCertificates=True)

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
          # store filenames or paths
    }
    
    #tutor_id = result.inserted_id
    tutor_result = tutors_collection.insert_one(tutor)
    tutor_id = str(tutor_result.inserted_id)
    
    for file in resource_content:
        prepare_vector_index(file, tutor_id)
        
        
    return jsonify({"inserted_id": str(tutor_result.inserted_id)})


import fitz  # PyMuPDF

def add_assignment(tutor_id, assignment_name, assignment_content):
    if not tutor_id or not assignment_name:
        return jsonify({"error": "Missing required fields"}), 400

    questions = []
    for pdf_file in assignment_content:
        pdf_bytes = pdf_file.read()

        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            text = ""
            for page in doc:
                text += page.get_text() + "\n"

        questions += extract_questions(text)

    # ✅ Add attempts=0 for each question
    for q in questions:
        q["attempts"] = 0

    file_names = [file.filename for file in assignment_content]

    assignment = {
        "tutor_id": ObjectId(tutor_id),
        "assignment_name": assignment_name,
        "files": file_names,
        "questions": questions
    }
    result = assignments_collection.insert_one(assignment)

    return jsonify({"inserted_id": str(result.inserted_id)})
