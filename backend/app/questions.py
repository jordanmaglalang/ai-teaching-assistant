from agent2 import run_question
questions=["1. Which of the following is a register used to store the result of arithmetic operations in x86 assembly? A) EIP B) EAX C) ESP D) EFLAGS", "What does the MOV instruction do in x86 assembly? A) Adds two values B) Moves the instruction pointer C) Transfers data from one location to another D) Compares two values"]

for question in questions:
    print(f"Question: {question}")
    run_question(question)
    