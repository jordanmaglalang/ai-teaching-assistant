import subprocess
import json
from extract_content import get_text_from_pdf, pdf_path
import fitz  # PyMuPDF
import re
import json
from agent2 import run_question_step
from models import send_message_to_ollama
# -----------------------------
# 1️⃣ Extract text from PDF
def get_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text

# -----------------------------
# 2️⃣ Heuristic regex-based extractor
def extract_questions(text):
    lines = text.split('\n')
    tasks = []
    current_task = None

    # Regex patterns
    main_q = re.compile(r"^\s*\d+\s*[-–.)]?\s")   # 1 - ... or 1) ...
    sub_q = re.compile(r"^\s*[a-zA-Z]\s*[-–.)]?\s")  # a - ... or a) ...

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if main_q.match(line):
            # Save previous
            if current_task:
                tasks.append(current_task)
            # New main
            current_task = {"main_task": line, "subtasks": []}

        elif sub_q.match(line):
            if current_task:
                current_task["subtasks"].append(line)
            else:
                # Orphan subtask
                pass

        else:
            # Probably a continuation line
            if current_task:
                if current_task["subtasks"]:
                    current_task["subtasks"][-1] += " " + line
                else:
                    current_task["main_task"] += " " + line

    if current_task:
        tasks.append(current_task)

    return tasks

# -----------------------------
def ollama_query(prompt: str) -> str:
    # Call ollama CLI with the prompt, capture output
    result = subprocess.run(
        ["ollama", "run", "mistral:instruct"],
        input=prompt.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ollama error: {result.stderr.decode()}")
    return result.stdout.decode()


if __name__ == "__main__":
   

    pdf_file = pdf_path  # Make sure pdf_path is set correctly

    # 1️⃣ Open and read PDF text
    text = get_text_from_pdf(pdf_file)
    tasks = extract_questions(text)
    print(json.dumps(tasks, indent=2, ensure_ascii=False))