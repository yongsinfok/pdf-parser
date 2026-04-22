# Agent Instructions for MarkItDown Web App

## Tech Stack
- **Backend**: Python, FastAPI, Uvicorn, MarkItDown, Pydantic, PyMuPDF
- **Frontend**: React, Vite, Axios, React-Markdown
- **Runtime**: Node.js (>=20.19.0), Python

## Development
- **Run All**: `start_dev.bat`
- **Backend**: `cd backend && pip install -r requirements.txt && python main.py` (Port: 8001)
- **Frontend**: `cd frontend && npm install && npm run dev` (Port: 5173)
- **Linting**: `cd frontend && npm run lint`

## Testing
- **Backend**: `python backend/test_markitdown.py` or `python backend/test_markitdown_with_pdf.py`

## Usage
1. Open `http://localhost:5173`.
2. Upload PDF and enter page range (e.g., `1-5`, `10, 12-15`).

## Known Quirks
- **Port Conflicts**: If backend port changes from 8001, update frontend API base URL.
- **File Storage**: Uploaded files are in `backend/uploads/`.
