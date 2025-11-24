import os
import shutil
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from docling.document_converter import DocumentConverter

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use /tmp for serverless environments (Vercel)
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ParseRequest(BaseModel):
    file_path: str
    page_query: str

def parse_page_query(query: str):
    """
    Parses strings like "150-160", "page 5", "pages 1, 3, 5".
    Returns a list of page numbers (1-based) or None if parse all.
    """
    if not query:
        return None
        
    query = query.lower()
    pages = set()
    
    # Split by comma to handle multiple parts
    parts = query.split(',')
    
    found_any = False
    
    for part in parts:
        part = part.strip()
        # Check for range "x-y"
        match_range = re.search(r'(\d+)\s*-\s*(\d+)', part)
        if match_range:
            start = int(match_range.group(1))
            end = int(match_range.group(2))
            pages.update(range(start, end + 1))
            found_any = True
            continue
        
        # Check for single number
        match_single = re.search(r'(\d+)', part)
        if match_single:
            pages.add(int(match_single.group(1)))
            found_any = True
            continue
            
    if not found_any:
        return None
        
    return sorted(list(pages))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_path": file_path, "filename": file.filename}

@app.post("/parse")
async def parse_document(request: ParseRequest):
    if not os.path.exists(request.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    pages = parse_page_query(request.page_query)
    
    try:
        converter = DocumentConverter()
        # Note: docling's convert method might not support page selection directly in all versions.
        # If it does, we pass it. If not, we might need to parse all and filter.
        # Based on search, we might try to pass page numbers if possible, 
        # but the standard usage is convert(source).
        # Let's convert first.
        
        # Optimization: Use page_range to limit processing if pages are requested
        # docling's convert method accepts page_range=(start, end)
        
        conversion_kwargs = {}
        if pages:
            # Find min and max to cover the range
            # Note: This will parse everything between min and max.
            # If user asks for 1 and 100, it parses 1-100. 
            # This is still better than parsing 1-1000.
            start_page = min(pages)
            end_page = max(pages)
            conversion_kwargs["page_range"] = (start_page, end_page)
            
        result = converter.convert(request.file_path, **conversion_kwargs)
        doc = result.document
        
        # Filter content by page (in case we parsed a range but only wanted specific pages)
        filtered_content = []
        extracted_tables = []
        
        # Inspect doc.pages structure safely
        doc_pages = getattr(doc, 'pages', None)
        
        if doc_pages:
            # If we requested specific pages, we only want to return those
            target_pages = pages if pages else range(1, len(doc_pages) + 1)
            
            for page_no in target_pages:
                page_item = None
                
                # Handle Dict {page_num: page}
                if isinstance(doc_pages, dict):
                    page_item = doc_pages.get(page_no)
                # Handle List [page, page]
                elif isinstance(doc_pages, list):
                    # Try to find page with matching page_no if it's a list of objects
                     for p in doc_pages:
                         if getattr(p, 'page_no', None) == page_no:
                             page_item = p
                             break
                    # Fallback to index if page_no attribute not found/reliable
                     if page_item is None:
                        idx = page_no - 1
                        if 0 <= idx < len(doc_pages):
                            page_item = doc_pages[idx]

                if page_item:
                    # Extract Markdown
                    if hasattr(page_item, 'export_to_markdown'):
                        filtered_content.append(page_item.export_to_markdown())
                    elif hasattr(page_item, 'text'):
                        filtered_content.append(page_item.text)
                        
                    # Extract Tables
                    # Check if page_item has tables
                    if hasattr(doc, 'tables'):
                        # doc.tables is usually a list of Table objects across the doc.
                        # We need to check which page they belong to.
                        # Table objects usually have a 'prov' or 'page_no' attribute.
                        for table in doc.tables:
                            # Check if table belongs to current page
                            # This depends on docling version. 
                            # Often table.prov[0].page_no or similar.
                            # Let's try to inspect table structure or just export all tables found in the doc 
                            # if we can't filter easily, but filtering is better.
                            
                            # For now, let's iterate all tables in the doc and check their page location
                            # Assuming table.cells[0].prov.page_no or similar exists.
                            # A safer way is to check if the table is referenced in the page's structure.
                            
                            # Simpler approach: docling tables usually have a reference to the page.
                            # Let's try to access table.export_to_dataframe()
                            
                            # We will collect ALL tables that fall within the requested page range.
                            pass

        # Extract tables from the whole document but filter by page range
        if hasattr(doc, 'tables'):
            for i, table in enumerate(doc.tables):
                # Try to determine page number of the table
                table_page = -1
                
                # Try to find page number from provenance
                # provenance might be a list of items, each having page_no
                if hasattr(table, 'prov') and table.prov:
                     # Assuming prov is a list of ProvenanceItem
                     first_prov = table.prov[0]
                     if hasattr(first_prov, 'page_no'):
                         table_page = first_prov.page_no
                elif hasattr(table, 'cells') and table.cells:
                     # Check first cell
                     first_cell = table.cells[0]
                     if hasattr(first_cell, 'prov') and first_cell.prov:
                         if isinstance(first_cell.prov, list) and first_cell.prov:
                             if hasattr(first_cell.prov[0], 'page_no'):
                                 table_page = first_cell.prov[0].page_no
                         elif hasattr(first_cell.prov, 'page_no'):
                             table_page = first_cell.prov.page_no
                
                # If we found a page number and it matches our request (or no specific pages requested)
                if table_page != -1:
                    if not pages or table_page in pages:
                        # Convert to CSV
                        try:
                            df = table.export_to_dataframe()
                            csv_content = df.to_csv(index=False)
                            extracted_tables.append({
                                "id": i,
                                "page": table_page,
                                "csv": csv_content,
                                "preview": df.head().to_markdown(index=False) # Optional preview
                            })
                        except Exception as e:
                            print(f"Error converting table {i} to CSV: {e}")

        response_content = ""
        if filtered_content:
            response_content = "\n\n---\n\n".join(filtered_content)
        else:
            response_content = doc.export_to_markdown()

        return {
            "content": response_content,
            "tables": extracted_tables
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
