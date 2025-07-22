#!/usr/bin/env python3
"""
Backend Deployment Script for Receipt Analyzer
This script helps prepare the Django backend for deployment
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Starting Backend Deployment Preparation...")
    
    # Check if we're in the right directory
    if not os.path.exists('receipt_analyzer/manage.py'):
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Change to Django project directory
    os.chdir('receipt_analyzer')
    
    # Run Django commands
    commands = [
        ("python manage.py collectstatic --noinput", "Collecting static files"),
        ("python manage.py migrate", "Running database migrations"),
        ("python manage.py check --deploy", "Checking deployment settings")
    ]
    
    for command, description in commands:
        if run_command(command, description) is None:
            print("❌ Deployment preparation failed!")
            sys.exit(1)
    
    print("✅ Backend deployment preparation completed!")
    print("\n📋 Next Steps:")
    print("1. Deploy to Railway: railway up")
    print("2. Deploy to Render: Connect your GitHub repo")
    print("3. Deploy to Heroku: heroku create && git push heroku main")

if __name__ == "__main__":
    main() 