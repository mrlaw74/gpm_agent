"""
GPM-Login Selenium Automation Helper

Provides helper classes and functions to integrate GPM-Login with Selenium WebDriver
for automated browser tasks.

Author: mrlaw74
Date: July 16, 2025
"""

import time
import logging
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from gpm_client import GPMClient, GPMClientError, GPMProfileSession

logger = logging.getLogger(__name__)


class GPMSeleniumDriver:
    """
    GPM-Login Selenium Driver Integration
    
    Provides seamless integration between GPM-Login profiles and Selenium WebDriver.
    """
    
    def __init__(self, gpm_client: GPMClient):
        """
        Initialize GPM Selenium Driver
        
        Args:
            gpm_client (GPMClient): GPM client instance
        """
        self.gpm_client = gpm_client
        self.driver = None
        self.profile_id = None
        self.profile_info = None
    
    def create_driver_from_profile(self, profile_id: str, **start_kwargs) -> webdriver.Chrome:
        """
        Create Selenium WebDriver from GPM profile
        
        Args:
            profile_id (str): GPM profile ID
            **start_kwargs: Additional arguments for profile start
            
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
            
        Raises:
            GPMClientError: When profile cannot be started
        """
        # Start the profile
        self.profile_info = self.gpm_client.start_profile(profile_id, **start_kwargs)
        data = self.profile_info.get('data', {})
        
        # Extract connection details
        browser_path = data.get('browser_location')
        driver_path = data.get('driver_path')
        debug_address = data.get('remote_debugging_address')
        
        if not all([browser_path, driver_path, debug_address]):
            raise GPMClientError("Missing required browser connection details")
        
        # Configure Chrome options
        chrome_options = ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", debug_address)
        chrome_options.binary_location = browser_path
        
        # Additional Chrome options for better automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Create Chrome service
        service = ChromeService(executable_path=driver_path)
        
        try:
            # Create WebDriver instance
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.profile_id = profile_id
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info(f"Successfully created driver for profile {profile_id}")
            return self.driver
            
        except Exception as e:
            # If driver creation fails, stop the profile
            try:
                self.gpm_client.stop_profile(profile_id)
            except:
                pass
            raise GPMClientError(f"Failed to create WebDriver: {str(e)}")
    
    def close_driver(self):
        """Close the WebDriver and stop the GPM profile"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
        
        if self.profile_id:
            try:
                self.gpm_client.stop_profile(self.profile_id)
                logger.info(f"Profile {self.profile_id} stopped")
            except Exception as e:
                logger.warning(f"Error stopping profile: {e}")
            finally:
                self.profile_id = None
                self.profile_info = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.close_driver()


class GPMAutomationHelper:
    """
    Helper class for common automation tasks with GPM profiles
    """
    
    def __init__(self, gpm_client: GPMClient):
        """
        Initialize automation helper
        
        Args:
            gpm_client (GPMClient): GPM client instance
        """
        self.gpm_client = gpm_client
    
    def run_automation_task(self, 
                           profile_id: str, 
                           task_function,
                           *args, 
                           **kwargs) -> Any:
        """
        Run automation task with automatic profile management
        
        Args:
            profile_id (str): GPM profile ID
            task_function: Function to execute with WebDriver
            *args: Arguments for task function
            **kwargs: Keyword arguments for task function
            
        Returns:
            Any: Result from task function
        """
        with GPMSeleniumDriver(self.gpm_client) as gpm_driver:
            # Create driver from profile
            driver = gmp_driver.create_driver_from_profile(profile_id)
            
            # Execute the task function
            return task_function(driver, *args, **kwargs)
    
    def batch_automation(self, 
                        profile_tasks: list,
                        delay_between_tasks: float = 1.0) -> list:
        """
        Run multiple automation tasks on different profiles
        
        Args:
            profile_tasks (list): List of tuples (profile_id, task_function, args, kwargs)
            delay_between_tasks (float): Delay between tasks in seconds
            
        Returns:
            list: Results from all tasks
        """
        results = []
        
        for i, (profile_id, task_function, args, kwargs) in enumerate(profile_tasks):
            try:
                logger.info(f"Running task {i+1}/{len(profile_tasks)} on profile {profile_id}")
                
                result = self.run_automation_task(profile_id, task_function, *args, **kwargs)
                results.append({
                    'profile_id': profile_id,
                    'success': True,
                    'result': result,
                    'error': None
                })
                
                # Delay between tasks
                if delay_between_tasks > 0 and i < len(profile_tasks) - 1:
                    time.sleep(delay_between_tasks)
                    
            except Exception as e:
                logger.error(f"Task failed for profile {profile_id}: {e}")
                results.append({
                    'profile_id': profile_id,
                    'success': False,
                    'result': None,
                    'error': str(e)
                })
        
        return results


# Example automation tasks
def example_navigate_and_screenshot(driver: webdriver.Chrome, url: str, screenshot_path: str = None):
    """
    Example task: Navigate to URL and take screenshot
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        url (str): URL to navigate to
        screenshot_path (str, optional): Path to save screenshot
        
    Returns:
        dict: Task result with success status and screenshot path
    """
    try:
        # Navigate to URL
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Take screenshot if path provided
        if screenshot_path:
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
        
        return {
            'success': True,
            'url': url,
            'title': driver.title,
            'screenshot': screenshot_path
        }
        
    except Exception as e:
        logger.error(f"Navigation task failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def example_form_fill(driver: webdriver.Chrome, form_data: dict):
    """
    Example task: Fill out a form
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        form_data (dict): Form field data {selector: value}
        
    Returns:
        dict: Task result
    """
    try:
        results = {}
        
        for selector, value in form_data.items():
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Clear and fill field
            element.clear()
            element.send_keys(value)
            results[selector] = 'filled'
            
            logger.info(f"Filled field {selector} with value {value}")
        
        return {
            'success': True,
            'filled_fields': results
        }
        
    except Exception as e:
        logger.error(f"Form fill task failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def example_data_extraction(driver: webdriver.Chrome, selectors: list):
    """
    Example task: Extract data from page elements
    
    Args:
        driver (webdriver.Chrome): WebDriver instance
        selectors (list): List of CSS selectors to extract data from
        
    Returns:
        dict: Extracted data
    """
    try:
        extracted_data = {}
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                extracted_data[selector] = [elem.text for elem in elements]
                logger.info(f"Extracted {len(elements)} elements for selector {selector}")
            except Exception as e:
                logger.warning(f"Failed to extract data for selector {selector}: {e}")
                extracted_data[selector] = []
        
        return {
            'success': True,
            'data': extracted_data
        }
        
    except Exception as e:
        logger.error(f"Data extraction task failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Example usage
    gpm_client = GPMClient()
    automation_helper = GPMAutomationHelper(gpm_client)
    
    try:
        # Get first available profile
        profiles = gpm_client.list_profiles()
        if not profiles['data']:
            print("No profiles found")
            exit(1)
        
        profile_id = profiles['data'][0]['id']
        print(f"Using profile: {profile_id}")
        
        # Example 1: Single automation task
        result = automation_helper.run_automation_task(
            profile_id,
            example_navigate_and_screenshot,
            "https://www.example.com",
            "screenshot.png"
        )
        print(f"Navigation result: {result}")
        
        # Example 2: Batch automation
        tasks = [
            (profile_id, example_navigate_and_screenshot, ("https://www.google.com",), {}),
            (profile_id, example_data_extraction, (["title", "h1"],), {})
        ]
        
        batch_results = automation_helper.batch_automation(tasks)
        print(f"Batch results: {batch_results}")
        
    except GPMClientError as e:
        print(f"GPM Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
