#!/usr/bin/env python3
"""
Startup script for the Agentic PPT application.
This script starts the Streamlit web application.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the Streamlit application."""
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found!")
        print("Please copy env_template.txt to .env and configure your API keys.")
        print("Example: cp env_template.txt .env")
        print()
    
    # Start Streamlit
    try:
        print("🚀 Starting Agentic PPT application...")
        print("📱 The application will open in your default web browser")
        print("🔗 URL: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        print()
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 