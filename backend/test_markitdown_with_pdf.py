from markitdown import MarkItDown
import os

def test_conversion():
    md = MarkItDown()
    pdf_path = "test_with_table.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found")
        return
    print(f"Converting {pdf_path}...")
    try:
        result = md.convert(pdf_path)
        print("Conversion successful!")
        print("--- Content ---")
        print(result.text_content)
        print("--- End ---")
    except Exception as e:
        print(f"Conversion failed: {e}")

if __name__ == "__main__":
    test_conversion()
