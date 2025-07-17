"""
Quick test to verify GPM-Login connection and basic functionality

Author: mrlaw74
Date: July 17, 2025
"""

import sys
import os
import time

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gpm_client import GPMClient, GPMClientError
    print("✓ GPM client imported successfully")
except ImportError as e:
    print(f"✗ Failed to import GPM client: {e}")
    sys.exit(1)

def test_connection():
    """Test GPM-Login API connection"""
    try:
        print("Testing GPM-Login connection...")
        client = GPMClient()
        
        # Test basic API call
        profiles = client.list_profiles(per_page=1)
        print(f"✓ GPM-Login API is accessible")
        
        # Handle the actual response format
        if isinstance(profiles, dict) and 'data' in profiles:
            if 'pagination' in profiles:
                total = profiles['pagination'].get('total', 'unknown')
            else:
                total = len(profiles['data'])
        else:
            total = 'unknown'
            
        print(f"  Total profiles: {total}")
        print(f"  Current page profiles: {len(profiles.get('data', []))}")
        
        return True
        
    except GPMClientError as e:
        print(f"✗ GPM-Login API error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_profile_creation():
    """Test profile creation"""
    try:
        print("\nTesting profile creation...")
        client = GPMClient()
        
        # Simple profile data
        profile_data = {
            "profile_name": f"Test Profile {int(time.time())}",
            "group_name": "All",
            "browser_core": "chromium",
            "browser_name": "Chrome",
            "browser_version": "119.0.6045.124",
            "is_random_browser_version": False,
            "raw_proxy": "",
            "startup_urls": "",
            "is_masked_font": True,
            "is_noise_canvas": False,
            "is_noise_webgl": False,
            "is_noise_client_rect": False,
            "is_noise_audio_context": True,
            "is_random_screen": False,
            "is_masked_webgl_data": True,
            "is_masked_media_device": True,
            "is_random_os": False,
            "os": "Windows 11",
            "webrtc_mode": 2,
            "user_agent": "auto"
        }
        
        profile = client.create_profile(profile_data)
        profile_id = profile['data']['id']
        print(f"✓ Profile created successfully: {profile_id}")
        
        # Try to start the profile (this will test if GPM-Login can actually start browsers)
        print("  Testing profile start...")
        start_result = client.start_profile(profile_id)
        print(f"  ✓ Profile started: {start_result['data']['remote_debugging_address']}")
        
        # Stop the profile
        print("  Stopping profile...")
        client.stop_profile(profile_id)
        print("  ✓ Profile stopped")
        
        # Delete the test profile
        print("  Cleaning up test profile...")
        client.delete_profile(profile_id)
        print("  ✓ Test profile deleted")
        
        return True
        
    except Exception as e:
        print(f"✗ Profile creation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("GPM-Login Python Agent - Connection Test")
    print("=" * 50)
    
    # Test 1: Basic connection
    if not test_connection():
        print("\n❌ Connection test failed!")
        print("Make sure GPM-Login is running on http://127.0.0.1:19995")
        return
    
    # Test 2: Profile creation
    import time
    if not test_profile_creation():
        print("\n❌ Profile creation test failed!")
        print("There might be an issue with GPM-Login profile management")
        return
    
    print("\n🎉 All tests passed!")
    print("GPM-Login Python Agent is working correctly.")
    print("\nYou can now run:")
    print("  python simple_youtube_automation.py")
    print("  python youtube_automation_flow.py")

if __name__ == "__main__":
    main()
