# GPM-Login Python Agent

A comprehensive Python client and automation framework for GPM-Login browser profile management. This agent provides easy-to-use APIs for managing browser profiles, integrating with Selenium for automation, and performing batch operations.

## Features

- **Complete API Coverage**: All GPM-Login API endpoints are supported
- **Profile Management**: Create, list, start, stop, and delete browser profiles
- **Selenium Integration**: Seamless integration with Selenium WebDriver
- **Automation Helpers**: Built-in functions for common automation tasks
- **Context Managers**: Automatic resource management for profiles and drivers
- **Batch Operations**: Run automation tasks across multiple profiles
- **Error Handling**: Comprehensive error handling and logging
- **Type Hints**: Full type annotations for better IDE support
- **Fingerprint Protection**: Advanced anti-detection profile optimization
- **Proxy Assessment**: Quality evaluation for different proxy types
- **Consistency Validation**: Fingerprint consistency checking
- **🎬 YouTube Automation**: Complete automation workflow from profile creation to video playback
- **🔐 Google Sign-in**: Automated Google account authentication
- **🛡️ Anti-Detection**: Advanced fingerprinting and bot detection avoidance

## Requirements

- Python 3.7+
- GPM-Login software running on localhost (default port 19995)
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd gpm_agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Make sure GPM-Login is running on your system with API enabled.

## Quick Start

### Basic Profile Management

```python
from gpm_client import GPMClient

# Initialize client
client = GPMClient(base_url="http://127.0.0.1:19995")

# List all profiles
profiles = client.list_profiles()
print(f"Found {len(profiles['data'])} profiles")

# Create a new profile
profile_data = {
    "profile_name": "My Test Profile",
    "group_name": "Test Group",
    "browser_core": "chromium",
    "browser_name": "Chrome",
    "os": "Windows 11"
}
new_profile = client.create_profile(profile_data)

# Start the profile
profile_id = new_profile['data']['id']
browser_info = client.start_profile(profile_id)
print(f"Browser started: {browser_info['data']['remote_debugging_address']}")

# Stop the profile
client.stop_profile(profile_id)
```

### Fingerprint-Optimized Profile Creation

```python
from gpm_client import GPMClient

client = GPMClient()

# Create profile optimized for specific location and detection level
profile = client.create_fingerprint_optimized_profile(
    name="US E-commerce Profile",
    proxy="us.residential.proxy.com:8080:user:pass",
    location="US",
    detection_level="balanced"  # conservative, balanced, aggressive
)

# Validate fingerprint consistency
validation = client.validate_fingerprint_consistency(profile_data)
if not validation['valid']:
    print("Fingerprint issues detected:")
    for warning in validation['warnings']:
        print(f"⚠ {warning}")
```

### Selenium Integration

```python
from gpm_client import GPMClient
from gpm_selenium import GPMSeleniumDriver

client = GPMClient()

# Automatic browser management
with GPMSeleniumDriver(client) as gpm_driver:
    # Create WebDriver from GPM profile
    driver = gpm_driver.create_driver_from_profile(profile_id)
    
    # Use driver normally
    driver.get("https://www.example.com")
    print(f"Page title: {driver.title}")
    
    # Driver and profile automatically closed when exiting context
```

### Automation Helper

```python
from gpm_client import GPMClient
from gpm_selenium import GPMAutomationHelper

def my_automation_task(driver, url):
    driver.get(url)
    return {"title": driver.title, "url": driver.current_url}

client = GPMClient()
helper = GPMAutomationHelper(client)

# Run task with automatic profile/driver management
result = helper.run_automation_task(profile_id, my_automation_task, "https://www.google.com")
print(result)
```

### YouTube Automation Example

```python
from gpm_client import GPMClient
from gpm_selenium import GPMAutomationHelper

client = GPMClient()

# Define a YouTube automation task
def youtube_automation_task(driver, video_url):
    driver.get(video_url)
    # Add more automation steps as needed
    return {"title": driver.title, "url": driver.current_url}

helper = GPMAutomationHelper(client)

# Run YouTube automation with profile and driver management
result = helper.run_automation_task(profile_id, youtube_automation_task, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
print(result)
```

### 🎬 YouTube Automation (New!)

Complete automation flow from profile creation to video playback:

```python
# Simple YouTube automation
from simple_youtube_automation import simple_youtube_automation

# Run complete automation flow
simple_youtube_automation(
    email="your-email@gmail.com",
    password="your-password", 
    video_search="Python tutorials"
)
```

