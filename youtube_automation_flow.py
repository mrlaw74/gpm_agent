"""
Complete Automation Flow: Profile Creation to YouTube Video Playback

This script demonstrates a full automation workflow:
1. Create a new GPM profile with fingerprint protection
2. Start the profile and launch browser
3. Navigate to Google.com and sign in
4. Open YouTube and play a video
5. Clean up resources

Author: mrlaw74
Date: July 17, 2025
"""

import sys
import os
import time
import logging
import random
from typing import Optional, Dict, Any

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gpm_client import GPMClient, GPMClientError, GPMProfileSession
from gpm_selenium import GPMSeleniumDriver, GPMAutomationHelper

# Import Selenium with error handling
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError as e:
    print("❌ Selenium is not installed!")
    print("Please install it with: pip install selenium")
    sys.exit(1)

from utils import setup_logging, save_json_report, random_delay

# Configure logging
setup_logging("INFO")
logger = logging.getLogger(__name__)


class YouTubeAutomationFlow:
    """Complete automation flow for YouTube interaction"""
    
    def __init__(self, proxy: str = "", location: str = "US"):
        """
        Initialize automation flow
        
        Args:
            proxy (str): Proxy configuration
            location (str): Target location for profile
        """
        self.gpm_client = GPMClient()
        self.profile_id = None
        self.profile_name = None
        self.automation_helper = GPMAutomationHelper(self.gpm_client)
        self.proxy = proxy
        self.location = location
        
        # Results tracking
        self.results = {
            "profile_creation": None,
            "profile_start": None,
            "google_navigation": None,
            "google_signin": None,
            "youtube_navigation": None,
            "video_playback": None,
            "cleanup": None,
            "start_time": time.time(),
            "end_time": None
        }
    
    def create_optimized_profile(self) -> bool:
        """
        Create a new profile optimized for YouTube automation
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Creating optimized profile for YouTube automation...")
            
            # Create profile with fingerprint protection
            profile = self.gpm_client.create_fingerprint_optimized_profile(
                name=f"YouTube Automation {int(time.time())}",
                proxy=self.proxy,
                location=self.location,
                detection_level="balanced"
            )
            
            self.profile_id = profile['data']['id']
            self.profile_name = profile['data']['name']
            
            logger.info(f"✓ Profile created: {self.profile_name}")
            logger.info(f"  Profile ID: {self.profile_id}")
            
            # Validate fingerprint consistency
            profile_config = {
                "raw_proxy": self.proxy,
                "webrtc_mode": 2 if self.proxy else 1,
                "os": "Windows 11",
                "is_noise_canvas": True,
                "is_noise_audio_context": True
            }
            
            validation = self.gpm_client.validate_fingerprint_consistency(profile_config)
            if not validation['valid']:
                logger.warning("Fingerprint validation warnings detected:")
                for warning in validation['warnings']:
                    logger.warning(f"  ⚠ {warning}")
            
            self.results["profile_creation"] = {
                "success": True,
                "profile_id": self.profile_id,
                "profile_name": self.profile_name,
                "validation": validation
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            self.results["profile_creation"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def google_signin_flow(self, driver, email: str, password: str) -> bool:
        """
        Complete Google sign-in flow
        
        Args:
            driver: Selenium WebDriver instance
            email (str): Google account email
            password (str): Google account password
            
        Returns:
            bool: Success status
        """
        try:
            logger.info("Starting Google sign-in flow...")
            
            # Navigate to Google
            logger.info("Navigating to Google.com...")
            driver.get("https://www.google.com")
            random_delay(2, 4)
            
            # Check if already signed in
            try:
                profile_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ogsr-up]"))
                )
                logger.info("Already signed in to Google")
                self.results["google_signin"] = {"success": True, "already_signed_in": True}
                return True
            except TimeoutException:
                pass
            
            # Click Sign In button
            try:
                signin_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Sign in"))
                )
                signin_button.click()
                logger.info("Clicked Sign In button")
                random_delay(2, 4)
            except TimeoutException:
                # Try alternative sign in button
                try:
                    signin_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='accounts.google.com']"))
                    )
                    signin_button.click()
                    logger.info("Clicked alternative Sign In button")
                    random_delay(2, 4)
                except TimeoutException:
                    logger.error("Could not find Sign In button")
                    return False
            
            # Enter email
            try:
                email_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.ID, "identifierId"))
                )
                email_input.clear()
                
                # Type email with human-like delay
                for char in email:
                    email_input.send_keys(char)
                    time.sleep(0.1 + random.uniform(0, 0.1))
                
                logger.info("Entered email address")
                random_delay(1, 2)
                
                # Click Next
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "identifierNext"))
                )
                next_button.click()
                logger.info("Clicked Next after email")
                random_delay(3, 5)
                
            except TimeoutException:
                logger.error("Could not find email input field")
                return False
            
            # Enter password
            try:
                password_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
                password_input.clear()
                
                # Type password with human-like delay
                for char in password:
                    password_input.send_keys(char)
                    time.sleep(0.1 + random.uniform(0, 0.1))
                
                logger.info("Entered password")
                random_delay(1, 2)
                
                # Click Next
                password_next = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "passwordNext"))
                )
                password_next.click()
                logger.info("Clicked Next after password")
                random_delay(3, 5)
                
            except TimeoutException:
                logger.error("Could not find password input field")
                return False
            
            # Verify sign-in success
            try:
                # Wait for profile icon or account menu
                WebDriverWait(driver, 20).until(
                    lambda d: "accounts.google.com" not in d.current_url
                )
                
                # Check for profile element
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-ogsr-up], [data-ved]"))
                )
                
                logger.info("✓ Google sign-in successful")
                self.results["google_signin"] = {
                    "success": True,
                    "email": email,
                    "signin_time": time.time()
                }
                return True
                
            except TimeoutException:
                logger.error("Sign-in verification failed")
                self.results["google_signin"] = {
                    "success": False,
                    "error": "Sign-in verification timeout"
                }
                return False
                
        except Exception as e:
            logger.error(f"Google sign-in failed: {e}")
            self.results["google_signin"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def youtube_video_flow(self, driver, search_query: str = "Python programming tutorial") -> bool:
        """
        YouTube navigation and video playback flow
        
        Args:
            driver: Selenium WebDriver instance
            search_query (str): Video search query
            
        Returns:
            bool: Success status
        """
        try:
            logger.info("Starting YouTube automation flow...")
            
            # Navigate to YouTube
            logger.info("Navigating to YouTube...")
            driver.get("https://www.youtube.com")
            random_delay(3, 5)
            
            # Handle cookie consent if present
            try:
                accept_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'I agree')]"))
                )
                accept_button.click()
                logger.info("Accepted YouTube cookies")
                random_delay(2, 3)
            except TimeoutException:
                logger.info("No cookie consent dialog found")
            
            # Search for video
            try:
                search_box = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input#search"))
                )
                
                # Clear and type search query
                search_box.clear()
                for char in search_query:
                    search_box.send_keys(char)
                    time.sleep(0.1 + random.uniform(0, 0.05))
                
                logger.info(f"Entered search query: {search_query}")
                random_delay(1, 2)
                
                # Press Enter or click search button
                search_box.send_keys(Keys.RETURN)
                logger.info("Submitted search")
                random_delay(3, 5)
                
            except TimeoutException:
                logger.error("Could not find YouTube search box")
                return False
            
            # Click on first video
            try:
                # Wait for search results
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
                )
                
                # Find and click first video
                first_video = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
                )
                
                video_title = first_video.get_attribute("title") or "Unknown Video"
                logger.info(f"Clicking on video: {video_title}")
                
                first_video.click()
                random_delay(5, 8)
                
            except TimeoutException:
                logger.error("Could not find or click video")
                return False
            
            # Verify video is playing
            try:
                # Wait for video player
                video_player = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
                )
                
                # Check if video is playing
                time.sleep(3)  # Let video start
                
                # Try to get video duration/current time
                current_time = driver.execute_script("return document.querySelector('video').currentTime")
                duration = driver.execute_script("return document.querySelector('video').duration")
                
                if current_time > 0:
                    logger.info(f"✓ Video is playing! Current time: {current_time:.2f}s")
                    
                    # Let video play for a short time
                    logger.info("Letting video play for 10 seconds...")
                    time.sleep(10)
                    
                    # Get updated time to confirm playback
                    new_time = driver.execute_script("return document.querySelector('video').currentTime")
                    
                    if new_time > current_time:
                        logger.info(f"✓ Video playback confirmed! Time progressed to: {new_time:.2f}s")
                        
                        self.results["video_playback"] = {
                            "success": True,
                            "video_title": video_title,
                            "search_query": search_query,
                            "duration": duration,
                            "playback_time": new_time
                        }
                        return True
                    else:
                        logger.warning("Video doesn't seem to be progressing")
                        return False
                else:
                    logger.warning("Video current time is 0")
                    return False
                    
            except TimeoutException:
                logger.error("Could not find video player")
                return False
                
        except Exception as e:
            logger.error(f"YouTube automation failed: {e}")
            self.results["video_playback"] = {
                "success": False,
                "error": str(e)
            }
            return False
    
    def run_complete_flow(self, email: str, password: str, search_query: str = "Python programming tutorial") -> Dict[str, Any]:
        """
        Execute the complete automation flow
        
        Args:
            email (str): Google account email
            password (str): Google account password
            search_query (str): YouTube search query
            
        Returns:
            Dict: Complete results
        """
        logger.info("🚀 Starting complete YouTube automation flow...")
        
        try:
            # Step 1: Create profile
            if not self.create_optimized_profile():
                return self.results
            
            # Step 2: Start profile and create driver
            logger.info("Starting profile and creating browser session...")
            
            with GPMSeleniumDriver(self.gpm_client) as gpm_driver:
                try:
                    # Create driver from profile
                    driver = gpm_driver.create_driver_from_profile(self.profile_id)
                    
                    self.results["profile_start"] = {
                        "success": True,
                        "debug_address": gpm_driver.profile_info['data']['remote_debugging_address']
                    }
                    
                    logger.info("✓ Browser session created successfully")
                    
                    # Step 3: Google sign-in flow
                    self.results["google_navigation"] = {"success": True}
                    if not self.google_signin_flow(driver, email, password):
                        return self.results
                    
                    # Step 4: YouTube automation
                    self.results["youtube_navigation"] = {"success": True}
                    if not self.youtube_video_flow(driver, search_query):
                        return self.results
                    
                    # Success!
                    logger.info("🎉 Complete automation flow successful!")
                    
                    # Optional: Take a screenshot
                    try:
                        screenshot_path = f"youtube_automation_{int(time.time())}.png"
                        driver.save_screenshot(screenshot_path)
                        logger.info(f"Screenshot saved: {screenshot_path}")
                        self.results["screenshot"] = screenshot_path
                    except Exception as e:
                        logger.warning(f"Failed to save screenshot: {e}")
                    
                except Exception as e:
                    logger.error(f"Browser automation failed: {e}")
                    self.results["profile_start"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Step 5: Cleanup
            self.cleanup_profile()
            
        except Exception as e:
            logger.error(f"Complete flow failed: {e}")
            self.results["flow_error"] = str(e)
        
        finally:
            self.results["end_time"] = time.time()
            self.results["total_duration"] = self.results["end_time"] - self.results["start_time"]
        
        return self.results
    
    def cleanup_profile(self):
        """Clean up created profile"""
        try:
            if self.profile_id:
                logger.info("Cleaning up profile...")
                
                # Stop profile if running
                try:
                    self.gpm_client.stop_profile(self.profile_id)
                except:
                    pass
                
                # Optionally delete profile (uncomment if desired)
                # self.gpm_client.delete_profile(self.profile_id)
                # logger.info("Profile deleted")
                
                self.results["cleanup"] = {"success": True}
                logger.info("✓ Profile cleanup completed")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self.results["cleanup"] = {
                "success": False,
                "error": str(e)
            }


def main():
    """Main execution function"""
    print("YouTube Automation Flow with GPM-Login")
    print("=" * 50)
    
    # Configuration
    PROXY = ""  # Add your proxy here: "proxy.server.com:8080:user:pass"
    LOCATION = "US"  # Target location
    EMAIL = input("Enter Google email: ").strip()
    PASSWORD = input("Enter Google password: ").strip()
    SEARCH_QUERY = input("Enter YouTube search query (or press Enter for default): ").strip()
    
    if not SEARCH_QUERY:
        SEARCH_QUERY = "Python programming tutorial"
    
    if not EMAIL or not PASSWORD:
        print("Email and password are required!")
        return
    
    # Verify GPM-Login connection
    try:
        client = GPMClient()
        client.list_profiles(per_page=1)
        print("✓ GPM-Login API is accessible")
    except Exception as e:
        print(f"✗ GPM-Login API is not accessible: {e}")
        print("Please make sure GPM-Login is running on http://127.0.0.1:19995")
        return
    
    # Run automation flow
    automation = YouTubeAutomationFlow(proxy=PROXY, location=LOCATION)
    
    try:
        results = automation.run_complete_flow(EMAIL, PASSWORD, SEARCH_QUERY)
        
        # Generate report
        print("\n" + "=" * 50)
        print("🏁 Automation Flow Results")
        print("=" * 50)
        
        for step, result in results.items():
            if step in ["start_time", "end_time", "total_duration"]:
                continue
                
            if isinstance(result, dict) and "success" in result:
                status = "✓" if result["success"] else "✗"
                print(f"{step.replace('_', ' ').title()}: {status}")
                
                if not result["success"] and "error" in result:
                    print(f"  Error: {result['error']}")
        
        if "total_duration" in results:
            print(f"\nTotal Duration: {results['total_duration']:.2f} seconds")
        
        # Save detailed report
        report_file = f"youtube_automation_report_{int(time.time())}.json"
        save_json_report(results, report_file)
        print(f"\nDetailed report saved: {report_file}")
        
        # Overall success assessment
        success_steps = sum(1 for k, v in results.items() 
                          if isinstance(v, dict) and v.get("success", False))
        total_steps = sum(1 for k, v in results.items() 
                         if isinstance(v, dict) and "success" in v)
        
        if success_steps == total_steps:
            print("\n🎉 All steps completed successfully!")
        else:
            print(f"\n⚠ Completed {success_steps}/{total_steps} steps successfully")
        
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user")
        automation.cleanup_profile()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        automation.cleanup_profile()


if __name__ == "__main__":
    main()
