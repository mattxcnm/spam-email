#!/bin/bash

# Setup script for Spam Email Processing Tool

echo "Setting up Spam Email Processing Tool..."

# Make scripts executable
chmod +x spam-email.py
chmod +x email_reporter.py
chmod +x extract_emails.py

# Create necessary directories
mkdir -p consume
mkdir -p processed
mkdir -p logs

# Install Python dependencies
if command -v pip3 &> /dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "pip not found. Please install Python dependencies manually:"
    echo "pip install -r requirements.txt"
fi

# Create sample configuration if it doesn't exist
if [ ! -f config.json ]; then
    echo "Creating sample configuration file..."
    echo "Please edit config.json to add your email settings for reporting."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To get started:"
echo "1. Place spam email files (.eml or .msg) in the 'consume' directory"
echo "2. Run: python3 spam-email.py"
echo "3. Check the 'logs' directory for results"
echo ""
echo "For Apple Mail users:"
echo "- Save emails as 'Raw Message Source' (.eml format)"
echo "- Or try the experimental extractor: python3 extract_emails.py"
echo ""
echo "To send reports via email:"
echo "1. Configure your email settings in config.json"
echo "2. Run: python3 email_reporter.py"
