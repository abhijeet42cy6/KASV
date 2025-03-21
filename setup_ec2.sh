#!/bin/bash

# Setup script for Warewolf on EC2
echo "Setting up Warewolf on EC2..."

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and required tools
echo "Installing Python and dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv git

# Create and activate virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Fix python-jose compatibility issue
echo "Fixing python-jose compatibility issue..."
python fix_jose.py

# Create database tables
echo "Setting up database..."
python run.py

echo "Setup complete!"
echo "To start the application, run: uvicorn app.main:app --host 0.0.0.0 --port 8000" 