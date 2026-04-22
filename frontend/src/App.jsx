import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [filePath, setFilePath] = useState(null);
  const [query, setQuery] = useState('');
  const [allPages, setAllPages] = useState(false);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [tables, setTables] = useState([]);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setFileName(selectedFile ? selectedFile.name : '');
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
      setFileName(res.data.filename);
      alert('Upload successful!');
    } catch (error) {
      console.error(error);
      alert('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleParse = async (forceAll = false) => {
    const effectiveAllPages = forceAll ? true : allPages;

    if ((!filePath && !file) || (!query && !effectiveAllPages)) return;

    setLoading(true);
    setResult('');
    setTables([]);
    setAllPages(effectiveAllPages);
    if (effectiveAllPages) setQuery('');

    try {
      let currentFilePath = filePath;

      if (!currentFilePath && file) {
        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        setFileName(file.name);

        try {
          const uploadRes = await axios.post('http://localhost:8001/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          currentFilePath = uploadRes.data.file_path;
          setFilePath(currentFilePath);
          setFileName(uploadRes.data.filename);
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
        page_query: effectiveAllPages ? '' : query,
      });

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

  const downloadMarkdown = async () => {
    setLoading(true);
    try {
      // We need to request the file from the backend.
      // Since the content is already in the state, we could download it from there,
      // but "request for download" implies a new request to the server.
      // This is safer for large files.
      const response = await axios.get(`http://localhost:8001/download?file_path=${encodeURIComponent(filePath)}&page_query=${encodeURIComponent(query)}`, {
        responseType: 'blob',
      });
      
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      
      // Use the original filename, changing .pdf to .md
      const baseName = fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
      link.setAttribute('download', `${baseName}.md`);
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error(error);
      alert('Download failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <header>
        <h1 className="app-title">Docling AI Agent</h1>
        <p>Upload a PDF and ask for specific pages.</p>
      </header>

      <div className="card">
        <h2 className="card-title">1. Upload PDF</h2>
        <div className="input-group">
          <input type="file" onChange={handleFileChange} accept=".pdf" className="file-input" />
        </div>
      </div>

      <div className="card">
        <h2 className="card-title">2. Ask Agent</h2>
        <div className="input-group">
          <div className="input-wrapper">
            <input
              type="text"
              placeholder={allPages ? "All Pages" : "e.g., page 150-160"}
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (allPages) setAllPages(false);
              }}
              className="text-input"
              disabled={allPages}
            />
          </div>
          <div className="button-group">
            <button onClick={() => handleParse(false)} disabled={loading || (!filePath && !file) || (!query && !allPages)} className="primary-btn">
              {loading ? 'Processing...' : 'Parse'}
            </button>
            <button onClick={() => handleParse(true)} disabled={loading || (!filePath && !file)} className="secondary-btn">
              Parse All
            </button>
          </div>
        </div>
      </div>

      {tables.length > 0 && (
        <div className="result-area">
          <h3 className="result-header">Extracted Tables ({tables.length})</h3>
          <div className="tables-grid">
            {tables.map((table) => (
              <div key={table.id} className="table-card">
                <h4 className="table-title">Table on Page {table.page}</h4>
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
          <div className="result-header-container">
            <h3 className="result-title">Markdown Content:</h3>
            <button onClick={downloadMarkdown} disabled={loading} className="secondary-btn">
              {loading ? 'Downloading...' : 'Download .md'}
            </button>          
          </div>
          <div className="markdown-content">
            <ReactMarkdown>{result}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;


