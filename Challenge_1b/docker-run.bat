@echo off
REM Document Analyst Docker Build and Run Script for Windows

echo 🐳 Building Document Analyst Docker Image...
docker build -t document-analyst .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Docker image built successfully!
    echo.
    echo 🚀 Running Document Analyst...
    
    REM Run the container
    docker run --name document-analyst-run document-analyst
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo 📋 Copying output files from container...
        
        REM Copy output files from container to host
        docker cp "document-analyst-run:/app/Collection 1/challenge1b_output.json" "Collection 1/"
        docker cp "document-analyst-run:/app/Collection 2/challenge1b_output.json" "Collection 2/"
        docker cp "document-analyst-run:/app/Collection 3/challenge1b_output.json" "Collection 3/"
        
        echo ✅ Output files copied successfully!
        echo.
        echo 📁 Output files available at:
        echo    - Collection 1/challenge1b_output.json
        echo    - Collection 2/challenge1b_output.json
        echo    - Collection 3/challenge1b_output.json
    ) else (
        echo ❌ Container execution failed!
    )
    
    REM Clean up container
    docker rm document-analyst-run
) else (
    echo ❌ Docker build failed!
)

pause
