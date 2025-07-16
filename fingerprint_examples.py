"""
Fingerprint-Aware Profile Management Examples

This script demonstrates advanced profile creation and management
with fingerprint protection considerations.

Author: mrlaw74
Date: July 17, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient, GPMClientError
from utils import assess_proxy_quality, generate_fingerprint_test_urls, create_fingerprint_test_report
import time


def example_fingerprint_optimized_profiles():
    """Demonstrate fingerprint-optimized profile creation"""
    print("=== Fingerprint-Optimized Profile Creation ===")
    
    client = GPMClient()
    
    try:
        # Example 1: Conservative US profile for e-commerce
        print("\n1. Creating conservative US e-commerce profile...")
        us_profile = client.create_fingerprint_optimized_profile(
            name=f"US Ecommerce {int(time.time())}",
            proxy="us.residential.proxy.com:8080:user:pass",
            location="US",
            detection_level="conservative"
        )
        
        profile_data = us_profile['data']
        print(f"   Created: {profile_data['name']}")
        print(f"   ID: {profile_data['id'][:8]}...")
        
        # Example 2: Balanced EU profile for social media
        print("\n2. Creating balanced UK social media profile...")
        uk_profile = client.create_fingerprint_optimized_profile(
            name=f"UK Social {int(time.time())}",
            proxy="socks5://uk.proxy.com:1080:user:pass",
            location="UK", 
            detection_level="balanced"
        )
        
        profile_data = uk_profile['data']
        print(f"   Created: {profile_data['name']}")
        print(f"   ID: {profile_data['id'][:8]}...")
        
        # Example 3: Aggressive protection for high-risk activities
        print("\n3. Creating aggressive protection profile...")
        secure_profile = client.create_fingerprint_optimized_profile(
            name=f"Secure Research {int(time.time())}",
            proxy="tm://your_api_key|True",
            location="DE",
            detection_level="aggressive"
        )
        
        profile_data = secure_profile['data']
        print(f"   Created: {profile_data['name']}")
        print(f"   ID: {profile_data['id'][:8]}...")
        
        print("\n✓ All fingerprint-optimized profiles created successfully!")
        
    except GPMClientError as e:
        print(f"Error creating profiles: {e}")


def example_fingerprint_validation():
    """Demonstrate fingerprint consistency validation"""
    print("\n=== Fingerprint Consistency Validation ===")
    
    client = GPMClient()
    
    # Test different profile configurations
    test_configs = [
        {
            "name": "Good Config",
            "config": {
                "profile_name": "Good Profile",
                "raw_proxy": "socks5://proxy.com:1080:user:pass",
                "webrtc_mode": 2,
                "os": "Windows 11",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "is_noise_canvas": True,
                "is_noise_audio_context": True,
                "is_random_os": False
            }
        },
        {
            "name": "Problematic Config",
            "config": {
                "profile_name": "Problematic Profile", 
                "raw_proxy": "proxy.com:8080:user:pass",
                "webrtc_mode": 1,  # WebRTC off but has proxy
                "os": "Windows 11",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",  # macOS UA with Windows OS
                "is_noise_canvas": False,
                "is_noise_webgl": False,
                "is_noise_audio_context": False,  # No noise protection
                "is_random_browser_version": True  # Random enabled
            }
        }
    ]
    
    for test in test_configs:
        print(f"\nValidating: {test['name']}")
        validation = client.validate_fingerprint_consistency(test['config'])
        
        print(f"   Risk Level: {validation['risk_level'].upper()}")
        print(f"   Valid: {'✓' if validation['valid'] else '✗'}")
        
        if validation['warnings']:
            print("   Warnings:")
            for warning in validation['warnings']:
                print(f"     ⚠ {warning}")
        
        if validation['suggestions']:
            print("   Suggestions:")
            for suggestion in validation['suggestions']:
                print(f"     💡 {suggestion}")


def example_proxy_assessment():
    """Demonstrate proxy quality assessment"""
    print("\n=== Proxy Quality Assessment ===")
    
    test_proxies = [
        "socks5://residential.proxy.com:1080:user:pass",
        "datacenter.proxy.com:8080:user:pass", 
        "tm://your_api_key|True",
        "tin://your_api_key|False",
        "192.168.1.1:3128",  # Local proxy
        ""  # No proxy
    ]
    
    for proxy in test_proxies:
        print(f"\nAssessing: {proxy if proxy else '(No proxy)'}")
        assessment = assess_proxy_quality(proxy)
        
        print(f"   Quality Score: {assessment['quality']}/100")
        print(f"   Type: {assessment['type']}")
        print(f"   Risk Level: {assessment['risk_level'].upper()}")
        
        print("   Recommendations:")
        for rec in assessment['recommendations']:
            print(f"     • {rec}")


def example_fingerprint_testing():
    """Demonstrate fingerprint testing setup"""
    print("\n=== Fingerprint Testing Setup ===")
    
    # Get test URLs
    test_urls = generate_fingerprint_test_urls()
    
    print("Available fingerprint test URLs:")
    for category, url in test_urls.items():
        print(f"   {category.capitalize()}: {url}")
    
    print("\nRecommended testing workflow:")
    print("1. Create profile with specific settings")
    print("2. Start profile and get browser connection")
    print("3. Visit test URLs to check fingerprint protection")
    print("4. Analyze results and adjust settings if needed")
    
    # Simulate test results analysis
    print("\nExample test results analysis:")
    
    # Mock test results
    mock_results = {
        "canvas": {"unique": False},  # Good - not unique
        "webgl": {"unique": False},   # Good - not unique  
        "webrtc": {"real_ip_detected": False}  # Good - no IP leak
    }
    
    report = create_fingerprint_test_report(mock_results)
    
    print(f"   Overall Score: {report['overall_score']:.1f}/100")
    print(f"   Protection Level: {report['protection_level'].upper()}")
    
    for category, details in report['details'].items():
        print(f"   {category.capitalize()}: {details['status']} (Score: {details['score']})")


def example_location_specific_profiles():
    """Demonstrate location-specific profile optimization"""
    print("\n=== Location-Specific Profile Optimization ===")
    
    client = GPMClient()
    
    locations = ["US", "UK", "DE", "JP"]
    
    print("Creating location-optimized profiles:")
    
    for location in locations:
        try:
            # Create location-specific profile
            profile = client.create_fingerprint_optimized_profile(
                name=f"{location} Optimized {int(time.time())}",
                proxy=f"{location.lower()}.proxy.com:8080:user:pass",
                location=location,
                detection_level="balanced"
            )
            
            print(f"   {location}: {profile['data']['name']} - ID: {profile['data']['id'][:8]}...")
            
        except Exception as e:
            print(f"   {location}: Failed - {e}")
    
    print("\nNote: Each profile is optimized for the target location with:")
    print("   • Appropriate timezone settings")
    print("   • Location-consistent user agents")
    print("   • Regional proxy requirements")
    print("   • Balanced fingerprint protection")


if __name__ == "__main__":
    print("GPM-Login Fingerprint-Aware Profile Management Examples")
    print("=" * 60)
    
    # Check GPM-Login connection
    try:
        client = GPMClient()
        client.list_profiles(per_page=1)
        print("✓ GPM-Login API is accessible")
    except:
        print("✗ GPM-Login API is not accessible")
        print("Please make sure GPM-Login is running on http://127.0.0.1:19995")
        sys.exit(1)
    
    # Run examples
    try:
        example_fingerprint_optimized_profiles()
        example_fingerprint_validation()
        example_proxy_assessment()
        example_fingerprint_testing()
        example_location_specific_profiles()
        
        print("\n" + "=" * 60)
        print("🎯 Fingerprint-aware examples completed successfully!")
        print("\nKey takeaways:")
        print("• Use fingerprint-optimized profile creation for better protection")
        print("• Validate fingerprint consistency before deploying profiles")
        print("• Assess proxy quality to understand detection risks")
        print("• Test fingerprint protection with dedicated testing tools")
        print("• Customize profiles based on target location and use case")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error during examples: {e}")
        import traceback
        traceback.print_exc()
