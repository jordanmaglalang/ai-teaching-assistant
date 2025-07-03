from extract_content import get_text_from_pdf, get_doc_content
import re
syllabus_path = r"C:\Users\jorda\Downloads\Syllabus SP25.pdf"
syllabus_text = get_text_from_pdf(syllabus_path)

pattern = re.compile(r"""
    ^\s*                                       # line start + optional whitespace
    (
        # 1) Numbered lists: 1. Topic, 2) Topic, 3 - Topic
        (\d+\s*[\.\)\-]\s*[A-Za-z].+)$ |      
        # 2) Keywords + optional number + punctuation + text
        ((Week|Module|Unit|Chapter|Section|Topic|Lesson|Lecture|Part)\s*\d*\s*[:\-\.]?\s*[A-Za-z].+)$ | 
        # 3) Bullet points: -, *, • 
        ([\-\*\u2022]\s*[A-Za-z].+)$ | 
        # 4) Topics: followed by list separated by commas (capture whole line)
        (Topics?\s*[:\-]\s*.+)$ |
        # 5) Course Outline: capture line
        (Course\s+Outline\s*[:\-]\s*.+)$
    )
""", re.IGNORECASE | re.MULTILINE | re.VERBOSE)

matches = pattern.findall(syllabus_text)

topics = []

for match in matches:
    # Each match is a tuple with multiple groups due to ORs; find the first non-empty
    line = next(group for group in match if group)
    line = line.strip()

    # For "Topics:" or "Course Outline:", split by commas
    if re.match(r"^(Topics?|Course Outline)\s*[:\-]", line, re.I):
        # Extract after colon/dash
        _, after_colon = re.split(r"[:\-]", line, maxsplit=1)
        # Split comma-separated
        parts = [part.strip() for part in after_colon.split(",")]
        topics.extend(parts)
    else:
        # Clean numbering or bullets if present
        cleaned = re.sub(r"^\s*(\d+\s*[\.\)\-]\s*|[\-\*\u2022]\s*)", "", line)
        topics.append(cleaned)

# Remove duplicates while preserving order
seen = set()
unique_topics = []
for t in topics:
    if t.lower() not in seen:
        unique_topics.append(t)
        seen.add(t.lower())
display_topics = '\n\n'.join(unique_topics)
print(display_topics)
