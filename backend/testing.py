from models import send_message_to_ollama, send_message_to_claude, send_message_to_mixtral
from agent2 import grade_answer
from agent2 import run_question_step
def test_question_type_prompt():
    # ✅ Define test inputs and expected labels
    test_cases = [
        (
            """1. What is the largest ocean on Earth?
A) Atlantic Ocean
B) Indian Ocean
C) Pacific Ocean
D) Arctic Ocean""",
            "mcq"
        ),
        (
            """2) Which gas do plants absorb from the atmosphere?
a) Oxygen
b) Hydrogen
c) Nitrogen
d) Carbon Dioxide""",
            "mcq"
        ),
        (
            "Explain the impact of global warming on Arctic ice caps.",
            "frq"
        ),
        (
            "Describe how photosynthesis works in your own words.",
            "frq"
        ),
        (
            """6. Describe the structure of DNA.
a) What is the double helix?
b) What are nucleotides made of?
c) Explain base pairing.""",
            "frq"
        ),
    ]

    passed = 0

    for i, (question_input, expected) in enumerate(test_cases, start=1):
        prompt = f"""
You are an AI assistant helping classify student questions.

Your task is to determine whether the following question is:

- A multiple-choice question (MCQ), which includes answer options like A, B, C, D
- A free response question (FRQ), which does not include any answer choices

Only respond with one of the following labels:

- "MCQ"
- "FRQ"

Question:
\"\"\"{question_input}\"\"\"
""".strip()

        print(f"\n--- TEST CASE {i} ---")
        print("INPUT:\n", question_input)
        response = send_message_to_ollama(prompt).strip().lower().strip('."\'')
        print("OLAMA RESPONSE:", response)
        print("EXPECTED:", expected)

        if response == expected:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")

    total = len(test_cases)
    percentage = (passed / total) * 100
    print(f"\n✅ PASSED: {passed}/{total} ({percentage:.2f}%)")

# Example run


test_cases = [
    ("What is a function?", "question"),
    ("Can you explain recursion?", "question"),
    ("I think it’s photosynthesis.", "attempted_answer"),
    ("The capital of France is Paris.", "attempted_answer"),
    ("Why does water boil at 100 degrees Celsius?", "question"),
    ("My answer is that it’s the mitochondria.", "attempted_answer"),
    ("How do you solve quadratic equations?", "question"),
    ("It’s because of cellular respiration.", "attempted_answer"),
    ("What does DNA stand for?", "question"),
    ("I’m not sure, but it might be photosynthesis.", "attempted_answer"),
    ("Can you tell me what photosynthesis is?", "question"),
    ("Photosynthesis is the process plants use to make food.", "attempted_answer"),
    ("Does the Earth revolve around the Sun?", "question"),
    ("The Earth revolves around the Sun.", "attempted_answer"),
    ("What is the derivative of x^2?", "question"),
]

def run_classification_tests():
    total = len(test_cases)
    passed = 0

    for i, (message, expected) in enumerate(test_cases, 1):
        classification_prompt = f"""
You are an AI assistant classifying student input.

Classify the student's message as one of:
- question
- attempted_answer

Message:
"{message}"

Examples:
"What is a function?" → question
"I think it's photosynthesis." → attempted_answer

Respond with: question or attempted_answer
""".strip()

        try:
            response = send_message_to_mixtral(classification_prompt)
            actual = response.strip().lower().strip('."\'')
        except Exception as e:
            print(f"Test #{i}: ERROR sending request: {e}")
            continue

        if actual == expected:
            passed += 1
            result = "PASS"
        else:
            result = "FAIL"

        print(f"Test #{i}: '{message}'\nExpected: {expected}\nGot: {actual}\nResult: {result}\n")

    percentage = (passed / total) * 100
    print(f"Tests passed: {passed}/{total} ({percentage:.2f}%)")
def test_question_type_prompt2():
    test_cases = [
        # Clearly related follow-ups
        (
            "What is photosynthesis?",
            None,
            "How do plants use sunlight in photosynthesis?",
            "related"
        ),
        (
            "Explain Newton's first law of motion.",
            "Is that about inertia?",
            "Does friction affect it too?",
            "related"
        ),
        (
            "Describe the water cycle.",
            None,
            "What part does evaporation play in the water cycle?",
            "related"
        ),

        # Clearly unrelated switches
        (
            "What is the capital of France?",
            None,
            "Also, who invented the computer?",
            "unrelated"
        ),
        (
            "Explain the structure of an atom.",
            None,
            "Can you tell me about the history of Rome?",
            "unrelated"
        ),

        # Edge cases: partial topic switches
        (
            "What is an ecosystem?",
            None,
            "Can we talk about the solar system instead?",
            "unrelated"
        ),
        (
            "What are renewable energy sources?",
            None,
            "How about nuclear power plants?",
            "related"  # Many may argue nuclear is related as an energy topic.
        ),
        (
            "Describe the process of mitosis.",
            None,
            "Is that similar to meiosis?",
            "related"
        ),
        (
            "Who was the first president of the United States?",
            None,
            "Did he have any pets?",
            "related"
        ),
        (
            "What is climate change?",
            None,
            "What can I do to help stop it?",
            "related"
        ),

        # Ambiguous or conversation filler
        (
            "Explain photosynthesis.",
            None,
            "Wait, can you repeat that?",
            "related"
        ),
        (
            "Explain global warming.",
            None,
            "Cool, and how's your day?",
            "unrelated"
        ),
    ]

    passed = 0

    for i, (primary_task, follow_up, student_message, expected) in enumerate(test_cases, start=1):
        prompt = f"""
You are an AI Teaching Assistant.

Decide if the student's message is:
- related (builds on the same topic)
- unrelated (switches to a different topic)

Primary Question:
"{primary_task}"

Follow Up:
"{follow_up}"

Student Message:
"{student_message}"

Respond with: related or unrelated
""".strip()

        print(f"\n--- TEST CASE {i} ---")
        print("Primary:", primary_task)
        print("Follow Up:", follow_up)
        print("Student Message:", student_message)
        response = send_message_to_mixtral(prompt).strip().lower().strip('.')
        print("OLAMA RESPONSE:", response)
        print("EXPECTED:", expected)

        if response == expected:
            print("✅ PASS")
            passed += 1
        else:
            print("❌ FAIL")

    total = len(test_cases)
    percentage = (passed / total) * 100
    print(f"\n✅ PASSED: {passed}/{total} ({percentage:.2f}%)")


