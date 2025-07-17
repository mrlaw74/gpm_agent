"""
Simple YouTube Automation Example

A streamlined example of the complete automation flow:
Profile creation → Google sign-in → YouTube video playback

Requirements:
- pip install selenium

Author: mrlaw74
Date: July 17, 2025
"""

import sys
import os
import time
import logging

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient
from gpm_selenium import GPMSeleniumDriver

# Import Selenium (with error handling)
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
except ImportError as e:
    print("❌ Selenium is not installed!")
    print("Please install it with: pip install selenium")
    sys.exit(1)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simple_youtube_automation(email: str, password: str, video_search: str = "Python tutorial"):
    """
    Simple automation flow: Create profile → Google login → YouTube video
    
    Args:
        email (str): Google account email
        password (str): Google account password  
        video_search (str): What to search for on YouTube
    """
    
    # Initialize GPM client
    gpm_client = GPMClient()
    profile_id = None
    
    try:
        # 1. Create a new profile
        logger.info("🔨 Creating new profile...")
        profile_data = {
            "profile_name": f"YouTube Bot {int(time.time())}",
            "group_name": "All",
            "browser_core": "chromium", 
            "browser_name": "Chrome",
            "browser_version": "119.0.6045.124",
            "is_random_browser_version": False,
            "raw_proxy": "",  # Add proxy if needed: "proxy.server.com:8080:user:pass"
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
        profile = gpm_client.create_profile(profile_data)
        profile_id = profile['data']['id']
        logger.info(f"✓ Profile created: {profile_id}")
        
        # 2. Start profile and create browser
        logger.info("🌐 Starting browser...")
        with GPMSeleniumDriver(gpm_client) as gpm_driver:
            driver = gpm_driver.create_driver_from_profile(profile_id)
            logger.info("✓ Browser started")
            
            # 3. Go to Google and sign in
            logger.info("🔐 Signing into Google...")
            driver.get("https://accounts.google.com/signin")
            time.sleep(5)  # Increased wait time
            
            # Enter email
            email_input = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "identifierId"))
            )
            email_input.clear()
            email_input.send_keys(email)
            
            # Click Next
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "identifierNext"))
            )
            next_button.click()
            time.sleep(5)  # Increased wait time
            
            # Enter password - wait for it to be interactable
            password_input = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
            )
            time.sleep(2)  # Small delay before interacting
            password_input.clear()
            password_input.send_keys(password)
            
            # Click Next
            password_next = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "passwordNext"))
            )
            password_next.click()
            time.sleep(5)
            
            logger.info("✓ Signed into Google")
            
            # 4. Go to YouTube
            logger.info("📺 Opening YouTube...")
            driver.get("https://www.youtube.com")
            time.sleep(3)
            
            # 5. Search for video
            logger.info(f"🔍 Searching for: {video_search}")
            
            # Try multiple selectors for the search box
            search_selectors = [
                "input#search",
                "input[name='search_query']",
                "input[aria-label*='Search']",
                "#search-input input",
                "ytd-searchbox input"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    logger.info(f"Found search box with selector: {selector}")
                    break
                except:
                    continue
            
            if not search_box:
                logger.error("Could not find YouTube search box")
                return
            
            search_box.clear()
            search_box.send_keys(video_search)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)
            
            # 6. Click first video
            logger.info("▶️ Playing first video...")
            first_video = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
            )
            video_title = first_video.get_attribute("title")
            logger.info(f"Playing: {video_title}")
            first_video.click()
            
            # 7. Let video play
            logger.info("🎬 Video is playing...")
            time.sleep(10)  # Watch for 10 seconds
            
            # Check if video is actually playing
            try:
                current_time = driver.execute_script("return document.querySelector('video').currentTime")
                if current_time > 0:
                    logger.info(f"✓ Confirmed video is playing at {current_time:.1f} seconds")
                else:
                    logger.warning("Video may not be playing (currentTime is 0)")
            except Exception as e:
                logger.warning(f"Could not verify video playback: {e}")
            
            logger.info("🎉 Automation completed successfully!")
            
            # Optional: Keep browser open for manual inspection
            print("\nVideo is playing! Press Enter to close browser and stop profile...")
            input()
            
        # The context manager will automatically close the driver and stop the profile
        logger.info("🧹 Closing browser and stopping profile...")
    
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Note: The finally block is now removed since GPMSeleniumDriver context manager
    # handles cleanup automatically


def main():
    """Main function"""
    print("Simple YouTube Automation with GPM-Login")
    print("=" * 40)
    
    # Get user input
    email = input("Google Email: ").strip()
    password = input("Google Password: ").strip()
    search = input("YouTube Search (default: Python tutorial): ").strip()
    
    if not search:
        search = "Python tutorial"
    
    if not email or not password:
        print("❌ Email and password are required!")
        return
    
    # Test GPM-Login connection
    try:
        client = GPMClient()
        client.list_profiles(per_page=1)
        print("✓ GPM-Login is running")
    except Exception as e:
        print(f"❌ Cannot connect to GPM-Login: {e}")
        print("Make sure GPM-Login is running on http://127.0.0.1:19995")
        return
    
    # Run automation
    simple_youtube_automation(email, password, search)


if __name__ == "__main__":
    main()
