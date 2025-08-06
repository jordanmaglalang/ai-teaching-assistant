from extract_content import get_text_from_pdf, pdf_path
from agent4 import rag_support, semantic_search

prompt="""
Let me help you think through this step by step.

When checking if parentheses match correctly, what needs to happen when you encounter each type of parenthesis? 

Think about it this way: If you're reading through the expression from left to right and you see an opening parenthesis '(', what should you do with it? And when you see a closing parenthesis ')', what needs to have happened before for it to be valid?

For example, in the expression "()()", when you reach the first ')', what must have come before it for the parentheses to be balanced?


"""
#print("Prompt is: ", prompt)
content = semantic_search(prompt)
print("RAG SUPPORT CONTENT:", content)
