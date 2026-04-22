import os
import shutil
import re
import io
import csv
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from markitdown import MarkItDown
import fitz  # PyMuPDF
from fastapi.responses import Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ParseRequest(BaseModel):
    file_path: str
    page_query: str

def parse_page_query(query: str):
    if not query:
        return None
    query = query.lower()
    pages = set()
    parts = query.split(',')
    found_any = False
    for part in parts:
        part = part.strip()
        match_range = re.search(r'(\d+)\s*-\s*(\d+)', part)
        if match_range:
            start = int(match_range.group(1))
            end = int(match_range.group(2))
            pages.update(range(start, end + 1))
            found_any = True
            continue
        match_single = re.search(r'(\d+)', part)
        if match_single:
            pages.add(int(match_single.group(1)))
            found_any = True
            continue
    if not found_any:
        return None
    return sorted(list(pages))

def get_markdown_preview(data):
    if not data:
        return ""
    
    # Find max columns
    max_cols = max(len(row) for row in data)
    
    md_rows = []
    for i, row in enumerate(data):
        # Pad row with empty strings
        row_padded = [str(item) if item is not None else "" for item in row]
        row_padded += [""] * (max_cols - len(row_padded))
        md_rows.append("| " + " | ".join(row_padded) + " |")
        
        if i == 0:
            # Add separator after header
            separator = "| " + " | ".join(["---"] * max_cols) + " |"
            md_rows.append(separator)
            
    return "\n".join(md_rows)

def process_document(file_path, page_query):
    # Normalize the input path
    file_path = os.path.normpath(file_path)
    
    if not os.path.isabs(file_path):
        # Resolve relative to the directory of main.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.normpath(os.path.join(base_dir, file_path))
        
        if os.path.exists(potential_path):
            file_path = potential_path
        else:
            # If not found, try joining with UPLOAD_DIR using only the filename
            file_path = os.path.normpath(os.path.join(UPLOAD_DIR, os.path.basename(file_path)))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    target_pages = parse_page_query(page_query)
    md_converter = MarkItDown()
    all_content = []
    all_tables = []

    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        
        if target_pages is None:
            pages_to_process = list(range(1, total_pages + 1))
        else:
            pages_to_process = [p for p in target_pages if 1 <= p <= total_pages]

        for page_no in pages_to_process:
            page_idx = page_no - 1
            
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_pdf_path = os.path.join(tmpdir, f"page_{page_idx}.pdf")
                
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
                new_doc.save(temp_pdf_path)
                new_doc.close()

                res = md_converter.convert(temp_pdf_path)
                all_content.append(res.text_content)
                
            page = doc[page_idx]
            tabs = page.find_tables()
            for i, table in enumerate(tabs.tables):
                data = table.extract()
                if not data:
                    continue
                
                csv_output = io.StringIO()
                csv_writer = csv.writer(csv_output)
                for row in data:
                    csv_writer.writerow(row)
                csv_content = csv_output.getvalue()
                
                preview = get_markdown_preview(data)
                
                all_tables.append({
                    "id": i,
                    "page": page_no,
                    "csv": csv_content,
                    "preview": preview
                })

        doc.close()
        final_content = "\n\n".join(all_content).strip()
        return final_content, all_tables

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_path": file_path, "filename": file.filename}

@app.post("/parse")
async def parse_document(request: ParseRequest):
    try:
        content, tables = process_document(request.file_path, request.page_query)
        return {
            "content": content,
            "tables": tables
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
async def download_document(file_path: str, page_query: str = ""):
    try:
        content, _ = process_document(file_path, page_query)
        return Response(content=content, media_type="text/markdown")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
