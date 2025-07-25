from extract_content import get_text_from_pdf, pdf_path
from agent4 import rag_support, semantic_search

prompt="""
1 - A stack can be used in finding matching items in a sequence. For example, when we parse a
mathematical expression, we may use a stack to find matching parentheses. Implement a C++
function that can check on an array of parentheses, and returns true if they all match, otherwise
it returns false. Write appropriate comments in your code to make your code understandable.
The algorithm presented in Code Fragment 5.11 on page 205 (section 5.1.7) of the textbook can
be used as a guideline. Use the STL stack class for stack ADT. To use the template class stack,
you need to include <stack>
. (30 points)
#include <stack>
bool parseParent(char array[], int n){
stack<char> aStack;
//To be implemented
}
The following list shows examples of input array:
Correct: ()(()())(()), the function returns true
Incorrect: (()(()) , the function returns false
The operations are size(), empty(), push(...), pop(), and top(). The reference to the STL stack
class is available at: http://www.cplusplus.com/reference/stack/stack/
"""
#print("Prompt is: ", prompt)
content = semantic_search(prompt)
print("RAG SUPPORT CONTENT:", content)
