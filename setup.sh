#!/bin/bash

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Initialize database
python -m coterie

echo "Setup complete! You can now run the application with: python main.py" 