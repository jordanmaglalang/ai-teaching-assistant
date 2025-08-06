import React, { useState, useEffect } from 'react';
import Navigation from './Navigation';

interface UploadFormData {
  title: string;
  topic: string;
  description: string;
  file: File | null;
}

export default function TeacherDashboard() {
  const [formData, setFormData] = useState<UploadFormData>({
    title: '',
    topic: '',
    description: '',
    file: null
  });
  
  const [availableTopics, setAvailableTopics] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [customTopic, setCustomTopic] = useState('');
  const [useCustomTopic, setUseCustomTopic] = useState(false);

  // Load available topics on component mount
  useEffect(() => {
    fetchTopics();
  }, []);

  const fetchTopics = async () => {
    try {
      const response = await fetch('http://localhost:8000/topics');
      const data = await response.json();
      if (data.topics) {
        setAvailableTopics(data.topics);
      }
    } catch (error) {
      console.error('Error fetching topics:', error);
      // Fallback topics
      setAvailableTopics(['Data Structures', 'Biology', 'Mathematics', 'Computer Science', 'Physics']);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFormData(prev => ({
      ...prev,
      file
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.file) {
      setUploadMessage('Please provide both title and file');
      return;
    }

    const finalTopic = useCustomTopic ? customTopic : formData.topic;
    if (!finalTopic) {
      setUploadMessage('Please select or enter a topic');
      return;
    }

    setIsUploading(true);
    setUploadMessage('');

    try {
      const uploadData = new FormData();
      uploadData.append('title', formData.title);
      uploadData.append('topic', finalTopic);
      uploadData.append('description', formData.description);
      uploadData.append('file', formData.file);

      const response = await fetch('http://localhost:8000/upload_material', {
        method: 'POST',
        body: uploadData
      });

      const result = await response.json();
      
      if (response.ok) {
        setUploadMessage(`✅ Material uploaded successfully! ID: ${result.material_id}`);
        // Reset form
        setFormData({
          title: '',
          topic: '',
          description: '',
          file: null
        });
        setCustomTopic('');
        setUseCustomTopic(false);
        // Reset file input
        const fileInput = document.getElementById('file') as HTMLInputElement;
        if (fileInput) fileInput.value = '';
      } else {
        setUploadMessage(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      setUploadMessage(`❌ Upload failed: ${error}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <Navigation />
      <div style={{ padding: '20px', maxWidth: '600px', margin: '0 auto' }}>
        <h1>🧑‍🏫 Teacher Dashboard</h1>
      <p>Upload course materials and tag them by topic for AI-powered student assistance</p>
      
      <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="title" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Material Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="e.g., Stacks & Queues Slides"
            required
            style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Topic *
          </label>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
              <input
                type="radio"
                checked={!useCustomTopic}
                onChange={() => setUseCustomTopic(false)}
                style={{ marginRight: '8px' }}
              />
              Select existing topic
            </label>
            <select
              name="topic"
              value={formData.topic}
              onChange={handleInputChange}
              disabled={useCustomTopic}
              style={{ 
                width: '100%', 
                padding: '8px', 
                border: '1px solid #ccc', 
                borderRadius: '4px',
                backgroundColor: useCustomTopic ? '#f5f5f5' : 'white'
              }}
            >
              <option value="">-- Select a topic --</option>
              {availableTopics.map(topic => (
                <option key={topic} value={topic}>{topic}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
              <input
                type="radio"
                checked={useCustomTopic}
                onChange={() => setUseCustomTopic(true)}
                style={{ marginRight: '8px' }}
              />
              Enter custom topic
            </label>
            <input
              type="text"
              value={customTopic}
              onChange={(e) => setCustomTopic(e.target.value)}
              placeholder="e.g., Advanced Algorithms"
              disabled={!useCustomTopic}
              style={{ 
                width: '100%', 
                padding: '8px', 
                border: '1px solid #ccc', 
                borderRadius: '4px',
                backgroundColor: !useCustomTopic ? '#f5f5f5' : 'white'
              }}
            />
          </div>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="description" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Description (Optional)
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Brief description of the material..."
            rows={3}
            style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="file" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Upload File *
          </label>
          <input
            type="file"
            id="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.pptx,.txt"
            required
            style={{ width: '100%', padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
          />
          <small style={{ color: '#666', fontSize: '12px' }}>
            Supported formats: PDF, DOCX, PPTX, TXT
          </small>
        </div>

        <button
          type="submit"
          disabled={isUploading}
          style={{
            backgroundColor: isUploading ? '#ccc' : '#007bff',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '4px',
            cursor: isUploading ? 'not-allowed' : 'pointer',
            fontSize: '16px'
          }}
        >
          {isUploading ? 'Uploading...' : 'Upload Material'}
        </button>
      </form>

      {uploadMessage && (
        <div style={{ 
          marginTop: '20px', 
          padding: '10px', 
          borderRadius: '4px',
          backgroundColor: uploadMessage.includes('✅') ? '#d4edda' : '#f8d7da',
          border: uploadMessage.includes('✅') ? '1px solid #c3e6cb' : '1px solid #f5c6cb',
          color: uploadMessage.includes('✅') ? '#155724' : '#721c24'
        }}>
          {uploadMessage}
        </div>
      )}

      <div style={{ marginTop: '30px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
        <h3>How it works:</h3>
        <ol>
          <li>Upload your course materials (slides, notes, documents)</li>
          <li>Tag them with relevant topics</li>
          <li>Students can search for help within specific topics</li>
          <li>AI provides contextual responses based on your materials</li>
        </ol>
      </div>
      </div>
    </div>
  );
}