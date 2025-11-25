from docling.document_converter import DocumentConverter
import pandas as pd
import os

file_path = "uploads/Online Communication Spec.pdf"
# Page 346 (1-based)
page_no = 346

print(f"Processing {file_path} for page {page_no}...")

converter = DocumentConverter()
# We can't easily limit page range in convert() in all versions, 
# but let's try to just convert and then inspect.
# To save time, if the file is huge (76MB), this might take a while.
# docling might allow page_range.
try:
    result = converter.convert(file_path, page_range=(page_no, page_no))
except TypeError:
    print("page_range not supported in convert, converting full doc (might be slow)...")
    result = converter.convert(file_path)

doc = result.document
print(f"Document converted. Pages: {len(doc.pages)}")

# Find tables on page 346
tables_on_page = []
if hasattr(doc, 'tables'):
    for i, table in enumerate(doc.tables):
        # Check provenance
        t_page = -1
        if hasattr(table, 'prov') and table.prov:
             if hasattr(table.prov[0], 'page_no'):
                 t_page = table.prov[0].page_no
        elif hasattr(table, 'cells') and table.cells:
             if hasattr(table.cells[0], 'prov') and table.cells[0].prov:
                 # prov might be list or object
                 if isinstance(table.cells[0].prov, list):
                     t_page = table.cells[0].prov[0].page_no
                 else:
                     t_page = table.cells[0].prov.page_no
        
        if t_page == page_no:
            tables_on_page.append(table)

print(f"Found {len(tables_on_page)} tables on page {page_no}.")

for idx, table in enumerate(tables_on_page):
    print(f"\n--- Table {idx+1} ---")
    
    # Check DataFrame export
    try:
        df = table.export_to_dataframe()
        print(f"DataFrame shape: {df.shape}")
        print("Last 5 rows of DataFrame:")
        print(df.tail())
    except Exception as e:
        print(f"DataFrame export failed: {e}")

    # Check Grid
    if hasattr(table, 'grid') and table.grid:
        print(f"Grid found. Number of rows: {len(table.grid)}")
        print("Last 5 rows of Grid:")
        for row_idx, row in enumerate(table.grid[-5:]):
            row_text = []
            for cell in row:
                if hasattr(cell, 'text'):
                    row_text.append(cell.text)
                else:
                    row_text.append("NO_TEXT")
            print(f"Row {len(table.grid)-5+row_idx}: {row_text}")
    else:
        print("No 'grid' attribute found on table.")