# Example test questions for classification
test_questions = [
    # ✅ MCQ
    ("What is the capital of France?\nA) Berlin\nB) Madrid\nC) Paris\nD) Rome", "mcq"),
    ("Which gas do humans breathe in the most?\na) Oxygen\nb) Carbon dioxide\nc) Nitrogen\nd) Helium", "mcq"),
    # ✅ FRQ
    ("Explain how gravity works in simple terms.", "frq"),
    ("Describe the process of cellular respiration.", "frq"),
    # ✅ Edge: looks MCQ but no options
    ("What is 2+2?", "frq"),
    # ✅ Edge: short question with option-looking word
    ("Pick the correct answer: Who wrote Hamlet?", "mcq"),
]

def generate_answer(current_task):
    question_type_prompt = f"""
You are an AI assistant helping classify student questions.
Your task is to determine whether the following question is:

- A multiple-choice question (MCQ)
- A free response question (FRQ)

Respond only with: "MCQ" or "FRQ"

Question:
\"\"\"{current_task}\"\"\"
""".strip()

    mcq_prompt = f"""
You are a highly knowledgeable teaching assistant.

The student question is **multiple-choice**.
Your task:
1. Identify the correct answer choice (A, B, C, D, etc.)
2. State it clearly.

Question:
\"\"\"{current_task}\"\"\"
""".strip()

    frq_prompt = f"""
You are a highly knowledgeable teaching assistant.

The student question is **free response**.
Your task:
1. Provide a clear, concise answer in your own words.
2. Use simple language.

Question:
\"\"\"{current_task}\"\"\"
""".strip()

    response1 = send_message_to_claude(question_type_prompt)
    q_type = response1.strip().lower()
    print("📌 Classified as:", q_type)

    if q_type == "frq":
        response2 = send_message_to_ollama(frq_prompt)
    else:
        response2 = send_message_to_ollama(mcq_prompt)

    print("✅ Generated Answer:", response2.strip())
    return response2.strip()

# ---------------------------
test_questions = [
    """"
    – Assume the following piece of code is part of a program.
a - Briefly (in one or two sentences) explain what will happen if we try to run the
program and why. (4 points)
string * data[10];
for (int i=0;i<10;i++)
*data[i] = “”;
"""
]

def test_generate_answer():
    question = test_questions[0]
    answer = generate_answer(question)
    print("Answer:", answer)
    return answer

def test_grade_answer_loop():
    primary_task = """
– Assume the following piece of code is part of a program.
a - Briefly (in one or two sentences) explain what will happen if we try to run the
program and why. (4 points)

string * data[10];
for (int i=0;i<10;i++)
*data[i] = “”;
""".strip()
    answer = test_generate_answer()
    # Initial state
    state = {
        "primary_task": primary_task,
        "primary_answer": answer,
        "current_task": "",
        "follow_up_question": None,
        "follow_up_task": "",
        "correct_answer": False,
        "full_response": "",
        "full_reference": "",
        "subquestions": [],
        "attempts": 0,
    }

    print("\n=== INTERACTIVE TEST GRADE ANSWER ===")
    print("\nPRIMARY TASK:\n", primary_task)

    attempt = 0

    while not state["correct_answer"]:
        student_input = input("\n💡 Enter your answer attempt: ").strip()
        if not student_input:
            print("❌ Empty input — exiting.")
            break

        state["current_task"] = student_input
        attempt += 1

        state = grade_answer(state)

        print("\n📝 AI RESPONSE:\n", state["full_response"])
        print("✅ Correct:", state["correct_answer"])
        print("💬 Follow-up:", state["follow_up_question"])

        if state["correct_answer"]:
            print("\n🎉 Correct! It took you", attempt, "attempt(s).")
            break
        else:
            print("\n❌ Not correct yet — try again!\n")

    if not state["correct_answer"]:
        print("\n⚠️ Session ended without a correct answer.")

if __name__ == "__main__":
    print("Running question type classification tests...")
   
