from docx import Document
import fitz 
def get_doc_content(content):
    doc = Document(path)
    text_content = ""
    for paragraph in doc.paragraphs:
        text_content += paragraph.text + "\n"  # add each paragraph text with a newline
        print(text_content)
    return text_content
    
def get_text_from_pdf(path):
    doc = fitz.open(path)  # open the PDF file
    text_content = ""
    for page in doc:
        text_content += page.get_text() + "\n"  # extract text from each page
    print(text_content)
    return text_content

doc_path = r"C:\Users\jorda\OneDrive\Documents\testing content ta-ai.docx"
pdf_path = r"C:\Users\jorda\Downloads\cmsc313-assembly-nasm-intro.pdf"
#pdf_path =r"C:\Users\jorda\Downloads\Carbs (1).pdf"
#get_doc_content(doc_path)
get_text_from_pdf(pdf_path)
print("testing")