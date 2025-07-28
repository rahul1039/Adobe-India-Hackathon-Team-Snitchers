# Document Analyst Docker Setup

This directory contains a Dockerized version of the Intelligent Document Analyst that processes PDF collections and generates analysis outputs.

## 🐳 Docker Files

- `Dockerfile` - Main Docker configuration
- `.dockerignore` - Excludes unnecessary files from build context
- `docker-run.sh` - Linux/Mac build and run script
- `docker-run.bat` - Windows build and run script

## 🚀 Quick Start

### Option 1: Use the automated scripts

**Linux/Mac:**
```bash
chmod +x docker-run.sh
./docker-run.sh
```

**Windows:**
```cmd
docker-run.bat
```

### Option 2: Manual Docker commands

**Build the image:**
```bash
docker build -t document-analyst .
```

**Run the container:**
```bash
docker run --name document-analyst-run document-analyst
```

**Copy output files:**
```bash
docker cp "document-analyst-run:/app/Collection 1/challenge1b_output.json" "Collection 1/"
docker cp "document-analyst-run:/app/Collection 2/challenge1b_output.json" "Collection 2/"
docker cp "document-analyst-run:/app/Collection 3/challenge1b_output.json" "Collection 3/"
```

**Clean up:**
```bash
docker rm document-analyst-run
```

## 📋 What the Container Does

1. **Processes 3 Collections:**
   - Collection 1: Travel planning documents (Travel Planner persona)
   - Collection 2: HR forms and documents (HR Professional persona)  
   - Collection 3: Food/recipe documents (Food Contractor persona)

2. **Generates Output Files:**
   - `Collection 1/challenge1b_output.json`
   - `Collection 2/challenge1b_output.json`
   - `Collection 3/challenge1b_output.json`

3. **Analysis Features:**
   - Extracts relevant sections based on persona
   - Finds exact matches for domain-specific content
   - Generates detailed recipe content for food domain
   - Provides metadata about processing time and document count

## 🔧 Container Specifications

- **Base Image:** Python 3.9 slim
- **Dependencies:** PyMuPDF, tqdm
- **Memory:** Optimized for <1GB usage
- **Processing Time:** <60 seconds per collection
- **CPU Only:** No GPU dependencies

## 📁 Directory Structure

```
Challenge_1b/
├── Dockerfile
├── .dockerignore
├── docker-run.sh
├── docker-run.bat
├── document_analyst.py
├── requirements.txt
├── Collection 1/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json (generated)
├── Collection 2/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json (generated)
└── Collection 3/
    ├── PDFs/
    ├── challenge1b_input.json
    └── challenge1b_output.json (generated)
```

## 🐛 Troubleshooting

**Container fails to start:**
- Ensure Docker is running
- Check that all Collection directories exist
- Verify PDF files are present in each Collection's PDFs folder

**Output files not copied:**
- Make sure container completed successfully
- Check container logs: `docker logs document-analyst-run`
- Verify destination directories exist

**Build fails:**
- Check Docker daemon is running
- Ensure you're in the Challenge_1b directory
- Try cleaning Docker cache: `docker system prune`
