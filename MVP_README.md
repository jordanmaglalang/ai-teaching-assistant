# AI Teaching Assistant - Community Educator Platform MVP

## 🎯 Overview
This MVP extends the existing AI tutor system with teacher-side features that allow educators to upload and tag course materials by topic. The AI assistant leverages vector search to provide students with better, contextual responses based on teacher-uploaded materials.

## 🚀 Features Implemented

### ✅ Teacher Upload Portal
- **Route**: `/teacher-dashboard`
- **File Support**: PDF, DOCX, PPTX, TXT
- **Topic Tagging**: Select from existing topics or create custom ones
- **Metadata Storage**: Title, description, teacher ID, timestamp

### ✅ Semantic Search by Topic
- **Route**: `/ai-query`
- **Topic-based Search**: Vector search within specific topic namespaces
- **Contextual Results**: Returns relevant content with source attribution
- **Match Scoring**: Shows relevance percentage for each result

### ✅ Vector Database Integration
- **Pinecone Integration**: Topic-based namespacing for organized content
- **Chunking Strategy**: 100-word chunks with 30-word overlap
- **Embedding Model**: Llama-text-embed-v2 via Pinecone
- **Namespace Sanitization**: Automatic topic name cleanup for valid namespaces

## 🏗️ Architecture

### Backend (Flask)
```
/upload_material    - POST: Upload and process teacher materials
/search_materials   - POST: Search materials by topic and query
/topics            - GET:  Retrieve available topics
```

### Frontend (React/TypeScript)
```
/teacher-dashboard  - Teacher material upload interface
/ai-query          - Student query interface with topic selection
Navigation         - Cross-platform navigation component
```

### Database Schema
```javascript
// MongoDB Collection: teacher_materials
{
  "_id": ObjectId,
  "teacher_id": "test_teacher_01",
  "title": "Stacks & Queues Slides",
  "topic": "Data Structures",
  "description": "Introduction to basic data structures",
  "file_path": "filename.pdf",
  "content": "extracted text content...",
  "timestamp": ISODate
}
```

### Vector Database Structure
```
Pinecone Index: developer-quickstart-py
Namespaces: topic-based (e.g., "data_structures", "biology")
Records: {
  "_id": "material_id-chunk-0",
  "chunk_text": "content chunk...",
  "metadata": {
    "material_id": "...",
    "topic": "...",
    "chunk_index": 0
  }
}
```

## 🛠️ Technical Implementation

### File Processing Pipeline
1. **Upload Validation**: Check file type and size
2. **Text Extraction**: Extract content using appropriate parser
3. **Content Chunking**: Split into searchable chunks
4. **Vector Embedding**: Generate embeddings via Pinecone
5. **Storage**: Save metadata to MongoDB, vectors to Pinecone

### Search Workflow
1. **Topic Selection**: User selects from available topics
2. **Query Processing**: Clean and validate search query
3. **Vector Search**: Search within topic namespace
4. **Result Ranking**: Return top-k matches with scores
5. **Metadata Enrichment**: Add source material information

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- Pinecone account

### Environment Variables
```bash
# Backend (.env)
MONGO_DB_KEY=your_mongodb_connection_string
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_key (optional)
CLAUDE_API_KEY=your_claude_key (optional)
TOGETHER_API_KEY=your_together_key (optional)
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Testing

### Sample Data
- `sample_data/sample_data_structures.txt` - Data structures content
- `sample_data/sample_biology.txt` - Biology content

### Test Workflow
1. Start backend: `python backend/app.py`
2. Start frontend: `npm run dev` (in frontend directory)
3. Navigate to `http://localhost:5173/teacher-dashboard`
4. Upload sample materials with topics
5. Navigate to `http://localhost:5173/ai-query`
6. Test search functionality

### Example Test Queries
- **Topic**: Data Structures, **Query**: "What is a stack?"
- **Topic**: Biology, **Query**: "What does the mitochondria do?"

## 🔧 Key Components

### Backend Files
- `app.py` - Main Flask application with new endpoints
- `db.py` - Database operations including teacher materials
- `vector_db.py` - Pinecone integration with topic namespacing
- `extract_content.py` - File parsing utilities

### Frontend Files
- `TeacherDashboard.tsx` - Teacher upload interface
- `AIQueryPage.tsx` - Student search interface
- `Navigation.tsx` - Navigation component
- `App.tsx` - Updated routing

## 🎯 MVP Success Criteria

✅ **Teacher Upload**: Teachers can upload materials tagged by topic  
✅ **Vector Storage**: Files are embedded and stored under topic namespaces  
✅ **Topic Search**: Users can search by topic and get semantic matches  
✅ **System Preservation**: No changes to existing tutor/assignment system  

## 🔄 Integration Strategy

- **Preserves Existing Code**: All original routes and functionality remain intact
- **Additive Implementation**: New features don't interfere with existing systems
- **Shared Infrastructure**: Uses existing MongoDB and adds Pinecone integration
- **Authentication Ready**: Designed for easy integration with existing auth systems

## 🚀 Future Enhancements

- **Dynamic Topic Management**: Allow teachers to create/edit topics
- **Advanced Search**: Multi-topic search, filtering, sorting
- **Analytics Dashboard**: Usage statistics and popular topics
- **Integration with Chat**: Connect search results to existing chat system
- **Role-based Access**: Proper teacher/student authentication
- **Batch Upload**: Multiple file upload with drag-and-drop

## 📝 API Documentation

### Upload Material
```http
POST /upload_material
Content-Type: multipart/form-data

teacherId: string (optional, defaults to "test_teacher_01")
title: string (required)
topic: string (required)
description: string (optional)
file: file (required, .pdf/.docx/.pptx/.txt)
```

### Search Materials
```http
POST /search_materials
Content-Type: application/json

{
  "topic": "Data Structures",
  "query": "What is a stack?",
  "top_k": 5
}
```

### Get Topics
```http
GET /topics

Response: {
  "topics": ["Data Structures", "Biology", "Mathematics", ...]
}
```

## 🐛 Known Limitations

- **Mock Topics**: Topic list is currently hardcoded for MVP
- **Basic Auth**: Uses placeholder teacher ID for MVP
- **File Size**: No explicit file size limits implemented
- **Error Handling**: Basic error handling, could be more robust
- **Caching**: No caching implemented for repeated searches

This MVP successfully demonstrates the core functionality of a topic-based AI teaching assistant that can be extended with additional features as needed.