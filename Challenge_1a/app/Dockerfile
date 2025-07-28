FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils tesseract-ocr libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install only required Python dependencies (No torch)
RUN pip install --no-cache-dir \
    pdfplumber pytesseract pdf2image onnxruntime transformers

# Copy quantized ONNX model + tokenizer + script
COPY ./model/minilm-multilingual ./model/minilm-multilingual
COPY extract_pdfs.py ./extract_pdfs.py

CMD ["python", "extract_pdfs.py"]
