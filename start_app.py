#!/usr/bin/env python3
"""
Startup script for Receipt & Bill Analyzer
Runs both Django backend and Streamlit frontend
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import django
        import streamlit
        import requests
        import plotly
        import pandas
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract OCR is installed")
            return True
        else:
            print("❌ Tesseract OCR not found")
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR not found")
        print("Please install Tesseract:")
        print("  macOS: brew install tesseract")
        print("  Ubuntu: sudo apt-get install tesseract-ocr")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def setup_database():
    """Setup Django database"""
    try:
        print("🔧 Setting up database...")
        subprocess.run([
            sys.executable, "receipt_analyzer/manage.py", "migrate"
        ], check=True, capture_output=True)
        print("✅ Database setup complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        return False

def start_django_backend():
    """Start Django backend server"""
    print("🚀 Starting Django backend...")
    try:
        # Change to Django project directory
        os.chdir("receipt_analyzer")
        
        # Start Django server
        process = subprocess.Popen([
            sys.executable, "manage.py", "runserver", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:8000/api/stats/", timeout=5)
            if response.status_code == 200:
                print("✅ Django backend is running on http://localhost:8000")
                return process
            else:
                print("❌ Django backend failed to start properly")
                process.terminate()
                return None
        except requests.exceptions.RequestException:
            print("❌ Django backend failed to start")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error starting Django backend: {e}")
        return None

def start_streamlit_frontend():
    """Start Streamlit frontend"""
    print("🚀 Starting Streamlit frontend...")
    try:
        # Change back to root directory
        os.chdir("..")
        
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("✅ Streamlit frontend is running on http://localhost:8501")
        return process
        
    except Exception as e:
        print(f"❌ Error starting Streamlit frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("📊 Receipt & Bill Analyzer Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Tesseract
    if not check_tesseract():
        print("⚠️  OCR functionality will be limited without Tesseract")
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Start backend
    django_process = start_django_backend()
    if not django_process:
        sys.exit(1)
    
    # Start frontend
    streamlit_process = start_streamlit_frontend()
    if not streamlit_process:
        django_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Application is running!")
    print("📊 Frontend: http://localhost:8501")
    print("🔧 Backend API: http://localhost:8000/api/")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Keep both processes running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if django_process.poll() is not None:
                print("❌ Django backend stopped unexpectedly")
                break
            if streamlit_process.poll() is not None:
                print("❌ Streamlit frontend stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
        # Terminate processes
        django_process.terminate()
        streamlit_process.terminate()
        
        # Wait for processes to stop
        django_process.wait()
        streamlit_process.wait()
        
        print("✅ Servers stopped")

if __name__ == "__main__":
    main() 