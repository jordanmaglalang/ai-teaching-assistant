import { Link } from 'react-router-dom';

export default function Navigation() {
  return (
    <nav style={{
      backgroundColor: '#f8f9fa',
      padding: '10px 20px',
      borderBottom: '1px solid #dee2e6',
      marginBottom: '20px'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#495057' }}>
          AI Teaching Assistant Platform
        </div>
        
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <Link 
            to="/" 
            style={{
              textDecoration: 'none',
              color: '#007bff',
              padding: '5px 10px',
              borderRadius: '4px',
              border: '1px solid #007bff',
              fontSize: '14px'
            }}
          >
            🏠 Home
          </Link>
          
          <Link 
            to="/teacher-dashboard" 
            style={{
              textDecoration: 'none',
              color: '#28a745',
              padding: '5px 10px',
              borderRadius: '4px',
              border: '1px solid #28a745',
              fontSize: '14px'
            }}
          >
            🧑‍🏫 Teacher Dashboard
          </Link>
          
          <Link 
            to="/ai-query" 
            style={{
              textDecoration: 'none',
              color: '#17a2b8',
              padding: '5px 10px',
              borderRadius: '4px',
              border: '1px solid #17a2b8',
              fontSize: '14px'
            }}
          >
            🤖 AI Query
          </Link>
        </div>
      </div>
    </nav>
  );
}