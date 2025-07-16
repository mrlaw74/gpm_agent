"""
Example usage of GPM-Login Python Agent

This script demonstrates how to use the GPM-Login API client
to manage browser profiles and perform automation tasks.

Author: mrlaw74
Date: July 16, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient, GPMClientError, GPMProfileSession
import time


def example_basic_operations():
    """Demonstrate basic GPM operations"""
    print("=== GPM-Login Basic Operations ===")
    
    # Initialize client
    client = GPMClient(base_url="http://127.0.0.1:19995")
    
    try:
        # 1. List existing profiles
        print("\n1. Listing profiles...")
        response = client.list_profiles(per_page=10)
        profiles = response.get('data', [])
        print(f"Found {len(profiles)} profiles")
        
        for profile in profiles[:3]:  # Show first 3 profiles
            print(f"  - {profile['name']} (ID: {profile['id'][:8]}...)")
        
        # 2. Create a new test profile
        print("\n2. Creating new profile...")
        new_profile = client.create_default_profile(
            name=f"Test Profile {int(time.time())}",
            group_name="Test Group",
            os="Windows 11"
        )
        
        profile_data = new_profile.get('data', {})
        profile_id = profile_data.get('id')
        print(f"Created profile: {profile_data.get('name')} (ID: {profile_id[:8]}...)")
        
        # 3. Get profile details
        print("\n3. Getting profile details...")
        profile_details = client.get_profile(profile_id)
        details = profile_details.get('data', {})
        print(f"Profile Name: {details.get('name')}")
        print(f"Browser: {details.get('browser_type')} {details.get('browser_version')}")
        print(f"Group ID: {details.get('group_id')}")
        
        # 4. Start the profile
        print("\n4. Starting profile...")
        browser_info = client.start_profile(profile_id, win_scale=0.8)
        browser_data = browser_info.get('data', {})
        
        print(f"Browser Location: {browser_data.get('browser_location')}")
        print(f"Debug Address: {browser_data.get('remote_debugging_address')}")
        print(f"Driver Path: {browser_data.get('driver_path')}")
        
        # Wait a bit
        print("\nWaiting 5 seconds...")
        time.sleep(5)
        
        # 5. Stop the profile
        print("\n5. Stopping profile...")
        client.stop_profile(profile_id)
        print("Profile stopped successfully")
        
        # 6. Optional: Delete the test profile
        print("\n6. Cleaning up test profile...")
        # Uncomment the line below to delete the test profile
        # client.delete_profile(profile_id)
        # print("Test profile deleted")
        
    except GPMClientError as e:
        print(f"GPM Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_profile_session():
    """Demonstrate using profile session context manager"""
    print("\n=== GPM Profile Session Example ===")
    
    client = GPMClient()
    
    try:
        # Get first available profile
        profiles = client.list_profiles(per_page=1)
        if not profiles.get('data'):
            print("No profiles available for session example")
            return
        
        profile_id = profiles['data'][0]['id']
        profile_name = profiles['data'][0]['name']
        
        print(f"Using profile: {profile_name}")
        
        # Use context manager for automatic profile management
        with GPMProfileSession(client, profile_id, win_scale=0.6) as session_info:
            browser_data = session_info.get('data', {})
            print(f"Profile started with debug address: {browser_data.get('remote_debugging_address')}")
            
            # Simulate some work
            print("Simulating automation work...")
            time.sleep(3)
            
            print("Work completed")
        
        print("Profile automatically stopped when exiting context")
        
    except GPMClientError as e:
        print(f"GPM Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_search_and_manage():
    """Demonstrate profile search and management"""
    print("\n=== Profile Search and Management ===")
    
    client = GPMClient()
    
    try:
        # Search for profiles by name
        print("\n1. Searching profiles...")
        search_term = "Test"
        response = client.list_profiles(search=search_term)
        found_profiles = response.get('data', [])
        
        print(f"Found {len(found_profiles)} profiles matching '{search_term}'")
        for profile in found_profiles:
            print(f"  - {profile['name']} (Created: {profile['created_at'][:10]})")
        
        # Find profile by exact name
        print("\n2. Finding profile by name...")
        test_profile = client.get_profile_by_name("Test Profile")
        if test_profile:
            print(f"Found profile: {test_profile['name']}")
        else:
            print("Profile not found by name")
        
        # List profiles in different sort orders
        print("\n3. Different sorting options...")
        sorts = {
            0: "Newest first",
            1: "Oldest first", 
            2: "Name A-Z",
            3: "Name Z-A"
        }
        
        for sort_id, sort_name in sorts.items():
            response = client.list_profiles(sort=sort_id, per_page=1)
            if response.get('data'):
                first_profile = response['data'][0]
                print(f"{sort_name}: {first_profile['name']}")
        
    except GPMClientError as e:
        print(f"GPM Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def example_proxy_configurations():
    """Demonstrate different proxy configurations"""
    print("\n=== Proxy Configuration Examples ===")
    
    client = GPMClient()
    
    # Example proxy configurations
    proxy_examples = {
        "HTTP Proxy": "123.456.789.0:8080:username:password",
        "SOCKS5 Proxy": "socks5://123.456.789.0:1080:username:password",
        "TMProxy": "tm://your_api_key|True",
        "TinProxy": "tin://your_api_key|False",
        "TinsoftProxy": "tinsoft://your_api_key|True"
    }
    
    print("Example proxy configurations:")
    for proxy_type, proxy_config in proxy_examples.items():
        print(f"{proxy_type}: {proxy_config}")
    
    # Create profile with proxy (example - won't actually work without real proxy)
    try:
        print("\nCreating profile with HTTP proxy example...")
        profile_with_proxy = {
            "profile_name": f"Proxy Test {int(time.time())}",
            "group_name": "Proxy Tests",
            "browser_core": "chromium",
            "browser_name": "Chrome",
            "raw_proxy": "",  # Add real proxy here to test
            "webrtc_mode": 2  # Base on IP
        }
        
        # Uncomment to actually create (need real proxy)
        # new_profile = client.create_profile(profile_with_proxy)
        # print(f"Created proxy profile: {new_profile['data']['name']}")
        
        print("(Proxy profile creation skipped - add real proxy to test)")
        
    except GPMClientError as e:
        print(f"Proxy configuration error: {e}")


if __name__ == "__main__":
    print("GPM-Login Python Agent Examples")
    print("================================")
    
    # Check if GPM-Login is running
    try:
        client = GPMClient()
        # Try to list profiles to check connection
        client.list_profiles(per_page=1)
        print("✓ GPM-Login API is accessible")
    except:
        print("✗ GPM-Login API is not accessible")
        print("Please make sure GPM-Login is running on http://127.0.0.1:19995")
        sys.exit(1)
    
    # Run examples
    try:
        example_basic_operations()
        example_profile_session()
        example_search_and_manage()
        example_proxy_configurations()
        
        print("\n=== Examples completed successfully! ===")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error during examples: {e}")
        import traceback
        traceback.print_exc()
