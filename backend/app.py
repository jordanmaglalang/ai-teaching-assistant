
from flask import Flask, request, jsonify
from flask_cors import CORS
from agent2 import run_question_step  # import the new step function
#from questions import questions
from db import add_tutor, add_assignment, tutors_collection, assignments_collection, ObjectId # import database functions if needed
app = Flask(__name__)
CORS(app, origins=["http://localhost:5174"])


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_message = data.get("message", "")
    session_state = data.get("state", {})
    current_index = data.get("index", 0)

    # If all questions done
    if current_index >= len(questions):
        return jsonify({"reply": "✅ All questions done! Great job!", "state": {}, "index": current_index})

    # On first turn for this question or after correct answer, send the question itself
    if not session_state or session_state.get("correct_answer", False):
        user_message = questions[current_index]
        session_state = {}

    result = run_question_step(user_message, session_state)

    reply = ""
    if result.get("correct_answer", False):
        reply = "✅ Correct! Moving to next question."
        reference = ""
        current_index += 1
    else:
        reply = result.get("current_response", "Got it. Keep going!")
        reference = result.get("full_reference", "")

    return jsonify({
        "reply": reply,
        "reference": reference,
        "state": result,
        "index": current_index
    })


@app.route("/add_tutor", methods=["POST"])
def add_tutor_route():
    user_id = request.form.get("userId")
    course_name = request.form.get("courseName")
    resource_content = request.files.getlist("files")
    return add_tutor(user_id, course_name, resource_content)

@app.route('/tutors', methods=['GET'])
def get_tutors():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    try:
        object_id = ObjectId(user_id)  # ✅ convert string to ObjectId
    except Exception:
        return jsonify({"error": "Invalid userId format"}), 400

    tutors = list(tutors_collection.find({"user_id": object_id}))

    for tutor in tutors:
        tutor['_id'] = str(tutor['_id'])
        tutor['user_id'] = str(tutor['user_id'])  # convert back for frontend
    return jsonify(tutors)


@app.route("/init_vector_index", methods=["POST"])
def init_vector_index():
    from agent2 import prepare_vector_index
    prepare_vector_index()
    return jsonify({"status": "Indexing done!"})

@app.route("/assignments", methods=["GET"])
def get_assignments():
    tutor_id = request.args.get("tutorId")

    if not tutor_id:
        return jsonify({"error": "Missing tutorId"}), 400

    # Convert tutorId to ObjectId if needed
    try:
        tutor_oid = ObjectId(tutor_id)
    except:
        return jsonify({"error": "Invalid tutorId"}), 400

    # Find all assignments for that tutor
    assignments = list(assignments_collection.find({"tutor_id": tutor_oid}))

    # Convert ObjectIds to strings so they’re JSON serializable
    for assignment in assignments:
        assignment["_id"] = str(assignment["_id"])
        assignment["tutor_id"] = str(assignment["tutor_id"])

    return jsonify(assignments)


@app.route("/add_assignment", methods=["POST"])
def add_assignment_route():
    tutor_id = request.form.get("tutorId")
    assignment_name = request.form.get("assignmentName")
    assignment_content= request.files.getlist("files")

    return add_assignment(tutor_id, assignment_name, assignment_content)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
