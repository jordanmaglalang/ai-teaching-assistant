from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId

from agent4 import run_question_step  # your LangGraph logic
from db import (
    add_tutor,
    add_assignment,
    tutors_collection,
    assignments_collection,
)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


@app.route("/add_tutor", methods=["POST"])
def add_tutor_route():
    user_id = request.form.get("userId")
    course_name = request.form.get("courseName")
    files = request.files.getlist("files")
    return add_tutor(user_id, course_name, files)


@app.route("/add_assignment", methods=["POST"])
def add_assignment_route():
    tutor_id = request.form.get("tutorId")
    assignment_name = request.form.get("assignmentName")
    files = request.files.getlist("files")
    return add_assignment(tutor_id, assignment_name, files)


@app.route("/tutors", methods=["GET"])
def get_tutors():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    tutors = list(tutors_collection.find({"user_id": ObjectId(user_id)}))
    for tutor in tutors:
        tutor["_id"] = str(tutor["_id"])
        tutor["user_id"] = str(tutor["user_id"])
    return jsonify(tutors)


@app.route("/assignments", methods=["GET"])
def get_assignments():
    tutor_id = request.args.get("tutorId")
    if not tutor_id:
        return jsonify({"error": "Missing tutorId"}), 400

    assignments = list(assignments_collection.find({"tutor_id": ObjectId(tutor_id)}))
    for a in assignments:
        a["_id"] = str(a["_id"])
        a["tutor_id"] = str(a["tutor_id"])
    return jsonify(assignments)
@app.route("/assignments/<assignment_id>", methods=["GET"])
def get_assignment(assignment_id):
    assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    assignment["_id"] = str(assignment["_id"])
    assignment["tutor_id"] = str(assignment["tutor_id"])

    # Important: expose 'assignment_name' as 'name' or 'assignment_name' as is
    return jsonify(assignment)






@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    assignment_id = data.get("assignmentId")
    user_message = data.get("message", "")
    session_state = data.get("state", {})
    index = data.get("index", 0)
    reference = ""
    

    print("MESSAGE IS:", user_message)

    if not assignment_id:
        print("assignment_id is missing")
        return jsonify({"error": "Missing assignmentId"}), 400

    assignment = assignments_collection.find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        print("assignment not found")
        return jsonify({"error": "Assignment not found"}), 404

    questions = assignment.get("questions", [])
    if index >= len(questions):
        print("index is out of range")
        return jsonify({"reply": "✅ All done!", "state": {}, "index": index})

    main_q = questions[index]["main_task"]
    subtasks = questions[index].get("subtasks", []).copy()  # ✅ WORKING COPY
    print("SUBTASKS:", subtasks)

    # Build current subtasks text for display
    current_subtasks = "  ".join(subtasks) if subtasks else ""

    # Create new state if first time or forced new
    if session_state == {} or not session_state:
        is_new_question = False
        print("CREATING NEW SESSION STATE")
        working_subtasks = subtasks.copy()
        follow_up = working_subtasks.pop(0) if working_subtasks else None

        session_state = {
            "primary_task": f"{main_q} {subtasks}",
            "primary_answer": "",
            "current_task": None,
            "follow_up_question": follow_up,
            "follow_up_task": "",
            "correct_answer": False,
            "full_response": "",
            "full_reference": None,
            "subquestions": working_subtasks,  # ✅ separate working copy!
            "attempts": 0,
        }
        result = session_state
        reply = f"{main_q} {current_subtasks}"
    else:
        # Continuing an existing thread
        print("USING EXISTING SESSION STATE")
        if session_state.get("follow_up_question") is None and session_state["subquestions"]:
            session_state["follow_up_question"] = session_state["subquestions"].pop(0)

        result = run_question_step(user_message, session_state)
        reply = result.get("full_response", "")
        reference = result.get("full_reference")

        if result.get("follow_up_question") is None and result.get("subquestions"):
            result["follow_up_question"] = result["subquestions"].pop(0)

    print("REPLY:", reply)

    # Check if user confirmed correct or LLM marked correct
    if user_message.strip().lower() == "yes" or result.get("correct_answer") == True:
        print("✅ Marking as correct and advancing")
        reply = "✅ Correct! " + reply
        index += 1

        if index >= len(questions):
            return jsonify({
                "reply": "✅ All done!",
                "state": {},
                "index": index
            })
        else:
            next_main_q = questions[index]["main_task"]
            next_subtasks = questions[index].get("subtasks", [])
            subtasks_text = " ".join(next_subtasks) if next_subtasks else ""
            reply += f" Next task: {next_main_q} {subtasks_text}"

            # Reset for next
            result = {
                "primary_task": f"{next_main_q} {next_subtasks}",
                "primary_answer": "",
                "current_task": None,
                "follow_up_question": next_subtasks.pop(0) if next_subtasks else "",
                "follow_up_task": "",
                "correct_answer": False,
                "full_response": "",
                "full_reference": None,
                "subquestions": next_subtasks,
                "attempts": 0,
            }

    print("CURRENT STATE:", result)

    return jsonify({
        "reply": reply.strip() + "\n\n\n STATE: :"+ str(result)+ "\n\n\n" ,
        "reference": reference,
        "state": result,
        "index": index,
        
    })


if __name__ == "__main__":
    app.run(port=8000, debug=True)
