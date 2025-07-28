#!/bin/bash

# Document Analyst Docker Build and Run Script

echo "🐳 Building Document Analyst Docker Image..."
docker build -t document-analyst .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 Running Document Analyst..."
    
    # Run the container and copy outputs back to host
    docker run --name document-analyst-run document-analyst
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "📋 Copying output files from container..."
        
        # Copy output files from container to host
        docker cp document-analyst-run:/app/Collection\ 1/challenge1b_output.json ./Collection\ 1/
        docker cp document-analyst-run:/app/Collection\ 2/challenge1b_output.json ./Collection\ 2/
        docker cp document-analyst-run:/app/Collection\ 3/challenge1b_output.json ./Collection\ 3/
        
        echo "✅ Output files copied successfully!"
        echo ""
        echo "📁 Output files available at:"
        echo "   - Collection 1/challenge1b_output.json"
        echo "   - Collection 2/challenge1b_output.json" 
        echo "   - Collection 3/challenge1b_output.json"
    else
        echo "❌ Container execution failed!"
    fi
    
    # Clean up container
    docker rm document-analyst-run
else
    echo "❌ Docker build failed!"
fi
