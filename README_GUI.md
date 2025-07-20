# GPM-Login Automation GUI Application

A comprehensive graphical user interface for GPM-Login automation featuring YouTube automation, profile management, and advanced anti-detection capabilities.

## 🎬 Features

### Core Functionality
- **YouTube Automation**: Complete workflow from profile creation to video playback
- **Profile Management**: Create, start, stop, and manage GPM profiles
- **Google Sign-in**: Automated Google account authentication
- **Batch Operations**: Manage multiple profiles simultaneously
- **Fingerprint Protection**: Advanced anti-detection with 13-category protection
- **Settings Management**: Customizable configuration and preferences
- **Reports & Logs**: Comprehensive logging and reporting system

### User Interface
- **Modern GUI**: Clean, intuitive interface built with tkinter
- **Real-time Monitoring**: Live logs and status updates
- **Context Menus**: Right-click operations for profiles
- **Quick Actions**: Dashboard with one-click common operations
- **Multi-threaded**: Non-blocking operations for smooth experience

## 🚀 Quick Start

### Method 1: Using the Launcher (Recommended)
```bash
python launch_gui.py
```

The launcher will:
- Check all dependencies
- Verify project files
- Install missing packages automatically
- Test GPM-Login connection
- Launch the GUI application

### Method 2: Direct Launch
```bash
python gpm_automation_gui.py
```

## 📋 Requirements

### System Requirements
- Windows 10/11 (primary), macOS, or Linux
- Python 3.9 or higher
- GPM-Login application installed and running
- Chrome browser installed

### Python Dependencies
- `tkinter` (usually included with Python)
- `requests`
- `selenium`

### Project Files
- `gpm_client.py` - GPM-Login API client
- `gpm_selenium.py` - Selenium integration
- `utils.py` - Utility functions
- `gpm_automation_gui.py` - Main GUI application
- `launch_gui.py` - Launcher script

## 🎯 Usage Guide

### 1. Dashboard
The main dashboard provides:
- Welcome information and feature overview
- Quick action buttons for common tasks
- Real-time statistics
- Connection status monitoring

### 2. YouTube Automation
Complete YouTube automation workflow:

1. **Navigate to YouTube Automation** from the sidebar
2. **Enter credentials**: Google email and password
3. **Set search query**: What to search for on YouTube
4. **Configure options**: 
   - Auto cleanup after completion
   - Take screenshot of video
   - Keep browser open after automation
5. **Click "Start YouTube Automation"**
6. **Monitor progress** in the real-time log

### 3. Profile Management
Comprehensive profile management:

- **View all profiles** in a sortable table
- **Create new profiles** with custom settings
- **Right-click context menu** for quick actions:
  - Start/Stop profiles
  - YouTube automation
  - Edit profile settings
  - Delete profiles
- **Bulk operations** for multiple profiles

### 4. Settings
Customize the application:

- **GPM-Login Connection**: Configure API URL and test connection
- **Automation Settings**: Set default behaviors
- **Logging Options**: Control log verbosity and storage

### 5. Fingerprint Tools
Advanced anti-detection features:

- **Information** about 13-category fingerprint protection
- **Testing tools** with links to fingerprint test websites
- **Automatic protection** for all created profiles

### 6. Reports & Logs
Monitor and analyze activities:

- **Real-time log viewer** showing recent activities
- **Generate reports** in JSON format
- **Open logs folder** for detailed analysis
- **Clear old logs** to manage disk space

## 🛡️ Fingerprint Protection

The application includes advanced fingerprint protection covering:

1. **User-Agent and Browser Headers**
2. **Screen Resolution and Color Depth**
3. **Timezone and Language Settings**
4. **Canvas and WebGL Fingerprinting**
5. **Audio Context Fingerprinting**
6. **Font Detection and Rendering**
7. **Hardware Specifications**
8. **Network and Connection Info**
9. **Plugin and Extension Detection**
10. **Behavioral Patterns**
11. **Geolocation Data**
12. **Clipboard and Storage Access**
13. **Performance Metrics**

## 🔧 Configuration

### GPM-Login Setup
1. Ensure GPM-Login is running on `http://127.0.0.1:19995`
2. Test connection in Settings → GPM-Login Connection
3. Adjust API URL if using custom port/host

### Automation Settings
- **Auto cleanup**: Automatically stop profiles after automation
- **Save logs**: Store detailed logs to files
- **Show warnings**: Display urllib3 connection warnings

## 📊 Monitoring & Debugging

### Real-time Logs
All operations show real-time progress in the GUI logs:
- Profile creation and management
- YouTube automation steps
- Error messages and warnings
- Connection status updates

### File Logs
Detailed logs are saved to the `logs/` directory:
- Timestamped entries
- Complete operation details
- Error stack traces
- Performance metrics

### Reports
Generate comprehensive reports including:
- Profile statistics
- Automation results
- Connection status
- Application metadata

## ⚡ Keyboard Shortcuts

- **F5**: Refresh current view
- **Ctrl+Q**: Quit application
- **Ctrl+S**: Save settings
- **Ctrl+C**: Stop running automation

## 🔍 Troubleshooting

### Connection Issues
- Ensure GPM-Login is running on port 19995
- Check Windows Firewall settings
- Try restarting GPM-Login application
- Verify API URL in Settings

### Profile Issues
- Use "Cleanup All" if profiles are stuck
- Check available system resources
- Verify proxy settings if using proxies
- Restart GPM-Login if needed

### Browser Issues
- Chrome compatibility issues are automatically handled
- Check Chrome browser installation
- Try creating a new profile if issues persist
- Verify Chrome is not running in background

### Automation Issues
- Verify Google account credentials
- Check internet connection stability
- Use simpler search terms if needed
- Monitor logs for specific error messages

## 📁 File Structure

```
gpm_agent/
├── gpm_automation_gui.py      # Main GUI application
├── launch_gui.py              # Launcher script
├── gpm_client.py              # GPM-Login API client
├── gpm_selenium.py            # Selenium integration
├── utils.py                   # Utility functions
├── gpm_automation_settings.json  # Settings file (created automatically)
├── logs/                      # Log files directory
└── README_GUI.md             # This file
```

## 🆕 Version History

### v1.1.0 (Current)
- Complete GUI application with all features
- YouTube automation workflow
- Profile management interface
- Fingerprint protection tools
- Reports and logging system
- Settings management
- Cross-platform launcher

### v1.0.0
- Initial command-line tools
- Basic GPM-Login integration
- Selenium automation
- YouTube automation scripts

## 👨‍💻 Author

**mrlaw74**
- GitHub: [mrlaw74](https://github.com/mrlaw74)
- Project: GPM-Login Automation Suite
- Date: July 20, 2025

## 📝 License

This project is developed for educational and automation purposes. Please ensure compliance with YouTube's Terms of Service and applicable laws when using automation features.

## 🔗 Links

- **GPM-Login**: Official GPM browser manager
- **Selenium**: Web automation framework
- **YouTube**: Video platform (use responsibly)

---

**Note**: This application requires GPM-Login to be installed and running. Ensure you have proper licensing for GPM-Login before using this automation suite.
