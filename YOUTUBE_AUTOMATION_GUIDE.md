# YouTube Automation Setup Guide

## Quick Start

### 1. Install Dependencies

First, make sure you have Python 3.7+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests selenium undetected-chromedriver
```

### 2. Start GPM-Login

Make sure GPM-Login is running on your computer. The default API endpoint is:
- **URL**: `http://127.0.0.1:19995`
- **Port**: `19995`

### 3. Run the Automation

#### Simple Version (Recommended for beginners):
```bash
python simple_youtube_automation.py
```

#### Advanced Version (Full featured):
```bash
python youtube_automation_flow.py
```

## What You Need

1. **Google Account**: Email and password for signing into Google/YouTube
2. **GPM-Login**: Must be running locally
3. **Internet Connection**: For accessing Google and YouTube

## Automation Flow

The automation will:
1. 🔨 Create a new browser profile with anti-detection settings
2. 🌐 Start the browser 
3. 🔐 Navigate to Google and sign in with your account
4. 📺 Open YouTube
5. 🔍 Search for videos (you can specify what to search for)
6. ▶️ Play the first video in results
7. 🎬 Let the video play for a few seconds
8. 🧹 Clean up the profile

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
Install dependencies:
```bash
pip install requests selenium
```

### "Cannot connect to GPM-Login"
1. Make sure GPM-Login software is running
2. Check that it's running on port 19995
3. Try opening `http://127.0.0.1:19995` in your browser

### "create_profile() got an unexpected keyword argument"
Make sure you're using the latest version of the scripts. The `create_profile()` method requires a dictionary of profile data.

### Browser doesn't start
1. Check that your proxy settings are correct (if using a proxy)
2. Make sure GPM-Login has permission to start browsers
3. Check the GPM-Login logs for any errors

## Example Usage

```python
# Simple automation with custom search
python simple_youtube_automation.py

# When prompted:
# Google Email: your-email@gmail.com
# Google Password: your-password
# YouTube Search: "Python tutorials"
```

## Advanced Configuration

For the advanced script (`youtube_automation_flow.py`), you can customize:

- **Proxy**: Add proxy settings in the script
- **Location**: Change target location (US, UK, DE, JP)
- **Detection Level**: Adjust anti-detection aggressiveness
- **Search Query**: What to search for on YouTube

## Safety Notes

⚠️ **Important**: 
- Use your own Google accounts
- Don't run too many automations simultaneously
- Respect YouTube's terms of service
- Use proxies if running multiple instances

## Files Overview

- `simple_youtube_automation.py` - Easy-to-use basic automation
- `youtube_automation_flow.py` - Advanced automation with full logging
- `gpm_client.py` - GPM-Login API client
- `gpm_selenium.py` - Selenium integration helpers
- `utils.py` - Utility functions

## Support

If you encounter issues:
1. Check this setup guide
2. Look at the error messages carefully
3. Make sure all dependencies are installed
4. Verify GPM-Login is running properly
