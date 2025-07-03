from flask import Flask, request, jsonify
from flask_cors import CORS
from agent2 import run_question_step  # import the new step function
from questions import questions

app = Flask(__name__)
CORS(app)

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
        current_index += 1
    else:
        reply = result.get("current_response", "Got it. Keep going!")
        reply += result.get("full_reference", "")

    return jsonify({
        "reply": reply,
        "state": result,
        "index": current_index
    })

if __name__ == "__main__":
    app.run(port=8000, debug=True)
