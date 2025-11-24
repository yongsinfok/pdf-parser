# Docling Web App

A web application to upload PDFs and parse specific pages using Docling.

## Setup

### Backend

1. Navigate to `backend` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python main.py
   ```
   The server runs on `http://localhost:8001`.

### Frontend

1. Navigate to `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```
   The app runs on `http://localhost:5173`.

## Usage

1. Open the frontend URL (`http://localhost:5173`).
2. Upload a PDF.
3. Enter a page range (e.g., "150-160") or a single page ("5").
4. Click "Parse".
5. View the extracted markdown content and download extracted tables as CSV files.

## Troubleshooting

- **Port Conflicts**: The backend runs on port 8001. If this port is in use, modify `backend/main.py` and `frontend/src/App.jsx`.
- **First Run**: The first time you parse a document, the backend will download necessary AI models (approx. 500MB). This may take a few minutes. Check the backend terminal for progress.

