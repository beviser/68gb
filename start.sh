#!/bin/bash

# Start script for 68GB Game API Crawler

echo "Starting 68GB Game API Crawler..."

# Set environment variables if not set
export PYTHONPATH="${PYTHONPATH}:/app"
export DISPLAY=:99

# Start Xvfb for headless browser support
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait a moment for Xvfb to start
sleep 2

# Run the application
python main.py
