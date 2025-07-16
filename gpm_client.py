"""
GPM-Login API Client

A Python client for interacting with GPM-Login browser profile management API.
This client provides methods to manage profiles, groups, and browser automation.

Author: mrlaw74
Date: July 16, 2025
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPMClientError(Exception):
    """Custom exception for GPM Client errors"""
    pass


class GPMClient:
    """
    GPM-Login API Client
    
    Provides methods to interact with GPM-Login API for managing browser profiles,
    including creating, listing, opening, and closing profiles.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:19995", timeout: int = 30):
        """
        Initialize GPM Client
        
        Args:
            base_url (str): Base URL of GPM-Login API server
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to GPM API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Dict: API response data
            
        Raises:
            GPMClientError: When API request fails
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Log request details
            logger.debug(f"{method} {url} - Status: {response.status_code}")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise GPMClientError(f"Invalid JSON response: {response.text}")
            
            # Check if request was successful
            if not data.get('success', False):
                message = data.get('message', 'Unknown error')
                raise GPMClientError(f"API Error: {message}")
            
            return data
            
        except requests.RequestException as e:
            raise GPMClientError(f"Request failed: {str(e)}")
    
    # Profile Management Methods
    
    def list_profiles(self, 
                     group_id: Optional[str] = None,
                     page: int = 1,
                     per_page: int = 50,
                     sort: int = 0,
                     search: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of profiles
        
        Args:
            group_id (str, optional): Group ID to filter profiles
            page (int): Page number (default: 1)
            per_page (int): Profiles per page (default: 50)
            sort (int): Sort order (0=newest, 1=oldest, 2=A-Z, 3=Z-A)
            search (str, optional): Search keyword for profile name
            
        Returns:
            Dict: Response containing profiles list and pagination info
        """
        params = {
            'page': page,
            'per_page': per_page,
            'sort': sort
        }
        
        if group_id:
            params['group_id'] = group_id
        if search:
            params['search'] = search
        
        return self._make_request('GET', '/api/v3/profiles', params=params)
    
    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get profile information by ID
        
        Args:
            profile_id (str): Profile ID
            
        Returns:
            Dict: Profile information
        """
        return self._make_request('GET', f'/api/v3/profiles/{profile_id}')
    
    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new profile
        
        Args:
            profile_data (Dict): Profile configuration data
            
        Returns:
            Dict: Created profile information
            
        Example:
            profile_data = {
                "profile_name": "Test profile",
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
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        """
        return self._make_request('POST', '/api/v3/profiles/create', json=profile_data)
    
    def start_profile(self, 
                     profile_id: str,
                     additional_args: Optional[str] = None,
                     win_scale: Optional[float] = None,
                     win_pos: Optional[str] = None,
                     win_size: Optional[str] = None) -> Dict[str, Any]:
        """
        Start/Open a profile
        
        Args:
            profile_id (str): Profile ID to start
            additional_args (str, optional): Additional browser startup arguments
            win_scale (float, optional): Window scale (0.0 to 1.0)
            win_pos (str, optional): Window position as "x,y"
            win_size (str, optional): Window size as "width,height"
            
        Returns:
            Dict: Browser connection information including:
                - profile_id: Profile ID
                - browser_location: Path to browser executable
                - remote_debugging_address: Address for remote debugging
                - driver_path: Path to browser driver
        """
        params = {}
        
        if additional_args:
            params['additional_args'] = additional_args
        if win_scale is not None:
            params['win_scale'] = win_scale
        if win_pos:
            params['win_pos'] = win_pos
        if win_size:
            params['win_size'] = win_size
        
        return self._make_request('GET', f'/api/v3/profiles/start/{profile_id}', params=params)
    
    def stop_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Stop/Close a profile
        
        Args:
            profile_id (str): Profile ID to stop
            
        Returns:
            Dict: Response indicating success/failure
        """
        return self._make_request('GET', f'/api/v3/profiles/stop/{profile_id}')
    
    def close_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Close a profile (alternative to stop_profile)
        
        Args:
            profile_id (str): Profile ID to close
            
        Returns:
            Dict: Response indicating success/failure
        """
        return self._make_request('GET', f'/api/v3/profiles/close/{profile_id}')
    
    def update_profile(self, profile_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing profile
        
        Args:
            profile_id (str): Profile ID to update
            update_data (Dict): Profile update data
            
        Returns:
            Dict: Response indicating success/failure
            
        Example:
            update_data = {
                "profile_name": "Updated Profile Name",
                "group_id": 1,
                "raw_proxy": "new.proxy.com:8080:user:pass",
                "startup_urls": "https://google.com, https://facebook.com",
                "note": "Updated profile note",
                "color": "#FF0000",
                "user_agent": "auto",
                "is_noise_canvas": False,
                "is_noise_webgl": False,
                "is_noise_client_rect": False,
                "is_noise_audio_context": True
            }
        """
        return self._make_request('POST', f'/api/v3/profiles/update/{profile_id}', json=update_data)
    
    def delete_profile(self, profile_id: str, mode: int = 2) -> Dict[str, Any]:
        """
        Delete a profile
        
        Args:
            profile_id (str): Profile ID to delete
            mode (int): Deletion mode:
                        1 - Delete only from database
                        2 - Delete from database and storage (default)
            
        Returns:
            Dict: Response indicating success/failure
        """
        params = {'mode': mode}
        return self._make_request('GET', f'/api/v3/profiles/delete/{profile_id}', params=params)
    
    def list_groups(self) -> Dict[str, Any]:
        """
        Get list of profile groups
        
        Returns:
            Dict: Response containing groups list
        """
        return self._make_request('GET', '/api/v3/groups')

    # Utility Methods
    
    def get_profile_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find profile by name
        
        Args:
            name (str): Profile name to search for
            
        Returns:
            Dict or None: Profile data if found, None otherwise
        """
        try:
            response = self.list_profiles(search=name)
            profiles = response.get('data', [])
            
            for profile in profiles:
                if profile.get('name') == name:
                    return profile
            
            return None
            
        except GPMClientError:
            return None
    
    def is_profile_running(self, profile_id: str) -> bool:
        """
        Check if a profile is currently running
        
        Args:
            profile_id (str): Profile ID to check
            
        Returns:
            bool: True if profile is running, False otherwise
        """
        try:
            # Try to get profile status - this would need actual API endpoint
            # For now, we'll return False as this endpoint isn't documented
            return False
        except GPMClientError:
            return False
    
    def create_default_profile(self, 
                             name: str, 
                             group_name: str = "All",
                             proxy: str = "",
                             os: str = "Windows 11") -> Dict[str, Any]:
        """
        Create a profile with default settings
        
        Args:
            name (str): Profile name
            group_name (str): Group name (default: "All")
            proxy (str): Proxy configuration (default: no proxy)
            os (str): Operating system (default: "Windows 11")
            
        Returns:
            Dict: Created profile information
        """
        default_profile = {
            "profile_name": name,
            "group_name": group_name,
            "browser_core": "chromium",
            "browser_name": "Chrome",
            "browser_version": "119.0.6045.124",
            "is_random_browser_version": False,
            "raw_proxy": proxy,
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
            "os": os,
            "webrtc_mode": 2,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }
        
        return self.create_profile(default_profile)
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """
        Get list of all groups
        
        Returns:
            List: List of group data
        """
        try:
            response = self.list_groups()
            return response.get('data', [])
        except GPMClientError:
            return []
    
    def get_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find group by name
        
        Args:
            name (str): Group name to search for
            
        Returns:
            Dict or None: Group data if found, None otherwise
        """
        groups = self.get_groups()
        for group in groups:
            if group.get('name') == name:
                return group
        return None
    
    def update_profile_proxy(self, profile_id: str, proxy: str) -> Dict[str, Any]:
        """
        Update only the proxy setting of a profile
        
        Args:
            profile_id (str): Profile ID to update
            proxy (str): New proxy configuration
            
        Returns:
            Dict: Update response
        """
        return self.update_profile(profile_id, {"raw_proxy": proxy})
    
    def update_profile_name(self, profile_id: str, name: str) -> Dict[str, Any]:
        """
        Update only the name of a profile
        
        Args:
            profile_id (str): Profile ID to update
            name (str): New profile name
            
        Returns:
            Dict: Update response
        """
        return self.update_profile(profile_id, {"profile_name": name})


# Context Manager for Profile Sessions
class GPMProfileSession:
    """
    Context manager for GPM profile sessions
    
    Automatically starts a profile on enter and stops it on exit.
    """
    
    def __init__(self, client: GPMClient, profile_id: str, **start_kwargs):
        """
        Initialize profile session
        
        Args:
            client (GPMClient): GPM client instance
            profile_id (str): Profile ID to manage
            **start_kwargs: Additional arguments for profile start
        """
        self.client = client
        self.profile_id = profile_id
        self.start_kwargs = start_kwargs
        self.profile_info = None
    
    def __enter__(self):
        """Start the profile and return connection info"""
        try:
            self.profile_info = self.client.start_profile(self.profile_id, **self.start_kwargs)
            logger.info(f"Started profile {self.profile_id}")
            return self.profile_info
        except GPMClientError as e:
            logger.error(f"Failed to start profile {self.profile_id}: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the profile"""
        try:
            self.client.stop_profile(self.profile_id)
            logger.info(f"Stopped profile {self.profile_id}")
        except GPMClientError as e:
            logger.error(f"Failed to stop profile {self.profile_id}: {e}")


if __name__ == "__main__":
    # Example usage
    client = GPMClient()
    
    try:
        # List all profiles
        profiles = client.list_profiles()
        print(f"Found {len(profiles['data'])} profiles")
        
        # Create a test profile
        profile_data = {
            "profile_name": "Test Profile",
            "group_name": "All",
            "browser_core": "chromium",
            "browser_name": "Chrome"
        }
        
        new_profile = client.create_profile(profile_data)
        print(f"Created profile: {new_profile['data']['name']}")
        
        # Start the profile
        profile_id = new_profile['data']['id']
        browser_info = client.start_profile(profile_id)
        print(f"Browser started at: {browser_info['data']['remote_debugging_address']}")
        
        # Stop the profile
        client.stop_profile(profile_id)
        print("Profile stopped")
        
    except GPMClientError as e:
        print(f"Error: {e}")
