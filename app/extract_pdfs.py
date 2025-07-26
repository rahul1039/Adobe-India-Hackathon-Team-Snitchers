import json
import argparse
import os
import gc
from typing import List, Dict
import fitz  # PyMuPDF

# Define directories relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "input")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

def extract_structure(pdf_path: str) -> Dict:
    """
    Extracts the document structure from a PDF file.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        Dict: A dictionary containing the document title and an outline of headings.
    """
    text_lines = extract_text_lines(pdf_path)
    title = get_document_title(text_lines, pdf_path)
    outline = extract_headings(text_lines)

    # Remove headings that match the title (case insensitive)
    cleaned_outline = [
        h for h in outline if h["text"].strip().lower() != title.strip().lower()
    ]

    return {
        "title": title,
        "outline": cleaned_outline
    }

def extract_text_lines(pdf_path: str) -> List[str]:
    """
    Extracts all text lines from a PDF by reading text page by page.

    Args:
        pdf_path (str): Path to the input PDF file.

    Returns:
        List[str]: A list of all text lines in the PDF.
    """
    lines = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text = page.get_text("text")  # Extract plain text
            if text:
                lines.extend(text.splitlines())
    return lines

def get_document_title(lines: List[str], pdf_path: str) -> str:
    """
    Determines the document title by selecting the first non-empty line.
    If none found, falls back to the PDF filename (without extension).

    Args:
        lines (List[str]): List of text lines extracted from the PDF.
        pdf_path (str): Path to the PDF file.

    Returns:
        str: The document title.
    """
    for line in lines:
        if line.strip():
            return line.strip()
    return os.path.splitext(os.path.basename(pdf_path))[0]

def extract_headings(lines: List[str]) -> List[Dict]:
    """
    Extracts headings from text lines based on simple heuristics:
    - Uppercase lines are treated as H1.
    - Title-case lines as H2.
    - Others as H3.

    Each heading is assigned a page number approximated by dividing
    line index by 50 (assuming roughly 50 lines per page).

    Args:
        lines (List[str]): List of text lines.

    Returns:
        List[Dict]: List of heading dictionaries with keys 'level', 'text', and 'page'.
    """
    headings = []
    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Consider only lines shorter than 100 characters as headings
        if len(line_stripped) < 100:
            if line_stripped.isupper():
                level = "H1"
            elif line_stripped.istitle():
                level = "H2"
            else:
                level = "H3"

            headings.append({
                "level": level,
                "text": line_stripped,
                "page": idx // 50
            })

    return headings

def save_to_json(data: Dict, output_path: str):
    """
    Saves the extracted data to a JSON file.

    Args:
        data (Dict): Data to save.
        output_path (str): Path to the output JSON file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """
    Main function to process PDFs in the input directory,
    extract their structure, and save the results as JSON files
    in the output directory.
    """
    parser = argparse.ArgumentParser(description='Extract PDF structure using PyMuPDF')
    args = parser.parse_args()

    try:
        # Create input/output directories if they do not exist
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        # List all PDF files in the input directory
        pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print("No PDF files found in input directory.", flush=True)
            exit(1)

        # Process each PDF file
        for pdf_file in pdf_files:
            input_pdf = os.path.join(INPUT_DIR, pdf_file)
            output_filename = os.path.splitext(pdf_file)[0] + ".json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            print(f"Processing: {input_pdf}", flush=True)

            # Extract structure and save to JSON
            result = extract_structure(input_pdf)
            save_to_json(result, output_path)

            # Clean up
            del result
            gc.collect()
            print(f"✅ Saved to: {output_path}", flush=True)

    except Exception:
        import traceback
        traceback.print_exc()
        exit(1)

# Entry point check
if __name__ == "__main__":
    main()
