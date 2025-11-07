#!/bin/bash
echo "Starting BMS Development Environment..."

# Step 1: Initialize the database
echo "📦Initializing database..."
python init_db.py

# Step 2: Run the Flask server
echo "Starting Flask server..."
flask run
