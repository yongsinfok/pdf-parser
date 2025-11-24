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

1. Open the frontend URL.
2. Upload a PDF.
3. Enter a page range (e.g., "150-160") or a single page ("5").
4. Click "Parse" to see the extracted markdown.
