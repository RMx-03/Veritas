#!/bin/bash
# Setup script for Linux/macOS

echo "Setting up Python virtual environment for Veritas backend..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo ""
echo "Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "To run the backend server:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
