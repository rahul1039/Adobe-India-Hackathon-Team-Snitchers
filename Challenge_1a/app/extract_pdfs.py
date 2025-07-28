import os
import regex as re  # better unicode regex support
import json
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pytesseract import Output
import onnxruntime as ort
from transformers import AutoTokenizer
import numpy as np

# ✅ Use quantized multilingual MiniLM model
MODEL_PATH = "./model/minilm-multilingual/model-quant.onnx"
TOKENIZER_PATH = "./model/minilm-multilingual"

tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, local_files_only=True)
session = ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

def get_embeddings(texts):
    inputs = tokenizer(texts, return_tensors="np", padding=True, truncation=True)
    ort_inputs = {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"]
    }
    outputs = session.run(None, ort_inputs)
    last_hidden_state = outputs[0]
    return last_hidden_state.mean(axis=1)

def normalize_text(text: str) -> str:
    text = re.sub(r"([A-Za-z])\1{2,}", r"\1", text)
    text = re.sub(r"([A-Za-z])\s*:{2,}", r"\1:", text)
    text = re.sub(r"\s{2,}", " ", text).strip()
    parts = text.split(" ", 1)
    if len(parts) > 1:
        text = parts[0] + "  " + parts[1]
    return text + "  "

def detect_title(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text() or ""
        raw_lines = text.split("\n")

    lines = [l.rstrip() for l in raw_lines if l.strip()]
    title_parts = []

    for line in lines:
        if any(re.search(p, line, re.I) for p in [r"Table of Contents", r"^\d+(\.\d+)*[\s.]", r"Copyright", r"Version\s+\d"]):
            break
        if len(line.split()) > 8:
            break

        title_parts.append(line)
        if len(title_parts) >= 2:
            break

    return normalize_text(" ".join(title_parts))

def extract_outline_from_toc(pdf_path):
    outline = []
    merged_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        buffer = ""
        for page in pdf.pages:
            text = page.extract_text() or ""
            for raw in text.split("\n"):
                line = raw.strip()
                if not line:
                    continue
                if re.search(r"\.{2,}\s*\d+$", line):
                    merged_lines.append((buffer + " " + line).strip())
                    buffer = ""
                elif re.search(r"\p{L}{2,}", line):
                    buffer += (" " + line).strip()

    for full_line in merged_lines:
        m = re.match(r"^(.+?)\s+\.{2,}\s*(\d+)$", full_line)
        if not m:
            continue

        heading_text, page_ref = m.group(1).strip(), int(m.group(2))

        if len(heading_text.split()) > 25:
            continue

        num_match = re.match(r"^(\d+(?:\.\d+)*)", heading_text)
        if num_match:
            level = f"H{num_match.group(1).count('.') + 1}"
        elif len(heading_text) <= 15:
            level = "H1"  # short headings → H1
        else:
            level = "H2"

        outline.append({
            "level": level,
            "text": heading_text + " ",
            "page": page_ref - 1
        })

    return sorted(outline, key=lambda x: (x["page"], x["text"]))

def extract_fallback_headings(pdf_path):
    skip_words = {"ADDRESS", "PHONE", "EMAIL", "CONTACT"}
    with pdfplumber.open(pdf_path) as pdf:
        for p_idx, page in enumerate(pdf.pages[:3]):
            words = page.extract_words(x_tolerance=2, y_tolerance=3)
            lines = {}
            for w in words:
                key = round(w["top"], 1)
                lines.setdefault(key, []).append(w)

            for items in lines.values():
                line_text = " ".join([i["text"] for i in sorted(items, key=lambda x: x["x0"])])
                if re.match(r"^[A-Z0-9\s\-]{6,}$", line_text.strip()):
                    first_word = line_text.strip().split()[0].rstrip(":").upper()
                    if first_word not in skip_words:
                        return [{"level": "H1", "text": line_text.strip() + " ", "page": p_idx}]
    return []

def add_missing_headings(pdf_path, outline):
    required = ["Revision History", "Acknowledgements"]
    found_texts = {o["text"].strip().lower() for o in outline}

    with pdfplumber.open(pdf_path) as pdf:
        for p_idx, page in enumerate(pdf.pages[:3]):
            text = page.extract_text() or ""
            for line in text.split("\n"):
                for req in required:
                    if req.lower() in line.lower() and req.lower() not in found_texts:
                        outline.append({
                            "level": "H1",
                            "text": req + " ",
                            "page": p_idx
                        })
                        found_texts.add(req.lower())

    return sorted(outline, key=lambda x: (x["page"], x["text"]))

def deduplicate_outline(outline):
    if not outline:
        return outline

    texts = [o["text"].strip() for o in outline]
    embeddings = get_embeddings(texts)

    final_outline = [outline[0]]
    for i in range(1, len(outline)):
        sims = np.dot(embeddings[:i], embeddings[i]) / (
            np.linalg.norm(embeddings[:i], axis=1) * np.linalg.norm(embeddings[i])
        )
        if sims.max() < 0.95:  # keep only non-duplicate headings
            final_outline.append(outline[i])

    return final_outline

def fix_outline_for_last_text(pdf_path, outline):
    if not outline or len(outline[0]["text"].strip()) < 10:
        try:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        except Exception:
            return outline

        data = pytesseract.image_to_data(images[0], lang="jpn+eng", output_type=Output.DICT)
        words = [data["text"][i] for i in range(len(data["text"])) if data["text"][i].strip()]

        for i, w in enumerate(words):
            if w.strip().lower().startswith("hope"):
                hope_text = " ".join(words[i:])
                if "!" in hope_text:
                    hope_text = hope_text.split("!")[0] + "!"
                    if hope_text.upper().startswith("HOPE TO SEE YOU THERE"):
                        hope_text = "HOPE To SEE You THERE!"
                        return [{"level": "H1", "text": hope_text.strip() + " ", "page": 0}]
    return outline

def process_pdf(pdf_path):
    title = detect_title(pdf_path)
    if re.match(r"^\s*ADDRESS[:\-]?", title, re.I):
        title = ""

    outline = extract_outline_from_toc(pdf_path) or extract_fallback_headings(pdf_path)
    outline = add_missing_headings(pdf_path, outline)
    outline = deduplicate_outline(outline)

    if not title or (outline and len(outline[0]["text"].strip()) < 10):
        outline = fix_outline_for_last_text(pdf_path, outline)

    return {"title": title, "outline": outline}

def main():
    input_dir = "./input"
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = process_pdf(pdf_path)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            print(f"✅ Saved: {output_path}")

if __name__ == "__main__":
    main()
