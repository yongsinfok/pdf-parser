import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [filePath, setFilePath] = useState(null);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [tables, setTables] = useState([]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8001/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setFilePath(res.data.file_path);
      alert('Upload successful!');
    } catch (error) {
      console.error(error);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleParse = async () => {
    if ((!filePath && !file) || !query) return;

    setLoading(true);
    setResult('');
    setTables([]);

    try {
      let currentFilePath = filePath;

      // Auto-upload if not yet uploaded
      if (!currentFilePath && file) {
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
          const uploadRes = await axios.post('http://localhost:8001/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          currentFilePath = uploadRes.data.file_path;
          setFilePath(currentFilePath);
        } catch (uploadError) {
          console.error(uploadError);
          alert('Upload failed. Please ensure the backend is running.');
          setLoading(false);
          setUploading(false);
          return;
        }
        setUploading(false);
      }

      const res = await axios.post('http://localhost:8001/parse', {
        file_path: currentFilePath,
        page_query: query,
      });

      // Handle new response format
      if (res.data.tables) {
        setTables(res.data.tables);
      }
      setResult(res.data.content);

    } catch (error) {
      console.error(error);
      alert('Parsing failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = (csvContent, tableId) => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `table_${tableId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="container">
      <header>
        <h1>Docling AI Agent</h1>
        <p>Upload a PDF and ask for specific pages.</p>
      </header>

      <div className="card">
        <h2>1. Upload PDF</h2>
        <div className="input-group">
          <input type="file" onChange={handleFileChange} accept=".pdf" className="file-input" />
        </div>
      </div>

      <div className="card">
        <h2>2. Ask Agent</h2>
        <div className="input-group">
          <input
            type="text"
            placeholder="e.g., page 150-160"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="text-input"
          />
          <button onClick={handleParse} disabled={loading || (!filePath && !file)} className="primary-btn">
            {loading ? 'Processing (First time may take longer)...' : 'Parse'}
          </button>
        </div>
      </div>

      {tables.length > 0 && (
        <div className="result-area">
          <h3>Extracted Tables ({tables.length}):</h3>
          <div className="tables-grid">
            {tables.map((table) => (
              <div key={table.id} className="table-card">
                <h4>Table on Page {table.page}</h4>
                <pre className="table-preview">{table.preview}</pre>
                <button onClick={() => downloadCSV(table.csv, table.id)} className="secondary-btn">
                  Download CSV
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {result && (
        <div className="result-area">
          <h3>Markdown Content:</h3>
          <div className="markdown-content">
            <ReactMarkdown>{result}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
