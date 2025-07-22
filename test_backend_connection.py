#!/usr/bin/env python3
"""
Test script to check backend connectivity
"""

import requests
import os
import json

def test_backend_connection():
    """Test backend API connectivity"""
    
    # Get API URL from environment or use default
    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
    
    print(f"🔍 Testing connection to: {api_base_url}")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        'stats/',
        'records/',
        'upload/'
    ]
    
    for endpoint in endpoints:
        url = f"{api_base_url}/{endpoint}"
        print(f"\n📡 Testing: {url}")
        
        try:
            if endpoint == 'upload/':
                # Skip upload endpoint for GET test
                print("   ⏭️  Skipping upload endpoint (POST only)")
                continue
                
            response = requests.get(url, timeout=10)
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📄 Content Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Response: {json.dumps(data, indent=2)[:200]}...")
                except json.JSONDecodeError:
                    print(f"   ⚠️  Response is not JSON: {response.text[:100]}...")
            else:
                print(f"   ❌ Error: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection Error: Backend not reachable")
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout: Backend not responding")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Recommendations:")
    print("1. Make sure your backend is deployed and running")
    print("2. Check the API_BASE_URL environment variable")
    print("3. Verify CORS settings in Django")
    print("4. Test backend endpoints directly")

if __name__ == "__main__":
    test_backend_connection() 