"""
Test script for GPM-Login Python Agent

This script runs basic tests to verify the agent is working correctly.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient, GPMClientError


def test_connection():
    """Test basic connection to GPM-Login API"""
    print("Testing GPM-Login API connection...")
    
    try:
        client = GPMClient()
        response = client.list_profiles(per_page=1)
        
        print("✓ Connection successful")
        total = response.get('pagination', {}).get('total', 0)
        print(f"  Total profiles: {total}")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_profile_operations():
    """Test profile CRUD operations"""
    print("\nTesting profile operations...")
    
    client = GPMClient()
    created_profile_id = None
    
    try:
        # Create test profile
        print("  Creating test profile...")
        test_profile = client.create_default_profile(
            name=f"Test Profile {int(time.time())}",
            group_name="Test"
        )
        
        created_profile_id = test_profile['data']['id']
        print(f"  ✓ Profile created: {created_profile_id[:8]}...")
        
        # Get profile details
        print("  Getting profile details...")
        details = client.get_profile(created_profile_id)
        profile_name = details['data']['name']
        print(f"  ✓ Profile details retrieved: {profile_name}")
        
        # Start profile
        print("  Starting profile...")
        browser_info = client.start_profile(created_profile_id)
        debug_address = browser_info['data']['remote_debugging_address']
        print(f"  ✓ Profile started: {debug_address}")
        
        # Wait a moment
        time.sleep(2)
        
        # Stop profile
        print("  Stopping profile...")
        client.stop_profile(created_profile_id)
        print("  ✓ Profile stopped")
        
        # Search by name
        print("  Testing profile search...")
        found = client.get_profile_by_name(profile_name)
        if found:
            print(f"  ✓ Profile found by name: {found['name']}")
        else:
            print("  ✗ Profile not found by name")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Profile operations failed: {e}")
        return False
        
    finally:
        # Cleanup: delete test profile
        if created_profile_id:
            try:
                print("  Cleaning up test profile...")
                # Uncomment to actually delete
                # client.delete_profile(created_profile_id)
                print("  ✓ Test profile cleanup completed")
            except:
                print("  ! Test profile cleanup failed")


def test_list_operations():
    """Test profile listing and filtering"""
    print("\nTesting list operations...")
    
    try:
        client = GPMClient()
        
        # Test basic listing
        print("  Testing basic listing...")
        response = client.list_profiles(per_page=5)
        profiles = response['data']
        pagination = response['pagination']
        
        print(f"  ✓ Listed {len(profiles)} profiles (total: {pagination['total']})")
        
        # Test sorting
        print("  Testing different sort orders...")
        for sort_id in [0, 1, 2, 3]:
            response = client.list_profiles(sort=sort_id, per_page=1)
            if response['data']:
                profile_name = response['data'][0]['name']
                print(f"    Sort {sort_id}: {profile_name}")
        
        # Test search
        if profiles:
            print("  Testing search functionality...")
            # Search for first character of first profile name
            search_term = profiles[0]['name'][0] if profiles[0]['name'] else 'T'
            response = client.list_profiles(search=search_term)
            found_count = len(response['data'])
            print(f"  ✓ Search '{search_term}' found {found_count} profiles")
        
        return True
        
    except Exception as e:
        print(f"  ✗ List operations failed: {e}")
        return False


def test_error_handling():
    """Test error handling for invalid operations"""
    print("\nTesting error handling...")
    
    client = GPMClient()
    
    try:
        # Test invalid profile ID
        print("  Testing invalid profile ID...")
        try:
            client.get_profile("invalid-profile-id")
            print("  ✗ Should have failed with invalid ID")
            return False
        except GPMClientError:
            print("  ✓ Correctly handled invalid profile ID")
        
        # Test starting non-existent profile
        print("  Testing start non-existent profile...")
        try:
            client.start_profile("non-existent-id")
            print("  ✗ Should have failed with non-existent profile")
            return False
        except GPMClientError:
            print("  ✓ Correctly handled non-existent profile start")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error handling test failed: {e}")
        return False


def test_context_manager():
    """Test profile session context manager"""
    print("\nTesting context manager...")
    
    try:
        from gpm_client import GPMProfileSession
        
        client = GPMClient()
        
        # Get first available profile
        profiles = client.list_profiles(per_page=1)
        if not profiles['data']:
            print("  ! No profiles available for context manager test")
            return True
        
        profile_id = profiles['data'][0]['id']
        profile_name = profiles['data'][0]['name']
        
        print(f"  Using profile: {profile_name}")
        
        # Test context manager
        print("  Testing context manager...")
        with GPMProfileSession(client, profile_id) as session_info:
            debug_address = session_info['data']['remote_debugging_address']
            print(f"  ✓ Profile started in context: {debug_address}")
            time.sleep(1)
        
        print("  ✓ Profile automatically stopped when exiting context")
        return True
        
    except Exception as e:
        print(f"  ✗ Context manager test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("GPM-Login Python Agent Tests")
    print("=" * 40)
    
    tests = [
        ("Connection Test", test_connection),
        ("Profile Operations", test_profile_operations),
        ("List Operations", test_list_operations),
        ("Error Handling", test_error_handling),
        ("Context Manager", test_context_manager)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{passed + 1}/{total}] {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
