import json
import fitz  # PyMuPDF
import re

from agent4 import run_question_step

# -----------------------------
# 1️⃣ Extract text from PDF
def get_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

# -----------------------------
# 2️⃣ Heuristic extractor
def extract_questions(text):
    lines = text.split('\n')
    tasks = []
    current_task = None

    main_q = re.compile(r"^\s*\d+\s*[-–.)]?\s")   # 1 -
    sub_q = re.compile(r"^\s*[a-zA-Z]\s*[-–.)]?\s")  # a -

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if main_q.match(line):
            if current_task:
                tasks.append(current_task)
            current_task = {"main_task": line, "subtasks": []}

        elif sub_q.match(line):
            if current_task:
                current_task["subtasks"].append(line)

        else:
            if current_task:
                if current_task["subtasks"]:
                    current_task["subtasks"][-1] += " " + line
                else:
                    current_task["main_task"] += " " + line

    if current_task:
        tasks.append(current_task)

    return tasks

# -----------------------------
if __name__ == "__main__":
    pdf_path = r"/Users/jordanmaglalang/Downloads/Unknown-4.pdf"  # Change to your PDF path
    text = get_text_from_pdf(pdf_path)
    results = extract_questions(text)

    print("✅ Extracted:", json.dumps(results, indent=2))

    # Pick the first task to test
    task = results[1] if len(results) > 1 else results[0]

    main_task = task["main_task"]
    subtasks = task["subtasks"]

    print("\n▶️ Main:", main_task)
    print("▶️ Subtasks:", subtasks)

    # Setup initial state for the graph
    state = {
        "primary_task": main_task,
        "primary_answer": None,
        "follow_up_question": None,
        "full_reference": None,
        "subquestions": subtasks.copy(),
        "attempts": 0,
    }

    # First input: main + subtasks if any
    if subtasks:
        first_input = f"{main_task}\n\n{subtasks[0]}"
    else:
        first_input = main_task

    count = 0
    while True:
        if count == 0:
            state = run_question_step(first_input, state)
        else:
            if state["follow_up_question"]:
                # Reuse follow-up
                user_input = input("\n🧩 Your follow-up: ")
                state = run_question_step(user_input, state)
            elif state["subquestions"]:
                # Pick next subtask if any
                next_subtask = state["subquestions"].pop(0)
                print("\n📝 Next subtask:", next_subtask)
                state = run_question_step(next_subtask, state)
            else:
                # Normal student input
                user_input = input("\n✏️ Your answer: ")
                state = run_question_step(user_input, state)

        

      

        count += 1