**Advanced YouTube automation with full logging:**

```python
from youtube_automation_flow import YouTubeAutomationFlow

# Initialize automation
automation = YouTubeAutomationFlow(
    proxy="proxy.server.com:8080:user:pass",  # Optional
    location="US"  # Target location
)

# Run complete flow
results = automation.run_complete_flow(
    email="your-email@gmail.com",
    password="your-password",
    search_query="Python programming tutorial"
)

# Check results
print(f"Automation success: {results['video_playback']['success']}")
```

**What the automation does:**
1. 🔨 Creates optimized browser profile with anti-detection
2. 🌐 Starts browser session with Selenium
3. 🔐 Signs into Google account
4. 📺 Navigates to YouTube
5. 🔍 Searches for videos
6. ▶️ Plays first video in results
7. 🧹 Cleans up resources

### 🚀 Quick YouTube Demo

Want to see how it works without running it? Try the demo:

```bash
python youtube_automation_demo.py
```

## 🧹 Cleanup Behavior

**Normal cleanup warnings**: During cleanup, you may see urllib3 connection warnings like:
```
WARNING:urllib3.connectionpool:Retrying... Failed to establish a new connection
```

**These warnings are completely normal** and indicate that:
- ✅ The browser session is being properly terminated
- ✅ The WebDriver is correctly disconnecting
- ✅ All resources are being cleaned up as expected

The warnings occur because Selenium tries to send final commands to a browser that's already closing. This is expected behavior and not an error.

### Available Automation Scripts:

1. **`simple_youtube_automation.py`** - Basic automation, automatic cleanup
2. **`improved_youtube_automation.py`** - Advanced with cleanup options  
3. **`clean_youtube_automation.py`** - Optimized for minimal warning output
4. **`youtube_automation_demo.py`** - Demo mode (no actual automation)

## 📁 Project Structure

```
gpm_agent/
├── gpm_client.py                    # Core GPM-Login API client
├── gpm_selenium.py                  # Selenium WebDriver integration  
├── utils.py                         # Utility functions and helpers
├── examples.py                      # Basic usage examples
├── batch_automation.py              # Parallel processing examples
├── test_agent.py                   # Comprehensive test suite
├── setup.py                        # Installation automation
├── requirements.txt                # Python dependencies
├── README.md                       # Main documentation
├── PROJECT_STRUCTURE.md            # Architecture overview
├── FINGERPRINTING_GUIDE.md         # Fingerprint protection guide
├── fingerprint_examples.py         # Advanced anti-detection examples
├── 🎬 YOUTUBE AUTOMATION FILES 🎬
├── youtube_automation_flow.py       # Complete YouTube automation workflow
├── simple_youtube_automation.py    # Easy-to-use YouTube automation
├── youtube_automation_demo.py       # Demo showing workflow steps
└── YOUTUBE_AUTOMATION_GUIDE.md     # YouTube automation setup guide
```

## API Reference

### GPMClient Class

The main client class for interacting with GPM-Login API.

#### Methods

- `list_profiles(group_id=None, page=1, per_page=50, sort=0, search=None)` - Get list of profiles
- `get_profile(profile_id)` - Get profile information by ID
- `create_profile(profile_data)` - Create a new profile
- `start_profile(profile_id, **kwargs)` - Start/open a profile
- `stop_profile(profile_id)` - Stop/close a profile
- `delete_profile(profile_id)` - Delete a profile
- `get_profile_by_name(name)` - Find profile by name
- `create_default_profile(name, group_name="All", proxy="", os="Windows 11")` - Create profile with defaults

### Profile Data Structure

When creating profiles, use this structure:

```python
profile_data = {
    "profile_name": "Profile Name",           # Required
    "group_name": "Group Name",               # Optional
    "browser_core": "chromium",               # chromium or firefox
    "browser_name": "Chrome",                 # Chrome or Firefox
    "browser_version": "119.0.6045.124",     # Specific version
    "is_random_browser_version": False,       # Random version
    "raw_proxy": "",                          # Proxy configuration
    "startup_urls": "",                       # Comma-separated URLs
    "is_masked_font": True,                   # Font masking
    "is_noise_canvas": False,                 # Canvas noise
    "is_noise_webgl": False,                  # WebGL noise
    "is_noise_client_rect": False,            # Client rect noise
    "is_noise_audio_context": True,           # Audio context noise
    "is_random_screen": False,                # Random screen resolution
    "is_masked_webgl_data": True,             # WebGL data masking
    "is_masked_media_device": True,           # Media device masking
    "is_random_os": False,                    # Random OS
    "os": "Windows 11",                       # Operating system
    "webrtc_mode": 2,                         # 1=Off, 2=Base on IP
    "user_agent": "Mozilla/5.0 ..."          # Custom user agent
}
```

