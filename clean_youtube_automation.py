"""
Clean YouTube Automation - Optimized for Clean Output

This version provides clean output without connection warnings during cleanup.

Author: mrlaw74
Date: July 17, 2025
"""

import sys
import os
import time
import logging
import warnings

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient
from gpm_selenium import GPMSeleniumDriver

# Import Selenium with error handling
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
except ImportError as e:
    print("❌ Selenium is not installed!")
    print("Please install it with: pip install selenium")
    sys.exit(1)

# Setup clean logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Suppress urllib3 warnings during cleanup
warnings.filterwarnings("ignore", message=".*Failed to establish a new connection.*")
warnings.filterwarnings("ignore", message=".*Connection broken.*")


def clean_youtube_automation(email: str, password: str, video_search: str = "Python tutorial"):
    """
    Clean YouTube automation with minimal output noise
    
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
        profile = gpm_client.create_profile(profile_data)
        profile_id = profile['data']['id']
        logger.info(f"✓ Profile created: {profile_id}")
        
        # 2. Start profile and create browser
        logger.info("🌐 Starting browser...")
        with GPMSeleniumDriver(gpm_client) as gpm_driver:
            # Suppress urllib3 logging during driver operations
            logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
            
            driver = gpm_driver.create_driver_from_profile(profile_id)
            logger.info("✓ Browser started")
            
            # 3. Go to Google and sign in
            logger.info("🔐 Signing into Google...")
            driver.get("https://accounts.google.com/signin")
            time.sleep(5)
            
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
            time.sleep(5)
            
            # Enter password
            password_input = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
            )
            time.sleep(2)
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
                "input[name='search_query']",
                "input#search",
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
            time.sleep(10)
            
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
            
            # User choice for cleanup
            print(f"\n📺 Currently playing: {video_title}")
            print("\nChoose what to do next:")
            print("1. ⏸️  Close everything immediately")
            print("2. ⏯️  Keep watching (browser stays open)")
            print("3. 🔄 Run another search")
            
            choice = input("\nEnter choice (1-3, or just press Enter for option 1): ").strip()
            
            if choice == "2":
                print("\n🎬 Browser will stay open. You can close it manually.")
                print(f"📋 Profile ID: {profile_id}")
                print("💡 Tip: You can stop the profile later from GPM-Login interface")
                input("\nPress Enter when you want to stop the profile...")
                
            elif choice == "3":
                new_search = input("\n🔍 Enter new search term: ").strip()
                if new_search:
                    # Go back to YouTube home and search again
                    driver.get("https://www.youtube.com")
                    time.sleep(2)
                    
                    # Find search box again
                    for selector in search_selectors:
                        try:
                            search_box = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            break
                        except:
                            continue
                    
                    if search_box:
                        search_box.clear()
                        search_box.send_keys(new_search)
                        search_box.send_keys(Keys.RETURN)
                        time.sleep(3)
                        
                        # Click first video
                        try:
                            first_video = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
                            )
                            new_title = first_video.get_attribute("title")
                            logger.info(f"Now playing: {new_title}")
                            first_video.click()
                            time.sleep(5)
                            
                            input(f"\n🎵 Now watching: {new_title}\nPress Enter to close browser...")
                        except:
                            logger.warning("Could not play new video")
                            input("Press Enter to close browser...")
            
            # Default: Clean exit
            logger.info("🧹 Closing browser and cleaning up...")
            
        # Context manager handles cleanup automatically
        logger.info("✅ All resources cleaned up successfully!")
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Automation interrupted by user")
        if profile_id:
            try:
                gpm_client.stop_profile(profile_id)
                logger.info("🧹 Profile stopped")
            except:
                pass
                
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        if profile_id:
            try:
                gpm_client.stop_profile(profile_id)
                logger.info("🧹 Profile stopped during error handling")
            except:
                pass


def main():
    """Main function"""
    print("🎬 Clean YouTube Automation with GPM-Login")
    print("=" * 50)
    
    # Get user input
    email = input("📧 Google Email: ").strip()
    password = input("🔐 Google Password: ").strip()
    search = input("🔍 YouTube Search (default: Python tutorial): ").strip()
    
    if not search:
        search = "Python tutorial"
    
    if not email or not password:
        print("❌ Email and password are required!")
        return
    
    # Test GPM-Login connection
    try:
        client = GPMClient()
        client.list_profiles(per_page=1)
        print("✅ GPM-Login is running")
        print()
    except Exception as e:
        print(f"❌ Cannot connect to GPM-Login: {e}")
        print("Make sure GPM-Login is running on http://127.0.0.1:19995")
        return
    
    # Run automation
    clean_youtube_automation(email, password, search)


if __name__ == "__main__":
    main()
