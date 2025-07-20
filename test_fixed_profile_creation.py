"""
Test Fixed Profile Creation

This script tests the fixed profile creation using the fingerprint optimized method.

Author: mrlaw74
Date: July 20, 2025
"""

import sys
import os
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gpm_client import GPMClient
except ImportError as e:
    print(f"Error importing GPM client: {e}")
    sys.exit(1)

def test_fixed_profile_creation():
    """Test the fixed profile creation method"""
    print("🧪 Testing Fixed Profile Creation")
    print("=" * 40)
    
    try:
        client = GPMClient()
        
        # Test using the fingerprint optimized method
        print("Creating profile using fingerprint optimized method...")
        
        profile_name = f"GUI_Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = client.create_fingerprint_optimized_profile(
            name=profile_name,
            proxy="",
            location="US",
            detection_level="balanced"
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("✅ Profile creation successful!")
            profile_id = result['data']['id']
            print(f"Profile ID: {profile_id}")
            
            # Test cleanup
            try:
                delete_result = client.delete_profile(profile_id)
                if delete_result.get('success'):
                    print("🧹 Test profile cleaned up successfully")
                else:
                    print("⚠️  Failed to cleanup test profile")
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
                
        else:
            print("❌ Profile creation failed")
            print(f"Error: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def test_profile_with_proxy():
    """Test profile creation with proxy"""
    print("\n🧪 Testing Profile Creation with Proxy")
    print("=" * 40)
    
    try:
        client = GPMClient()
        
        profile_name = f"GUI_Proxy_Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        proxy_string = "proxy.example.com:8080:user:pass"
        
        result = client.create_fingerprint_optimized_profile(
            name=profile_name,
            proxy=proxy_string,
            location="US",
            detection_level="balanced"
        )
        
        print(f"Result: {result}")
        
        if result.get('success'):
            print("✅ Profile with proxy creation successful!")
            profile_id = result['data']['id']
            print(f"Profile ID: {profile_id}")
            
            # Test cleanup
            try:
                delete_result = client.delete_profile(profile_id)
                if delete_result.get('success'):
                    print("🧹 Test profile cleaned up successfully")
                else:
                    print("⚠️  Failed to cleanup test profile")
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
                
        else:
            print("❌ Profile with proxy creation failed")
            print(f"Error: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

def main():
    """Run the tests"""
    print("🔧 Testing Fixed Profile Creation Methods")
    print("=" * 50)
    
    # Check connection first
    try:
        client = GPMClient()
        profiles = client.list_profiles(per_page=1)
        print("✅ GPM-Login connection successful")
    except Exception as e:
        print(f"❌ GPM-Login connection failed: {str(e)}")
        return
    
    # Run tests
    test_fixed_profile_creation()
    test_profile_with_proxy()
    
    print("\n🏁 Tests completed!")
    print("=" * 50)
    print("If these tests pass, the GUI should now work correctly!")

if __name__ == "__main__":
    main()
