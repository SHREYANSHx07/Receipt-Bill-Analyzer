#!/usr/bin/env python3
"""
Test deployed backend connectivity
"""

import requests
import json

def test_deployed_backend(backend_url):
    """Test a deployed backend URL"""
    
    print(f"🔍 Testing deployed backend: {backend_url}")
    print("=" * 60)
    
    # Test endpoints
    endpoints = [
        'stats/',
        'records/',
    ]
    
    for endpoint in endpoints:
        url = f"{backend_url}/{endpoint}"
        print(f"\n📡 Testing: {url}")
        
        try:
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
    
    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("1. If tests pass, update your Streamlit Cloud API_BASE_URL")
    print("2. If tests fail, check your backend deployment")
    print("3. Make sure CORS is configured in Django")

if __name__ == "__main__":
    # Replace with your actual deployed backend URL
    backend_url = input("Enter your deployed backend URL (e.g., https://your-app.railway.app/api): ").strip()
    
    if backend_url:
        test_deployed_backend(backend_url)
    else:
        print("❌ No URL provided") 