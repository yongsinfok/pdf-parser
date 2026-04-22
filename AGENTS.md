# Agent Instructions for MarkItDown Web App

## Project Overview
A web application for uploading PDFs and parsing specific pages using the MarkItDown library.

## Tech Stack
- **Backend**: Python, FastAPI, Uvicorn, MarkItDown, Pydantic
- **Frontend**: React, Vite, Axios, React-Markdown
- **Runtime**: Node.js (>=20.19.0), Python

## Development Setup

### Backend
1. Navigate to `backend/`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python main.py` (runs on `http://localhost:8001`)
   - *Note: You can also use the provided `start_backend.bat`*

### Frontend
1. Navigate to `frontend/`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev` (runs on `http://localhost:5173`)
   - *Note: You can also use the provided `start_frontend.bat`*

## Known Quirks & Gotchas
- **Port Conflicts**: The backend uses port `8001`. If this port is busy, you will need to update the frontend's API calls to point to the new port.
