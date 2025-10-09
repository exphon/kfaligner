#!/bin/bash

echo "Korean Forced Aligner - Quick Start"
echo "===================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
if ! pip install -q -r requirements.txt; then
    echo "Warning: Some dependencies may not have installed correctly"
    echo "You may need to install Flask manually: pip install Flask"
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "Starting the Korean Forced Aligner web application..."
echo "Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py
