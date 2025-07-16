"""
Setup script for GPM-Login Python Agent

This script helps set up the environment and install dependencies.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr.strip()}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        print("Python 3.7+ is required")
        return False


def install_dependencies():
    """Install required Python packages"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    )


def test_imports():
    """Test if all imports work correctly"""
    print("\nTesting imports...")
    try:
        import requests
        print("✓ requests imported successfully")
        
        try:
            from selenium import webdriver
            print("✓ selenium imported successfully")
        except ImportError:
            print("✗ selenium import failed")
            return False
            
        # Test our modules
        from gpm_client import GPMClient
        print("✓ gpm_client imported successfully")
        
        from gpm_selenium import GPMSeleniumDriver
        print("✓ gpm_selenium imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_gpm_connection():
    """Test connection to GPM-Login API"""
    print("\nTesting GPM-Login connection...")
    try:
        from gpm_client import GPMClient
        client = GPMClient()
        
        # Try to list profiles
        response = client.list_profiles(per_page=1)
        print("✓ GPM-Login API is accessible")
        print(f"  Found {response.get('pagination', {}).get('total', 0)} total profiles")
        return True
        
    except Exception as e:
        print("✗ GPM-Login API is not accessible")
        print(f"  Error: {e}")
        print("  Make sure GPM-Login is running on http://127.0.0.1:19995")
        return False


def create_example_config():
    """Create example configuration file"""
    config_content = """# GPM-Login Agent Configuration
# Copy this file to config.py and modify as needed

# GPM-Login API Configuration
GPM_BASE_URL = "http://127.0.0.1:19995"
GPM_TIMEOUT = 30

# Default Profile Settings
DEFAULT_BROWSER_CORE = "chromium"
DEFAULT_BROWSER_NAME = "Chrome"
DEFAULT_BROWSER_VERSION = "119.0.6045.124"
DEFAULT_OS = "Windows 11"
DEFAULT_GROUP_NAME = "Python Agent"

# Automation Settings
AUTOMATION_DELAY = 1.0  # Delay between batch operations (seconds)
SCREENSHOT_DIR = "screenshots"
DEFAULT_WINDOW_SCALE = 0.8

# Proxy Settings (examples)
PROXY_EXAMPLES = {
    "http": "IP:Port:Username:Password",
    "socks5": "socks5://IP:Port:Username:Password", 
    "tmproxy": "tm://API_KEY|True",
    "tinproxy": "tin://API_KEY|False",
    "tinsoftproxy": "tinsoft://API_KEY|True"
}

# Logging Configuration
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""
    
    try:
        with open("config_example.py", "w") as f:
            f.write(config_content)
        print("✓ Example configuration file created: config_example.py")
        return True
    except Exception as e:
        print(f"✗ Failed to create config file: {e}")
        return False


def main():
    """Main setup function"""
    print("GPM-Login Python Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("\nTrying to upgrade pip and retry...")
        run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
        if not install_dependencies():
            return False
    
    # Test imports
    if not test_imports():
        return False
    
    # Create example config
    create_example_config()
    
    # Test GPM connection (optional)
    test_gpm_connection()
    
    print("\n" + "=" * 40)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Make sure GPM-Login is running")
    print("2. Review config_example.py and copy to config.py if needed")
    print("3. Run: python examples.py")
    print("4. Check out the README.md for detailed usage")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during setup: {e}")
        sys.exit(1)