### Proxy Configuration

GPM-Login supports various proxy types:

```python
# HTTP Proxy
"raw_proxy": "IP:Port:Username:Password"

# SOCKS5 Proxy  
"raw_proxy": "socks5://IP:Port:Username:Password"

# TMProxy
"raw_proxy": "tm://API_KEY|True"

# TinProxy
"raw_proxy": "tin://API_KEY|False"

# TinsoftProxy
"raw_proxy": "tinsoft://API_KEY|True"
```

## Examples

Run the included examples to see the agent in action:

```bash
python examples.py
```

This will demonstrate:
- Basic profile operations
- Profile session management
- Search and filtering
- Proxy configurations

## Selenium Integration Features

### GPMSeleniumDriver

Provides seamless integration between GPM profiles and Selenium WebDriver:

- Automatic browser configuration from GPM profile
- Anti-detection measures built-in
- Context manager for resource cleanup
- Support for both Chrome and Firefox profiles

### GPMAutomationHelper

Helper class for common automation patterns:

- Single task execution with automatic cleanup
- Batch processing across multiple profiles
- Error handling and result collection
- Configurable delays between tasks

### Example Automation Tasks

The package includes example automation functions:

- `example_navigate_and_screenshot()` - Navigate to URL and capture screenshot
- `example_form_fill()` - Fill out web forms
- `example_data_extraction()` - Extract data from page elements

## Error Handling

The agent includes comprehensive error handling:

```python
from gpm_client import GPMClientError

try:
    client = GPMClient()
    profiles = client.list_profiles()
except GPMClientError as e:
    print(f"GPM API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Logging

The agent uses Python's logging module. Configure logging level as needed:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Use Context Managers**: Always use `GPMProfileSession` or `GPMSeleniumDriver` context managers to ensure proper cleanup.

2. **Handle Errors**: Wrap API calls in try-catch blocks to handle connection issues gracefully.

3. **Batch Operations**: Use `GPMAutomationHelper.batch_automation()` for processing multiple profiles efficiently.

4. **Resource Management**: Always stop profiles when done to free up system resources.

5. **Proxy Rotation**: Use different profiles with different proxies for better anonymity.

## Troubleshooting

### Common Issues

1. **"GPM-Login API is not accessible"**
   - Make sure GPM-Login is running
   - Check that API is enabled in GPM-Login settings
   - Verify the base URL (default: http://127.0.0.1:19995)

2. **"Import errors for selenium"**
   - Run `pip install -r requirements.txt` to install dependencies
   - Make sure you're using the correct Python environment

3. **"Failed to create WebDriver"**
   - Ensure the profile started successfully
   - Check that browser paths are valid
   - Verify driver compatibility with browser version

4. **"Profile failed to start"**
   - Check if profile already running
   - Verify proxy configuration if using proxies
   - Check available system resources

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

client = GPMClient()
# All API calls will now show detailed debug information
```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this agent.

## License

This project is provided as-is for educational and automation purposes. Please ensure compliance with websites' terms of service when using for automation.

## Author

Created by: **mrlaw74**

## Changelog

### Version 1.1.0 (July 17, 2025)
- 🎬 **YouTube Automation**: Complete automation workflow
- 🔐 **Google Sign-in**: Automated authentication flow
- 🛡️ **Enhanced Anti-Detection**: Advanced fingerprint protection
- 📺 **Video Playback**: Automated YouTube video interaction
- 🔍 **Smart Search**: Intelligent video search and selection
- 📊 **Detailed Reporting**: Comprehensive automation reports
- 🚀 **Demo Mode**: Interactive workflow demonstration
- 📚 **Setup Guide**: Complete YouTube automation documentation

### Version 1.0.0 (July 16, 2025)
- Initial release
- Complete GPM-Login API coverage
- Selenium integration
- Automation helpers
- Context managers
- Example scripts
- Comprehensive documentation
