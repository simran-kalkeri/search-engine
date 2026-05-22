#!/usr/bin/env python3
"""
Startup script for Kintsugi Search Engine Web UI
"""

import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not found. Installing...")
        os.system("pip install flask")
    
    try:
        import pandas
        print("✅ Pandas is installed")
    except ImportError:
        print("❌ Pandas not found. Installing...")
        os.system("pip install pandas")

def main():
    """Start the web application."""
    print("🌟 Starting Kintsugi Search Engine Web UI...")
    
    # Check requirements
    check_requirements()
    
    # Check if data file exists
    data_file = Path("../data-set.json")
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        print("Please make sure data-set.json is in the parent directory")
        sys.exit(1)
    
    print("✅ Data file found")
    print("🌐 Starting web server...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("🔍 Try searching for 'samsng galaxy' to see Kintsugi magic!")
    print("\nPress Ctrl+C to stop the server")
    
    # Import and run the web app
    from web_app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
