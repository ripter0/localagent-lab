#!/bin/bash

echo "=== CleanSignal Pollution Reporting Platform ==="
echo ""

# Create necessary directories
mkdir -p data templates static
echo "✓ Directories created"

# Initialize database
echo "Initializing database..."
python database_init.py

# Run the application
echo "Starting CleanSignal server..."
python app.py