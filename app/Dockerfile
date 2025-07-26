# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY extract_pdfs.py .

# Install PyMuPDF
RUN pip install PyMuPDF

# Run extract_pdfs.py when the container launches
CMD ["python", "extract_pdfs.py"]
