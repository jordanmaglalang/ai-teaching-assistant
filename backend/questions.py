from agent import run_question, model
from extract_content import get_doc_content, get_text_from_pdf, get_text_from_ppt
import re

def get_questions_from_doc(path):
    text_content = get_doc_content(path)
    print(text_content)
    list_questions = f"""
    Please extract all questions from the following text. The questions may be:

- Numbered with integers like 1., 2., 3., etc.
- Have subparts labeled with letters like a., b., c.
- Span multiple lines.
- May or may not end with question marks.

Treat each top-level number (e.g., 1, 2, 3) and its subparts as separate questions.

Output a clean numbered list starting with 1, 2, 3, ..., ignoring the original labels.

Keep the order the questions appear.

Here is the text:

{text_content}
"""

    response = model.invoke(list_questions)
    text = response.content.strip()

    questions = re.split(r'\n?\s*\d+\.\s+', text)
    if questions[0].strip() == '':
        questions = questions[1:]
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q.strip()}")


    return questions



questions=["1. Which of the following is a register used to store the result of arithmetic operations in x86 assembly? A) EIP B) EAX C) ESP D) EFLAGS", "What does the MOV instruction do in x86 assembly? A) Adds two values B) Moves the instruction pointer C) Transfers data from one location to another D) Compares two values"]

#questions = get_questions_from_doc("/Users/jordanmaglalang/Library/CloudStorage/OneDrive-Personal/Documents/CMSC 341 hw test1.docx")
def run_assignment(questions):
    for question in questions:
        print(f"Question: {question}")
        run_question(question)

#/Users/jordanmaglalang/Library/CloudStorage/OneDrive-Personal/Documents/CMSC 341 hw test1.docx