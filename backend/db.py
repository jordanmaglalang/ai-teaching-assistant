from flask import jsonify
from pymongo import MongoClient
from bson import ObjectId
import os
from vector_db import prepare_vector_index, prepare_topic_vector_index
from extract_content import get_text_from_pdf, extract_text_from_file
from questions import extract_questions
import fitz  # 
client = MongoClient(os.getenv("MONGO_DB_KEY"), tls=True,tlsAllowInvalidCertificates=True)

db = client["ai-tutor"]

users_collection = db["users"]
tutors_collection = db["tutors"]
assignments_collection = db["assignments"]
teacher_materials_collection = db["teacher_materials"]

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

def add_teacher_material(teacher_id, title, topic, description, file):
    """
    Add teacher material with topic tagging for vector search
    """
    if not teacher_id or not title or not topic or not file:
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Extract text content from file
        content = extract_text_from_file(file)
        
        # Create material document
        material = {
            "teacher_id": teacher_id,
            "title": title,
            "topic": topic,
            "description": description or "",
            "file_path": file.filename,
            "content": content,
            "timestamp": ObjectId().generation_time
        }
        
        # Insert into MongoDB
        result = teacher_materials_collection.insert_one(material)
        material_id = str(result.inserted_id)
        
        # Add to vector database with topic namespace
        prepare_topic_vector_index(file, content, topic, material_id)
        
        return jsonify({
            "message": "Material uploaded successfully",
            "material_id": material_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

def search_materials_by_topic(topic, query, top_k=5):
    """
    Search teacher materials by topic using vector search
    """
    try:
        from vector_db import semantic_search_by_topic
        
        # Get vector search results
        vector_results = semantic_search_by_topic(topic, query, top_k)
        
        # Get material metadata for each result
        materials = []
        for result in vector_results:
            material_id = result.get('material_id')
            if material_id:
                material = teacher_materials_collection.find_one({"_id": ObjectId(material_id)})
                if material:
                    materials.append({
                        "title": material["title"],
                        "topic": material["topic"],
                        "description": material["description"],
                        "content_snippet": result["text"],
                        "score": result["score"]
                    })
        
        return materials
        
    except Exception as e:
        print(f"Error searching materials: {str(e)}")
        return []
