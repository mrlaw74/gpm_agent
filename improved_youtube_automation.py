"""
Improved YouTube Automation with Better Cleanup

This version provides better control over browser cleanup and profile management.

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

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeAutomation:
    """YouTube automation with better resource management"""
    
    def __init__(self):
        self.gpm_client = GPMClient()
        self.profile_id = None
        self.driver = None
        self.gpm_driver = None
    
    def cleanup(self):
        """Cleanup resources properly"""
        logger.info("🧹 Starting cleanup...")
        
        # Close driver if exists
        if self.driver:
            try:
                # Temporarily suppress urllib3 warnings during cleanup
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                
                self.driver.quit()
                logger.info("  ✓ WebDriver closed")
            except Exception as e:
                # These exceptions are normal during cleanup - don't show them as warnings
                if "No connection could be made" in str(e) or "Connection refused" in str(e):
                    logger.info("  ✓ WebDriver closed (connection already terminated)")
                else:
                    logger.warning(f"  ⚠ WebDriver cleanup warning: {e}")
        
        # Close GPM driver context if exists
        if self.gpm_driver:
            try:
                self.gpm_driver.__exit__(None, None, None)
                logger.info("  ✓ GPM driver context closed")
            except Exception as e:
                logger.warning(f"  ⚠ GPM driver cleanup warning: {e}")
        
        # Stop profile if exists
        if self.profile_id:
            try:
                self.gpm_client.stop_profile(self.profile_id)
                logger.info("  ✓ Profile stopped")
            except Exception as e:
                logger.warning(f"  ⚠ Profile stop warning: {e}")
        
        logger.info("🧹 Cleanup completed successfully")
    
    def create_profile(self):
        """Create a new browser profile"""
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
        
        profile = self.gpm_client.create_profile(profile_data)
        self.profile_id = profile['data']['id']
        logger.info(f"✓ Profile created: {self.profile_id}")
        return self.profile_id
    
    def start_browser(self):
        """Start browser session"""
        logger.info("🌐 Starting browser...")
        
        self.gpm_driver = GPMSeleniumDriver(self.gpm_client)
        self.gpm_driver.__enter__()
        self.driver = self.gpm_driver.create_driver_from_profile(self.profile_id)
        
        logger.info("✓ Browser started")
        return self.driver
    
    def google_signin(self, email, password):
        """Sign into Google account"""
        logger.info("🔐 Signing into Google...")
        
        self.driver.get("https://accounts.google.com/signin")
        time.sleep(5)
        
        # Enter email
        email_input = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.ID, "identifierId"))
        )
        email_input.clear()
        email_input.send_keys(email)
        
        # Click Next
        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "identifierNext"))
        )
        next_button.click()
        time.sleep(5)
        
        # Enter password
        password_input = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']"))
        )
        time.sleep(2)
        password_input.clear()
        password_input.send_keys(password)
        
        # Click Next
        password_next = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "passwordNext"))
        )
        password_next.click()
        time.sleep(5)
        
        logger.info("✓ Signed into Google")
    
    def youtube_automation(self, search_query):
        """YouTube automation flow"""
        logger.info("📺 Opening YouTube...")
        self.driver.get("https://www.youtube.com")
        time.sleep(3)
        
        # Search for video
        logger.info(f"🔍 Searching for: {search_query}")
        
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
                search_box = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Found search box with selector: {selector}")
                break
            except:
                continue
        
        if not search_box:
            raise Exception("Could not find YouTube search box")
        
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Click first video
        logger.info("▶️ Playing first video...")
        first_video = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
        )
        video_title = first_video.get_attribute("title")
        logger.info(f"Playing: {video_title}")
        first_video.click()
        
        # Let video play
        logger.info("🎬 Video is playing...")
        time.sleep(10)
        
        # Check if video is actually playing
        try:
            current_time = self.driver.execute_script("return document.querySelector('video').currentTime")
            if current_time > 0:
                logger.info(f"✓ Confirmed video is playing at {current_time:.1f} seconds")
            else:
                logger.warning("Video may not be playing (currentTime is 0)")
        except Exception as e:
            logger.warning(f"Could not verify video playback: {e}")
        
        return video_title
    
    def run_automation(self, email, password, search_query):
        """Run complete automation with proper cleanup"""
        try:
            # Step 1: Create profile
            self.create_profile()
            
            # Step 2: Start browser
            self.start_browser()
            
            # Step 3: Google sign-in
            self.google_signin(email, password)
            
            # Step 4: YouTube automation
            video_title = self.youtube_automation(search_query)
            
            logger.info("🎉 Automation completed successfully!")
            
            # User interaction
            print(f"\n📺 Currently playing: {video_title}")
            print("Choose an option:")
            print("1. Keep browser open (manual cleanup required)")
            print("2. Close browser and stop profile automatically")
            print("3. Close browser but keep profile running")
            
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                print("Browser will stay open. Remember to manually stop the profile later!")
                print(f"Profile ID: {self.profile_id}")
                return
            elif choice == "3":
                logger.info("Closing browser but keeping profile running...")
                if self.driver:
                    self.driver.quit()
                    self.driver = None
                print(f"Profile {self.profile_id} is still running. Stop it manually if needed.")
                return
            else:
                # Default: full cleanup
                logger.info("Performing full cleanup...")
                self.cleanup()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Automation interrupted by user")
            self.cleanup()
        except Exception as e:
            logger.error(f"❌ Automation failed: {e}")
            import traceback
            traceback.print_exc()
            self.cleanup()


def main():
    """Main function"""
    print("Improved YouTube Automation with GPM-Login")
    print("=" * 50)
    
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
    automation = YouTubeAutomation()
    automation.run_automation(email, password, search)


if __name__ == "__main__":
    main()
