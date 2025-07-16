"""
Utility functions for GPM-Login Python Agent

Common helper functions and utilities for GPM automation tasks.
"""

import os
import json
import time
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None):
    """
    Setup logging configuration
    
    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string (str, optional): Custom format string
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def save_json_report(data: Dict[str, Any], filename: str, pretty: bool = True) -> bool:
    """
    Save data to JSON file
    
    Args:
        data (dict): Data to save
        filename (str): Output filename
        pretty (bool): Use pretty formatting
        
    Returns:
        bool: Success status
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON report to {filename}: {e}")
        return False


def load_json_config(filename: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        filename (str): Config filename
        
    Returns:
        dict: Configuration data
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Config file {filename} not found")
        return {}
    except Exception as e:
        logging.error(f"Failed to load config from {filename}: {e}")
        return {}


def generate_user_agents() -> List[str]:
    """
    Generate list of common user agents
    
    Returns:
        list: User agent strings
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    return user_agents


def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    """
    Add random delay to avoid detection
    
    Args:
        min_seconds (float): Minimum delay
        max_seconds (float): Maximum delay
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def create_directory(path: str) -> bool:
    """
    Create directory if it doesn't exist
    
    Args:
        path (str): Directory path
        
    Returns:
        bool: Success status
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create directory {path}: {e}")
        return False


def format_profile_summary(profile_data: Dict[str, Any]) -> str:
    """
    Format profile data for display
    
    Args:
        profile_data (dict): Profile information
        
    Returns:
        str: Formatted summary
    """
    name = profile_data.get('name', 'Unknown')
    id_short = profile_data.get('id', '')[:8] + '...' if profile_data.get('id') else 'N/A'
    browser = profile_data.get('browser_type', 'Unknown')
    version = profile_data.get('browser_version', 'Unknown')
    proxy = profile_data.get('raw_proxy', '')
    proxy_status = "with proxy" if proxy else "no proxy"
    
    return f"{name} (ID: {id_short}) - {browser} {version} - {proxy_status}"


def validate_proxy_format(proxy_string: str) -> bool:
    """
    Validate proxy string format
    
    Args:
        proxy_string (str): Proxy configuration string
        
    Returns:
        bool: True if format is valid
    """
    if not proxy_string:
        return True  # Empty proxy is valid (no proxy)
    
    # Check different proxy formats
    if proxy_string.startswith('socks5://'):
        return True
    elif proxy_string.startswith('tm://'):
        return True
    elif proxy_string.startswith('tin://'):
        return True
    elif proxy_string.startswith('tinsoft://'):
        return True
    elif ':' in proxy_string:
        # HTTP proxy format IP:Port or IP:Port:User:Pass
        parts = proxy_string.split(':')
        return len(parts) in [2, 4]
    
    return False


def create_profile_batch(count: int, base_name: str = "Batch Profile", **profile_kwargs) -> List[Dict[str, Any]]:
    """
    Create multiple profile configurations
    
    Args:
        count (int): Number of profiles to create
        base_name (str): Base name for profiles
        **profile_kwargs: Additional profile parameters
        
    Returns:
        list: List of profile configurations
    """
    profiles = []
    timestamp = int(time.time())
    
    for i in range(count):
        profile = {
            "profile_name": f"{base_name} {i+1} - {timestamp}",
            "group_name": profile_kwargs.get("group_name", "Batch Profiles"),
            "browser_core": profile_kwargs.get("browser_core", "chromium"),
            "browser_name": profile_kwargs.get("browser_name", "Chrome"),
            "browser_version": profile_kwargs.get("browser_version", "119.0.6045.124"),
            "is_random_browser_version": profile_kwargs.get("is_random_browser_version", False),
            "raw_proxy": profile_kwargs.get("raw_proxy", ""),
            "startup_urls": profile_kwargs.get("startup_urls", ""),
            "is_masked_font": profile_kwargs.get("is_masked_font", True),
            "is_noise_canvas": profile_kwargs.get("is_noise_canvas", False),
            "is_noise_webgl": profile_kwargs.get("is_noise_webgl", False),
            "is_noise_client_rect": profile_kwargs.get("is_noise_client_rect", False),
            "is_noise_audio_context": profile_kwargs.get("is_noise_audio_context", True),
            "is_random_screen": profile_kwargs.get("is_random_screen", False),
            "is_masked_webgl_data": profile_kwargs.get("is_masked_webgl_data", True),
            "is_masked_media_device": profile_kwargs.get("is_masked_media_device", True),
            "is_random_os": profile_kwargs.get("is_random_os", False),
            "os": profile_kwargs.get("os", "Windows 11"),
            "webrtc_mode": profile_kwargs.get("webrtc_mode", 2),
            "user_agent": profile_kwargs.get("user_agent", random.choice(generate_user_agents()))
        }
        profiles.append(profile)
    
    return profiles


def monitor_system_resources() -> Dict[str, Any]:
    """
    Monitor basic system resources
    
    Returns:
        dict: System resource information
    """
    import psutil
    
    try:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            'timestamp': datetime.now().isoformat()
        }
    except ImportError:
        return {
            'error': 'psutil not available',
            'timestamp': datetime.now().isoformat()
        }


def estimate_task_duration(profile_count: int, tasks_per_profile: int, avg_task_time: float = 2.0) -> Dict[str, Any]:
    """
    Estimate batch automation duration
    
    Args:
        profile_count (int): Number of profiles
        tasks_per_profile (int): Tasks per profile
        avg_task_time (float): Average time per task in seconds
        
    Returns:
        dict: Duration estimates
    """
    total_tasks = profile_count * tasks_per_profile
    
    # Sequential execution
    sequential_time = total_tasks * avg_task_time
    
    # Parallel execution (assuming 50% efficiency)
    parallel_time = sequential_time * 0.6
    
    return {
        'total_tasks': total_tasks,
        'sequential_minutes': sequential_time / 60,
        'parallel_minutes': parallel_time / 60,
        'estimated_savings_minutes': (sequential_time - parallel_time) / 60
    }


def assess_proxy_quality(proxy_string: str) -> Dict[str, Any]:
    """
    Assess proxy configuration quality for anti-detection
    
    Args:
        proxy_string (str): Proxy configuration string
        
    Returns:
        Dict: Quality assessment results
    """
    if not proxy_string:
        return {
            "quality": "none",
            "type": "none", 
            "recommendations": ["Consider using proxy for better anonymity"]
        }
    
    quality_scores = {
        "residential": 90,
        "datacenter": 60,
        "socks5": 80,
        "http": 70,
        "tm": 85,
        "tin": 85,
        "tinsoft": 85
    }
    
    recommendations = []
    proxy_type = "unknown"
    quality = 50  # Default score
    
    # Analyze proxy type
    if proxy_string.startswith('socks5://'):
        proxy_type = "socks5"
        quality = quality_scores["socks5"]
        recommendations.append("SOCKS5 provides good protocol support")
    elif proxy_string.startswith('tm://'):
        proxy_type = "tmproxy"
        quality = quality_scores["tm"]
        recommendations.append("TMProxy typically provides residential IPs")
    elif proxy_string.startswith('tin://'):
        proxy_type = "tinproxy"
        quality = quality_scores["tin"]
        recommendations.append("TinProxy service detected")
    elif proxy_string.startswith('tinsoft://'):
        proxy_type = "tinsoftproxy"
        quality = quality_scores["tinsoft"]
        recommendations.append("TinsoftProxy service detected")
    elif ':' in proxy_string:
        proxy_type = "http"
        quality = quality_scores["http"]
        parts = proxy_string.split(':')
        if len(parts) == 4:
            recommendations.append("HTTP proxy with authentication")
        else:
            recommendations.append("HTTP proxy without authentication - less secure")
    
    # Quality recommendations
    if quality >= 85:
        recommendations.append("High-quality proxy configuration")
    elif quality >= 70:
        recommendations.append("Good proxy configuration")
    elif quality >= 60:
        recommendations.append("Moderate proxy - consider upgrading for better protection")
        recommendations.append("Datacenter proxies may be more easily detected")
    else:
        recommendations.append("Low-quality proxy - high detection risk")
        recommendations.append("Consider using residential or mobile proxies")
    
    # Additional recommendations
    if proxy_type in ["tm", "tin", "tinsoft"]:
        recommendations.append("API-based proxy service - ensure proper key management")
    
    if proxy_type == "http":
        recommendations.append("Consider SOCKS5 for better protocol support")
    
    return {
        "quality": quality,
        "type": proxy_type,
        "recommendations": recommendations,
        "risk_level": "low" if quality >= 80 else "medium" if quality >= 60 else "high"
    }


def generate_fingerprint_test_urls() -> Dict[str, str]:
    """
    Generate URLs for testing fingerprint protection
    
    Returns:
        Dict: Test URLs for different fingerprint aspects
    """
    return {
        "canvas": "https://browserleaks.com/canvas",
        "webgl": "https://browserleaks.com/webgl",
        "audio": "https://browserleaks.com/audio",
        "fonts": "https://browserleaks.com/fonts",
        "webrtc": "https://browserleaks.com/webrtc",
        "ip": "https://browserleaks.com/ip",
        "dns": "https://browserleaks.com/dns",
        "geolocation": "https://browserleaks.com/geo",
        "timezone": "https://browserleaks.com/timezone",
        "screen": "https://browserleaks.com/screen",
        "comprehensive": "https://amiunique.org/",
        "advanced": "https://coveryourtracks.eff.org/",
        "webrtc_leak": "https://whatismyip.li/webrtc-leak-test"
    }


def create_fingerprint_test_report(test_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive fingerprint test report
    
    Args:
        test_results (dict): Results from fingerprint tests
        
    Returns:
        Dict: Formatted test report
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": 0,
        "protection_level": "unknown",
        "details": {},
        "recommendations": []
    }
    
    # Scoring system (0-100 for each category)
    category_scores = {}
    
    # Canvas protection assessment
    if "canvas" in test_results:
        canvas_unique = test_results["canvas"].get("unique", True)
        canvas_score = 20 if not canvas_unique else 80  # Lower score for unique canvas
        category_scores["canvas"] = canvas_score
        report["details"]["canvas"] = {
            "score": canvas_score,
            "unique": canvas_unique,
            "status": "protected" if canvas_score >= 70 else "vulnerable"
        }
    
    # WebGL protection assessment  
    if "webgl" in test_results:
        webgl_unique = test_results["webgl"].get("unique", True)
        webgl_score = 20 if not webgl_unique else 80
        category_scores["webgl"] = webgl_score
        report["details"]["webgl"] = {
            "score": webgl_score,
            "unique": webgl_unique,
            "status": "protected" if webgl_score >= 70 else "vulnerable"
        }
    
    # WebRTC leak assessment
    if "webrtc" in test_results:
        ip_leaked = test_results["webrtc"].get("real_ip_detected", False)
        webrtc_score = 20 if ip_leaked else 100
        category_scores["webrtc"] = webrtc_score
        report["details"]["webrtc"] = {
            "score": webrtc_score,
            "ip_leaked": ip_leaked,
            "status": "protected" if not ip_leaked else "vulnerable"
        }
        
        if ip_leaked:
            report["recommendations"].append("WebRTC is leaking real IP - check proxy configuration")
    
    # Overall assessment
    if category_scores:
        report["overall_score"] = sum(category_scores.values()) / len(category_scores)
        
        if report["overall_score"] >= 85:
            report["protection_level"] = "excellent"
        elif report["overall_score"] >= 70:
            report["protection_level"] = "good"
        elif report["overall_score"] >= 50:
            report["protection_level"] = "moderate"
        else:
            report["protection_level"] = "poor"
            report["recommendations"].append("Consider reviewing fingerprint protection settings")
    
    return report


class ProfileManager:
    """Helper class for managing profile operations"""
    
    def __init__(self, client):
        """
        Initialize profile manager
        
        Args:
            client: GPM client instance
        """
        self.client = client
        self.created_profiles = []
    
    def create_profiles(self, configurations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple profiles
        
        Args:
            configurations (list): List of profile configurations
            
        Returns:
            list: Created profile data
        """
        created = []
        
        for i, config in enumerate(configurations):
            try:
                profile = self.client.create_profile(config)
                profile_data = profile['data']
                created.append(profile_data)
                self.created_profiles.append(profile_data)
                
                logging.info(f"Created profile {i+1}/{len(configurations)}: {profile_data['name']}")
                
            except Exception as e:
                logging.error(f"Failed to create profile {i+1}: {e}")
        
        return created
    
    def cleanup_all(self):
        """Clean up all created profiles"""
        logging.info(f"Cleaning up {len(self.created_profiles)} profiles...")
        
        for profile in self.created_profiles:
            try:
                profile_id = profile['id']
                
                # Stop profile if running
                try:
                    self.client.stop_profile(profile_id)
                except:
                    pass
                
                # Delete profile
                # Uncomment to actually delete
                # self.client.delete_profile(profile_id)
                logging.info(f"Cleaned up profile: {profile['name']}")
                
            except Exception as e:
                logging.error(f"Failed to cleanup profile {profile['name']}: {e}")
        
        self.created_profiles.clear()


if __name__ == "__main__":
    # Example usage of utilities
    setup_logging("INFO")
    
    # Test user agent generation
    agents = generate_user_agents()
    print(f"Generated {len(agents)} user agents")
    
    # Test profile batch creation
    batch_configs = create_profile_batch(3, "Test Batch")
    print(f"Created {len(batch_configs)} profile configurations")
    
    # Test duration estimation
    estimate = estimate_task_duration(5, 3, 2.5)
    print(f"Estimated duration: {estimate}")
    
    # Test proxy validation
    test_proxies = [
        "127.0.0.1:8080",
        "127.0.0.1:8080:user:pass",
        "socks5://127.0.0.1:1080",
        "tm://api_key|True",
        "invalid_proxy"
    ]
    
    for proxy in test_proxies:
        valid = validate_proxy_format(proxy)
        print(f"Proxy '{proxy}': {'Valid' if valid else 'Invalid'}")
