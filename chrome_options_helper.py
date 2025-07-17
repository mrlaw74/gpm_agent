"""
Chrome Options Compatibility Helper

This helper provides different Chrome options configurations 
based on the Selenium and Chrome versions to avoid compatibility issues.

Author: mrlaw74
Date: July 17, 2025
"""

import logging
from selenium.webdriver.chrome.options import Options as ChromeOptions

logger = logging.getLogger(__name__)


def get_compatible_chrome_options(debug_address: str, browser_path: str) -> ChromeOptions:
    """
    Get Chrome options that are compatible with different Chrome/Selenium versions
    
    Args:
        debug_address (str): Remote debugging address
        browser_path (str): Path to Chrome browser executable
        
    Returns:
        ChromeOptions: Configured Chrome options
    """
    chrome_options = ChromeOptions()
    
    # Essential options - always safe
    chrome_options.add_experimental_option("debuggerAddress", debug_address)
    chrome_options.binary_location = browser_path
    
    # Basic stability options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Try to add advanced options with error handling
    advanced_options = [
        ("--disable-blink-features=AutomationControlled", "Disable automation detection"),
        ("--disable-web-security", "Disable web security"),
        ("--allow-running-insecure-content", "Allow insecure content"),
        ("--disable-features=VizDisplayCompositor", "Disable compositor"),
        ("--disable-extensions", "Disable extensions"),
        ("--disable-plugins", "Disable plugins"),
        ("--disable-images", "Disable images for faster loading")
    ]
    
    for option, description in advanced_options:
        try:
            chrome_options.add_argument(option)
            logger.debug(f"Added Chrome option: {option} ({description})")
        except Exception as e:
            logger.warning(f"Failed to add Chrome option {option}: {e}")
    
    # Try experimental options with error handling
    experimental_options = [
        ("useAutomationExtension", False, "Disable automation extension"),
        ("excludeSwitches", ["enable-automation"], "Exclude automation switches"),
    ]
    
    for option_name, option_value, description in experimental_options:
        try:
            chrome_options.add_experimental_option(option_name, option_value)
            logger.debug(f"Added experimental option: {option_name} ({description})")
        except Exception as e:
            logger.warning(f"Failed to add experimental option {option_name}: {e}")
    
    # Try preferences with error handling
    try:
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        logger.debug("Added Chrome preferences")
    except Exception as e:
        logger.warning(f"Failed to add Chrome preferences: {e}")
    
    return chrome_options


def get_minimal_chrome_options(debug_address: str, browser_path: str) -> ChromeOptions:
    """
    Get minimal Chrome options that should work with any Chrome/Selenium version
    
    Args:
        debug_address (str): Remote debugging address
        browser_path (str): Path to Chrome browser executable
        
    Returns:
        ChromeOptions: Minimal Chrome options
    """
    chrome_options = ChromeOptions()
    
    # Only the absolutely essential options
    chrome_options.add_experimental_option("debuggerAddress", debug_address)
    chrome_options.binary_location = browser_path
    
    # Minimal stability options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    logger.info("Using minimal Chrome options for maximum compatibility")
    return chrome_options


def test_chrome_options_compatibility():
    """Test different Chrome options configurations"""
    
    test_debug_address = "127.0.0.1:9222"
    test_browser_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    
    print("Testing Chrome Options Compatibility")
    print("=" * 40)
    
    # Test compatible options
    try:
        options1 = get_compatible_chrome_options(test_debug_address, test_browser_path)
        print("✓ Compatible Chrome options created successfully")
    except Exception as e:
        print(f"✗ Compatible Chrome options failed: {e}")
    
    # Test minimal options
    try:
        options2 = get_minimal_chrome_options(test_debug_address, test_browser_path)
        print("✓ Minimal Chrome options created successfully")
    except Exception as e:
        print(f"✗ Minimal Chrome options failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Run compatibility test
    test_chrome_options_compatibility()
