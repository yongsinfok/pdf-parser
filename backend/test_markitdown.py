from markitdown import MarkItDown

def test_markitdown_conversion():
    md = MarkItDown()
    # This will fail if no file exists, but it's just to check imports and basic usage
    print("MarkItDown imported successfully")
    try:
        # We'll use a non-existent file to test error handling
        result = md.convert("non_existent.pdf")
        print("Conversion result:", result.text_content)
    except Exception as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    test_markitdown_conversion()
