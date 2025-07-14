#!/bin/bash

# Activate virtual environment and run the Streamlit app
echo "🚀 Starting Neighborhood Real Estate Analysis App..."
echo "📍 Loading Rebecca Ridge and Sunrise Area data..."

# Activate virtual environment
source venv/bin/activate

# Test imports first
echo "🔍 Testing imports..."
python test_import.py

if [ $? -eq 0 ]; then
    echo "✅ All tests passed. Starting Streamlit app..."
    streamlit run neighborhood_analysis_app.py
else
    echo "❌ Import test failed. Please check the data files and dependencies."
    exit 1
fi