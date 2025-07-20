"""
Profile Creation Debug Script

This script helps debug profile creation issues with the GPM-Login API.
It tests different profile configurations to identify what causes the 
"NOT NULL constraint failed" error.

Author: mrlaw74
Date: July 20, 2025
"""

import sys
import os
import json
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gpm_client import GPMClient, GPMClientError
except ImportError as e:
    print(f"Error importing GPM client: {e}")
    sys.exit(1)

def test_basic_profile_creation():
    """Test basic profile creation"""
    print("🧪 Testing Basic Profile Creation")
    print("=" * 40)
    
    try:
        client = GPMClient()
        
        # Test 1: Minimal valid profile
        print("Test 1: Minimal profile with required fields only")
        minimal_profile = {
            "name": f"Test_Minimal_{datetime.now().strftime('%H%M%S')}",
            "browser_type": "chrome"
        }
        
        print(f"Profile data: {json.dumps(minimal_profile, indent=2)}")
        
        result = client.create_profile(minimal_profile)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Minimal profile creation successful")
            profile_id = result['data']['id']
            
            # Clean up
            try:
                client.delete_profile(profile_id)
                print("🧹 Test profile cleaned up")
            except:
                pass
        else:
            print("❌ Minimal profile creation failed")
            
    except Exception as e:
        print(f"❌ Test 1 failed: {str(e)}")
    
    print()

def test_profile_with_remark():
    """Test profile creation with remark"""
    print("Test 2: Profile with remark field")
    
    try:
        client = GPMClient()
        
        profile_with_remark = {
            "name": f"Test_WithRemark_{datetime.now().strftime('%H%M%S')}",
            "browser_type": "chrome",
            "remark": "Test profile created for debugging"
        }
        
        print(f"Profile data: {json.dumps(profile_with_remark, indent=2)}")
        
        result = client.create_profile(profile_with_remark)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Profile with remark creation successful")
            profile_id = result['data']['id']
            
            # Clean up
            try:
                client.delete_profile(profile_id)
                print("🧹 Test profile cleaned up")
            except:
                pass
        else:
            print("❌ Profile with remark creation failed")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
    
    print()

def test_profile_with_proxy():
    """Test profile creation with proxy"""
    print("Test 3: Profile with proxy configuration")
    
    try:
        client = GPMClient()
        
        profile_with_proxy = {
            "name": f"Test_WithProxy_{datetime.now().strftime('%H%M%S')}",
            "browser_type": "chrome",
            "remark": "Test profile with proxy",
            "proxy": {
                "proxy_type": "http",
                "proxy_host": "proxy.example.com",
                "proxy_port": 8080,
                "proxy_username": "testuser",
                "proxy_password": "testpass"
            }
        }
        
        print(f"Profile data: {json.dumps(profile_with_proxy, indent=2)}")
        
        result = client.create_profile(profile_with_proxy)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Profile with proxy creation successful")
            profile_id = result['data']['id']
            
            # Clean up
            try:
                client.delete_profile(profile_id)
                print("🧹 Test profile cleaned up")
            except:
                pass
        else:
            print("❌ Profile with proxy creation failed")
            
    except Exception as e:
        print(f"❌ Test 3 failed: {str(e)}")
    
    print()

def test_empty_name_profile():
    """Test what happens with empty name"""
    print("Test 4: Profile with empty name (should fail)")
    
    try:
        client = GPMClient()
        
        empty_name_profile = {
            "name": "",
            "browser_type": "chrome",
            "remark": "Test with empty name"
        }
        
        print(f"Profile data: {json.dumps(empty_name_profile, indent=2)}")
        
        result = client.create_profile(empty_name_profile)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("⚠️  Empty name profile unexpectedly succeeded")
        else:
            print("✅ Empty name profile correctly failed")
            print(f"Error message: {result.get('message', 'No message')}")
            
    except Exception as e:
        print(f"❌ Test 4 failed: {str(e)}")
    
    print()

def test_none_name_profile():
    """Test what happens with None name"""
    print("Test 5: Profile with None name (should fail)")
    
    try:
        client = GPMClient()
        
        none_name_profile = {
            "name": None,
            "browser_type": "chrome",
            "remark": "Test with None name"
        }
        
        print(f"Profile data: {json.dumps(none_name_profile, indent=2)}")
        
        result = client.create_profile(none_name_profile)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("⚠️  None name profile unexpectedly succeeded")
        else:
            print("✅ None name profile correctly failed")
            print(f"Error message: {result.get('message', 'No message')}")
            
    except Exception as e:
        print(f"❌ Test 5 failed: {str(e)}")
    
    print()

def test_missing_name_profile():
    """Test what happens with missing name field"""
    print("Test 6: Profile without name field (should fail)")
    
    try:
        client = GPMClient()
        
        missing_name_profile = {
            "browser_type": "chrome",
            "remark": "Test without name field"
        }
        
        print(f"Profile data: {json.dumps(missing_name_profile, indent=2)}")
        
        result = client.create_profile(missing_name_profile)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("⚠️  Missing name profile unexpectedly succeeded")
        else:
            print("✅ Missing name profile correctly failed")
            print(f"Error message: {result.get('message', 'No message')}")
            
    except Exception as e:
        print(f"❌ Test 6 failed: {str(e)}")
    
    print()

def get_profile_schema():
    """Try to get information about profile schema"""
    print("📋 Attempting to get profile schema information")
    print("=" * 50)
    
    try:
        client = GPMClient()
        
        # Try to get existing profiles to see the structure
        profiles = client.list_profiles(per_page=1)
        
        if profiles.get('success') and profiles.get('data'):
            print("✅ Sample profile structure:")
            sample_profile = profiles['data'][0]
            print(json.dumps(sample_profile, indent=2))
        else:
            print("⚠️  No existing profiles found to examine structure")
            
    except Exception as e:
        print(f"❌ Failed to get profile schema: {str(e)}")
    
    print()

def main():
    """Run all debug tests"""
    print("🧪 GPM-Login Profile Creation Debug Suite")
    print("=" * 50)
    print("This script will test various profile creation scenarios")
    print("to identify the cause of 'NOT NULL constraint failed' errors.")
    print()
    
    # Check connection first
    try:
        client = GPMClient()
        profiles = client.list_profiles(per_page=1)
        print("✅ GPM-Login connection successful")
        print()
    except Exception as e:
        print(f"❌ GPM-Login connection failed: {str(e)}")
        print("Please ensure GPM-Login is running and try again.")
        return
    
    # Get schema information
    get_profile_schema()
    
    # Run tests
    test_basic_profile_creation()
    test_profile_with_remark()
    test_profile_with_proxy()
    test_empty_name_profile()
    test_none_name_profile()
    test_missing_name_profile()
    
    print("🏁 Debug tests completed!")
    print("=" * 50)
    print("If any tests failed with 'NOT NULL constraint', check:")
    print("1. Required fields are present and not empty")
    print("2. Field names match GPM-Login API expectations")
    print("3. Data types are correct (string, int, etc.)")
    print("4. No unexpected null values in the data")

if __name__ == "__main__":
    main()
