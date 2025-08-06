import React, { useState, useEffect } from 'react';
import Navigation from './Navigation';

interface SearchResult {
  title: string;
  topic: string;
  description: string;
  content_snippet: string;
  score: number;
}

interface SearchResponse {
  results: SearchResult[];
  topic: string;
  query: string;
  error?: string;
}

export default function AIQueryPage() {
  const [selectedTopic, setSelectedTopic] = useState('');
  const [query, setQuery] = useState('');
  const [availableTopics, setAvailableTopics] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchMessage, setSearchMessage] = useState('');
  const [hasSearched, setHasSearched] = useState(false);

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

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedTopic || !query.trim()) {
      setSearchMessage('Please select a topic and enter a question');
      return;
    }

    setIsSearching(true);
    setSearchMessage('');
    setSearchResults([]);
    setHasSearched(false);

    try {
      const response = await fetch('http://localhost:8000/search_materials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic: selectedTopic,
          query: query.trim(),
          top_k: 5
        })
      });

      const data: SearchResponse = await response.json();
      
      if (response.ok) {
        setSearchResults(data.results);
        setHasSearched(true);
        if (data.results.length === 0) {
          setSearchMessage(`No materials found for "${selectedTopic}" related to your question. Try a different topic or rephrase your question.`);
        } else {
          setSearchMessage(`Found ${data.results.length} relevant materials for your question about ${selectedTopic}`);
        }
      } else {
        setSearchMessage(`❌ Search failed: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      setSearchMessage(`❌ Search failed: ${error}`);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setQuery('');
    setSelectedTopic('');
    setSearchResults([]);
    setSearchMessage('');
    setHasSearched(false);
  };

  return (
    <div>
      <Navigation />
      <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
        <h1>🤖 AI Teaching Assistant</h1>
      <p>Ask questions about specific topics and get answers based on your teacher's materials</p>
      
      <form onSubmit={handleSearch} style={{ marginTop: '20px', marginBottom: '30px' }}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="topic" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Select Topic *
          </label>
          <select
            id="topic"
            value={selectedTopic}
            onChange={(e) => setSelectedTopic(e.target.value)}
            required
            style={{ 
              width: '100%', 
              padding: '10px', 
              border: '1px solid #ccc', 
              borderRadius: '4px',
              fontSize: '16px'
            }}
          >
            <option value="">-- Select a topic --</option>
            {availableTopics.map(topic => (
              <option key={topic} value={topic}>{topic}</option>
            ))}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="query" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Your Question *
          </label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., What is a stack and how does it work?"
            required
            rows={3}
            style={{ 
              width: '100%', 
              padding: '10px', 
              border: '1px solid #ccc', 
              borderRadius: '4px',
              fontSize: '16px',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            type="submit"
            disabled={isSearching}
            style={{
              backgroundColor: isSearching ? '#ccc' : '#28a745',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              cursor: isSearching ? 'not-allowed' : 'pointer',
              fontSize: '16px',
              fontWeight: 'bold'
            }}
          >
            {isSearching ? 'Searching...' : '🔍 Search'}
          </button>
          
          <button
            type="button"
            onClick={clearSearch}
            style={{
              backgroundColor: '#6c757d',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Clear
          </button>
        </div>
      </form>

      {searchMessage && (
        <div style={{ 
          marginBottom: '20px', 
          padding: '12px', 
          borderRadius: '4px',
          backgroundColor: searchMessage.includes('❌') ? '#f8d7da' : '#d1ecf1',
          border: searchMessage.includes('❌') ? '1px solid #f5c6cb' : '1px solid #bee5eb',
          color: searchMessage.includes('❌') ? '#721c24' : '#0c5460'
        }}>
          {searchMessage}
        </div>
      )}

      {hasSearched && searchResults.length > 0 && (
        <div>
          <h2>📚 Relevant Materials</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {searchResults.map((result, index) => (
              <div 
                key={index}
                style={{
                  border: '1px solid #dee2e6',
                  borderRadius: '8px',
                  padding: '16px',
                  backgroundColor: '#f8f9fa'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <h3 style={{ margin: '0 0 5px 0', color: '#495057' }}>{result.title}</h3>
                  <span 
                    style={{
                      backgroundColor: '#007bff',
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '12px',
                      fontWeight: 'bold'
                    }}
                  >
                    {Math.round(result.score * 100)}% match
                  </span>
                </div>
                
                <div style={{ marginBottom: '10px' }}>
                  <span style={{ 
                    backgroundColor: '#e9ecef', 
                    padding: '2px 6px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    color: '#495057'
                  }}>
                    Topic: {result.topic}
                  </span>
                </div>

                {result.description && (
                  <p style={{ margin: '0 0 10px 0', fontStyle: 'italic', color: '#6c757d' }}>
                    {result.description}
                  </p>
                )}

                <div style={{ 
                  backgroundColor: 'white', 
                  padding: '12px', 
                  borderRadius: '4px',
                  border: '1px solid #dee2e6'
                }}>
                  <strong>Relevant content:</strong>
                  <p style={{ margin: '5px 0 0 0', lineHeight: '1.5' }}>
                    {result.content_snippet}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {hasSearched && searchResults.length === 0 && !searchMessage.includes('❌') && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6c757d' }}>
          <h3>No materials found</h3>
          <p>Try selecting a different topic or rephrasing your question.</p>
        </div>
      )}

      <div style={{ marginTop: '40px', padding: '15px', backgroundColor: '#e7f3ff', borderRadius: '4px', border: '1px solid #b8daff' }}>
        <h3 style={{ color: '#004085', margin: '0 0 10px 0' }}>💡 Tips for better results:</h3>
        <ul style={{ margin: '0', paddingLeft: '20px', color: '#004085' }}>
          <li>Choose the most relevant topic for your question</li>
          <li>Be specific in your questions</li>
          <li>Try different keywords if you don't find what you're looking for</li>
          <li>Results are based on materials uploaded by your teachers</li>
        </ul>
      </div>
      </div>
    </div>
  );
}