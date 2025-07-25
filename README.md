# 📄 PDF Structure Extractor

A command-line Python tool to extract the **title** and **headings** (like H1, H2, H3) from a PDF file using font size
heuristics. It outputs a structured JSON file and supports multilingual PDFs (including Japanese).

---

## 🚀 Features

- ✅ Extract document title from metadata or first page
- ✅ Detect headings (H1, H2, H3) using font size
- ✅ Save output in clean JSON format
- ✅ Multilingual support (Japanese, etc.)
- ✅ Optional: Make input directory and files read-only before processing

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/rahul1039/Adobe-India-Hackathon-Team-Snitchers.git
cd Adobe-India-Hackathon-Team-Snitchers
```
## Solution Structure
```
Challenge_1a/
├── sample_dataset/
│   ├── outputs/         # JSON files provided as outputs.
│   ├── pdfs/            # Input PDF files
│   └── schema/          # Output schema definition
│       └── output_schema.json
├── Dockerfile           # Docker container configuration
├── process_pdfs.py      # Sample processing script
└── README.md            # This file
```

### 3. Install Dependencies

```bash
pip install PyMuPDF
```

## 🚀 Usage

```bash
python extract_pdfs.py
```

---

## 📑 Output Format

```json
{
  "title": "Sample Report",
  "outline": [
    {
      "level": "H1",
      "text": "Executive Summary",
      "page": 0
    },
    {
      "level": "H2",
      "text": "Key Findings",
      "page": 1
    }
  ]
}
```





