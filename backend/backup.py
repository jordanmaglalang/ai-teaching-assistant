@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    assignment_id = data.get("assignmentId")
    user_message = data.get("message", "")
    session_state = data.get("state", {})
    index = data.get("index", 0)
    reference = ""
    is_new_question = data.get("isNewQuestion", True)
    print("mESSAGE IS: ", user_message)
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
    print("repeated somehow")
    main_q = questions[index]["main_task"]
    subtasks = questions[index].get("subtasks", [])
    print("SUBTASKS: ", subtasks)
 
    
    
    current_subtasks =""
    if len(subtasks) >0:
        if len(subtasks) == 1:
            current_subtasks = subtasks[0]
        else:
            current_subtasks = "  ".join(subtasks)

    if not session_state or is_new_question:
        print("CREATING NEW SESSION STATE")
        session_state = {
            "primary_task": f"{main_q} {subtasks}",
            "primary_answer": "",
            "current_task": None,
            "follow_up_question": subtasks.pop(0) if len(subtasks)>0 else "",
            "follow_up_task": "",
            "correct_answer": False,
            "full_response": "",
            "full_reference": None,
            "subquestions": subtasks,
            "attempts": 0,
        }
    else:
        if session_state.get("follow_up_question") is None and len(subtasks) > 0:
            session_state["follow_up_question"] = subtasks.pop(0) if len(subtasks) > 0 else ""
    print("SUBTASKS IS: ", subtasks)
   
    if is_new_question == False:
        print("ENTERING HERE")
        
        result = run_question_step(user_message, session_state)
        reply = result.get("full_response")
        if result["follow_up_question"] is None:
            result["follow_up_question"] = subtasks.pop(0) if len(subtasks) > 0 else ""
        reference = result["full_reference"]
    elif is_new_question:
        is_new_question = False       
        result = session_state
        
        print("subtasks in side loop are: ", subtasks)
        reply = main_q + " "+ current_subtasks
    print("reply is: ", reply)



    print("RESULT IS: ", result.get("correct_answer"), "user_message is: ", user_message, " and length of subtasks is: ", len(subtasks)," and is ", subtasks)
    if (user_message.lower() == "yes") or (result.get("correct_answer")==True):
        print("inside condition")
        reply = "✅ Correct!" + " " + reply 
        
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
            if next_subtasks:
                reply += f" Next task: {next_main_q} {next_subtasks}"
                print("REPLY 1 IS : ", reply)
            else:
                reply += f" Next task: {next_main_q}"
                print("REPLY 2 IS : ", reply)
            is_new_question

 
    print("CURRENT STATE IS: ", result  )
    

    
    return jsonify({
        "reply": reply + "\n\n\n",
        "reference": reference,
        "state": result,
        "index": index,''
        'isNewQuestion': is_new_question
    })