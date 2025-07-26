import json
import pdfplumber
import argparse
from typing import List, Dict
import os
import gc

def extract_structure(pdf_path: str) -> Dict:
    """
    Extracts the document structure including title and section headings from a PDF.

    Parameters:
        pdf_path (str): Path to the PDF file.

    Returns:
        Dict: A dictionary containing the document title and a list of headings.
    """
    title = get_document_title(pdf_path)
    outline = extract_headings(pdf_path)

    # Remove title from headings if duplicated
    cleaned_outline = [
        heading for heading in outline
        if heading["text"].strip().lower() != title.strip().lower()
    ]

    return {
        "title": title,
        "outline": cleaned_outline
    }

def get_document_title(pdf_path: str) -> str:
    """
    Attempts to retrieve the title of the document from metadata or the first page.
    Falls back to the filename if no suitable title is found.

    Parameters:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted title string.
    """
    with pdfplumber.open(pdf_path) as pdf:
        # Check for metadata title
        if pdf.metadata and 'Title' in pdf.metadata:
            return pdf.metadata['Title']

        # Use first line from first page if available
        first_page = pdf.pages[0]
        text = first_page.extract_text(layout=True)
        if text:
            first_line = text.split('\n')[0].strip()
            if first_line:
                return first_line

    # Fallback: use the filename without extension
    return os.path.splitext(os.path.basename(pdf_path))[0]

def extract_headings(pdf_path: str) -> List[Dict]:
    """
    Scans each page of the PDF and identifies likely headings based on font size.

    Parameters:
        pdf_path (str): Path to the PDF file.

    Returns:
        List[Dict]: A list of heading dictionaries with level, text, and page number.
    """
    headings = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=["size", "fontname"])
            if not words:
                continue

            current_line = []
            prev_top = None

            for word in words:
                if prev_top is None:
                    prev_top = word["top"]

                # Detect line change based on vertical position
                if abs(word["top"] - prev_top) > 5:
                    process_line(current_line, headings, page_num)
                    current_line = []

                current_line.append(word)
                prev_top = word["top"]

            # Process any remaining line
            process_line(current_line, headings, page_num)

    return headings

def process_line(words: List, headings: List, page_num: int):
    """
    Evaluates a line of words to determine if it's a heading based on average font size.

    Parameters:
        words (List): A list of word dictionaries from pdfplumber for one line.
        headings (List): The list to append heading information if found.
        page_num (int): The page number (1-based index).
    """
    if not words:
        return

    text = ' '.join(word["text"] for word in words)
    avg_size = sum(word["size"] for word in words) / len(words)

    # Determine heading level based on average font size
    if avg_size > 20:
        level = "H1"
    elif avg_size > 15:
        level = "H2"
    elif avg_size > 12:
        level = "H3"
    else:
        return  # Not considered a heading

    # Exclude overly long lines
    if len(text) < 200:
        headings.append({
            "level": level,
            "text": text,
            "page": page_num - 1  # zero-based index
        })

def save_to_json(data: Dict, output_path: str):
    """
    Saves a dictionary as a UTF-8 encoded JSON file.

    Parameters:
        data (Dict): The data to be serialized and saved.
        output_path (str): The target file path for the JSON output.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def make_directory_readonly(directory: str):
    """
    Makes a directory and its immediate files read-only by setting appropriate permissions.

    Parameters:
        directory (str): Path to the directory to modify.

    Notes:
        This function sets directory permissions to 555 and files inside to 444.
        It does not process subdirectories recursively.
    """
    print(f"[INFO] Attempting to make directory read-only: {directory}")

    # If directory doesn't exist, try correcting the path
    if not os.path.exists(directory):
        corrected = directory.replace("/app", "/Adobe-India-Hackathon-Team-Snitchers/app")
        if os.path.exists(corrected):
            print(f"[WARN] Directory not found at {directory}, corrected to {corrected}")
            directory = corrected
        else:
            print(f"[ERROR] Directory not found at {directory} or {corrected}, skipping read-only operation.")
            return

    try:
        os.chmod(directory, 0o555)  # r-xr-xr-x
        for entry in os.listdir(directory):
            full_path = os.path.join(directory, entry)
            if os.path.isfile(full_path):
                os.chmod(full_path, 0o444)  # r--r--r--
        print(f"[SUCCESS] Directory and files set to read-only: {directory}")
    except Exception as e:
        print(f"[ERROR] Failed to set permissions on {directory}: {e}")


def main():
    """
    Main CLI entry point.
    Parses command-line arguments, initiates structure extraction from a PDF,
    and optionally sets the containing directory to read-only mode.
    """
    parser = argparse.ArgumentParser(
        description='Extract structure from a PDF (supports multilingual text including Japanese).'
    )
    parser.add_argument('input_pdf', help='Path to the input PDF file')
    parser.add_argument('-o', '--output', default='output.json', help='Path to save the output JSON file')
    parser.add_argument('--readonly', action='store_true', help='Set the input directory to read-only before processing')
    args = parser.parse_args()

    input_pdf_path = os.path.abspath(args.input_pdf)
    output_path = os.path.abspath(args.output)
    input_dir = os.path.dirname(input_pdf_path)

    # Helper function to correct paths if not found
    def correct_path(path: str) -> str:
        if not os.path.exists(path):
            corrected = path.replace("/app", "/Adobe-India-Hackathon-Team-Snitchers/app")
            if os.path.exists(corrected):
                print(f"[WARN] Path not found at {path}, corrected to {corrected}")
                return corrected
            else:
                print(f"[ERROR] Path not found at {path} or {corrected}")
                return None
        return path

    # Correct input PDF path
    input_pdf_path = correct_path(input_pdf_path)
    if input_pdf_path is None:
        print("[ERROR] Input PDF file not found. Exiting.")
        exit(1)

    # Correct output path (for writing)
    output_path_corrected = correct_path(output_path)
    if output_path_corrected is None:
        # For output, maybe the file doesn't exist yet, so we check parent directory instead:
        output_dir = os.path.dirname(output_path)
        corrected_output_dir = output_dir.replace("/app", "/Adobe-India-Hackathon-Team-Snitchers/app")
        if os.path.exists(corrected_output_dir):
            output_path = os.path.join(corrected_output_dir, os.path.basename(output_path))
            print(f"[WARN] Output directory not found. Changed output path to: {output_path}")
        else:
            print(f"[ERROR] Output directory does not exist at {output_dir} or {corrected_output_dir}. Exiting.")
            exit(1)
    else:
        output_path = output_path_corrected

    input_dir = os.path.dirname(input_pdf_path)

    try:
        if args.readonly:
            print(f"[INFO] Setting directory to read-only: {input_dir}")
            make_directory_readonly(input_dir)

        print(f"[INFO] Processing {input_pdf_path}...")
        result = extract_structure(input_pdf_path)
        
        print(f"[INFO] Saving results to: {output_path}")
        save_to_json(result, output_path)

        del result
        gc.collect()

        print(f"[SUCCESS] Structure extraction completed. Output saved to: {output_path}")
    except Exception as e:
        import traceback
        print("[ERROR] An exception occurred during processing:")
        traceback.print_exc()
        exit(1)

if __name__ == "_main_":
    main()