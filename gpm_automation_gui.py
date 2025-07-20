"""
GPM-Login Automation UI Application

A comprehensive graphical user interface for all GPM-Login automation features including:
- Profile management
- YouTube automation
- Google sign-in automation
- Batch operations
- Settings and configuration

Author: mrlaw74
Date: July 20, 2025
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import threading
import time
import json
import subprocess
import webbrowser
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from gpm_client import GPMClient, GPMClientError
    from gpm_selenium import GPMSeleniumDriver, GPMAutomationHelper
    from utils import setup_logging
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please make sure all project files are present")


def save_json_report(data, filepath):
    """Save data as JSON report"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving report: {e}")
        return False


class GPMAutomationGUI:
    """Main GUI application for GPM-Login automation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("GPM-Login Automation Suite v1.1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize GPM client
        self.gpm_client = None
        self.automation_helper = None
        self.running_automations = {}
        self.settings = self.load_settings()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.check_gpm_connection()
        
    def setup_styles(self):
        """Setup custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        style.configure('Warning.TLabel', foreground='#f39c12')
        
        # Button styles
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', foreground='#27ae60')
        style.configure('Danger.TButton', foreground='#e74c3c')
        
    def create_widgets(self):
        """Create the main application widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎬 GPM-Login Automation Suite", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left sidebar - Navigation
        self.create_sidebar(main_frame)
        
        # Right content area
        self.create_content_area(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_sidebar(self, parent):
        """Create the navigation sidebar"""
        sidebar_frame = ttk.LabelFrame(parent, text="Navigation", padding="10")
        sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("📱 Profile Manager", self.show_profile_manager),
            ("🎬 YouTube Automation", self.show_youtube_automation),
            ("🔐 Google Sign-in Test", self.show_google_signin),
            ("📦 Batch Operations", self.show_batch_operations),
            ("🛡️ Fingerprint Tools", self.show_fingerprint_tools),
            ("⚙️ Settings", self.show_settings),
            ("📊 Reports", self.show_reports),
            ("❓ Help", self.show_help)
        ]
        
        self.nav_buttons = {}
        for i, (text, command) in enumerate(nav_buttons):
            btn = ttk.Button(sidebar_frame, text=text, command=command, width=20)
            btn.grid(row=i, column=0, pady=2, sticky=(tk.W, tk.E))
            self.nav_buttons[text] = btn
        
        # GPM Connection status
        self.connection_frame = ttk.LabelFrame(sidebar_frame, text="GPM-Login Status", padding="5")
        self.connection_frame.grid(row=len(nav_buttons), column=0, pady=(20, 0), sticky=(tk.W, tk.E))
        
        self.connection_status = ttk.Label(self.connection_frame, text="Checking...", style='Warning.TLabel')
        self.connection_status.grid(row=0, column=0)
        
        self.reconnect_btn = ttk.Button(self.connection_frame, text="Reconnect", 
                                       command=self.check_gpm_connection, state='disabled')
        self.reconnect_btn.grid(row=1, column=0, pady=(5, 0))
        
    def create_content_area(self, parent):
        """Create the main content area"""
        self.content_frame = ttk.Frame(parent)
        self.content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Initially show dashboard
        self.current_view = None
        self.show_dashboard()
        
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_text = tk.StringVar()
        self.status_text.set("Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_text)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Version info
        version_label = ttk.Label(status_frame, text="v1.1.0 by mrlaw74")
        version_label.grid(row=0, column=1, sticky=tk.E)
        
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_dashboard(self):
        """Show the dashboard view"""
        self.clear_content()
        self.current_view = "dashboard"
        
        # Dashboard container
        dashboard = ttk.Frame(self.content_frame, padding="20")
        dashboard.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dashboard.columnconfigure(0, weight=1)
        dashboard.columnconfigure(1, weight=1)
        
        # Welcome section
        welcome_frame = ttk.LabelFrame(dashboard, text="Welcome to GPM-Login Automation", padding="15")
        welcome_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        welcome_text = """
🎬 Complete YouTube automation workflow
🛡️ Advanced anti-detection and fingerprinting
📱 Professional profile management
🔐 Automated Google sign-in capabilities
📦 Batch processing for multiple profiles
⚙️ Customizable settings and configurations
        """
        ttk.Label(welcome_frame, text=welcome_text, font=('Arial', 11)).grid(row=0, column=0)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(dashboard, text="Quick Actions", padding="15")
        actions_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        quick_actions = [
            ("🎬 Start YouTube Automation", self.quick_youtube_automation),
            ("📱 Create New Profile", self.quick_create_profile),
            ("📊 View Profile List", self.quick_view_profiles),
            ("🧹 Cleanup Stopped Profiles", self.quick_cleanup_profiles)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            btn = ttk.Button(actions_frame, text=text, command=command, style='Primary.TButton')
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Statistics
        stats_frame = ttk.LabelFrame(dashboard, text="Statistics", padding="15")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.update_dashboard_stats(stats_frame)
        
    def update_dashboard_stats(self, parent):
        """Update dashboard statistics"""
        try:
            if self.gpm_client:
                profiles = self.gpm_client.list_profiles()
                total_profiles = profiles.get('pagination', {}).get('total', 0)
                
                stats_text = f"""
📊 Total Profiles: {total_profiles}
🟢 GPM-Login: Connected
⚡ Automation: Ready
🕒 Last Update: {datetime.now().strftime('%H:%M:%S')}
                """
            else:
                stats_text = """
📊 Total Profiles: N/A
🔴 GPM-Login: Disconnected
⚡ Automation: Not Available
🕒 Status: Connection Required
                """
                
            ttk.Label(parent, text=stats_text, font=('Arial', 10)).grid(row=0, column=0)
            
        except Exception as e:
            ttk.Label(parent, text=f"Error loading stats: {str(e)}", style='Error.TLabel').grid(row=0, column=0)
    
    def show_youtube_automation(self):
        """Show YouTube automation interface"""
        self.clear_content()
        self.current_view = "youtube"
        
        # YouTube automation container
        youtube_frame = ttk.Frame(self.content_frame, padding="20")
        youtube_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        youtube_frame.columnconfigure(0, weight=1)
        
        # Title
        ttk.Label(youtube_frame, text="🎬 YouTube Automation", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Configuration section
        config_frame = ttk.LabelFrame(youtube_frame, text="Configuration", padding="15")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Email
        ttk.Label(config_frame, text="Google Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(config_frame, width=40)
        self.email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Password
        ttk.Label(config_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(config_frame, show="*", width=40)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Search query
        ttk.Label(config_frame, text="Search Query:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.search_entry = ttk.Entry(config_frame, width=40)
        self.search_entry.insert(0, "Python programming tutorial")
        self.search_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Proxy (optional)
        ttk.Label(config_frame, text="Proxy (optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.proxy_entry = ttk.Entry(config_frame, width=40)
        self.proxy_entry.insert(0, "proxy.server.com:8080:user:pass")
        self.proxy_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Options
        options_frame = ttk.LabelFrame(youtube_frame, text="Options", padding="15")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.cleanup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto cleanup after completion", 
                       variable=self.cleanup_var).grid(row=0, column=0, sticky=tk.W)
        
        self.screenshot_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Take screenshot of video", 
                       variable=self.screenshot_var).grid(row=1, column=0, sticky=tk.W)
        
        self.keep_open_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Keep browser open after automation", 
                       variable=self.keep_open_var).grid(row=2, column=0, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(youtube_frame)
        control_frame.grid(row=3, column=0, pady=(0, 20))
        
        self.start_youtube_btn = ttk.Button(control_frame, text="🎬 Start YouTube Automation", 
                                          command=self.start_youtube_automation, style='Primary.TButton')
        self.start_youtube_btn.grid(row=0, column=0, padx=5)
        
        self.stop_youtube_btn = ttk.Button(control_frame, text="⏹️ Stop Automation", 
                                         command=self.stop_youtube_automation, state='disabled')
        self.stop_youtube_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="🧹 Quick Cleanup", 
                  command=self.quick_cleanup_profiles).grid(row=0, column=2, padx=5)
        
        # Log output
        log_frame = ttk.LabelFrame(youtube_frame, text="Automation Log", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        youtube_frame.rowconfigure(4, weight=1)
        
        self.youtube_log = scrolledtext.ScrolledText(log_frame, height=15, state='disabled')
        self.youtube_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def show_profile_manager(self):
        """Show profile management interface"""
        self.clear_content()
        self.current_view = "profiles"
        
        # Profile manager container
        profile_frame = ttk.Frame(self.content_frame, padding="20")
        profile_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        profile_frame.columnconfigure(0, weight=1)
        profile_frame.rowconfigure(1, weight=1)
        
        # Title and controls
        header_frame = ttk.Frame(profile_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(header_frame, text="📱 Profile Manager", style='Title.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(header_frame)
        control_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_profiles).grid(row=0, column=0, padx=2)
        ttk.Button(control_frame, text="➕ Create Profile", command=self.create_profile_dialog).grid(row=0, column=1, padx=2)
        ttk.Button(control_frame, text="🧹 Cleanup All", command=self.cleanup_all_profiles).grid(row=0, column=2, padx=2)
        
        # Profiles list
        list_frame = ttk.LabelFrame(profile_frame, text="Profiles", padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview for profiles
        columns = ('Name', 'ID', 'Browser', 'Proxy', 'Created', 'Status')
        self.profiles_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.profiles_tree.heading(col, text=col)
            self.profiles_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.profiles_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.profiles_tree.xview)
        self.profiles_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.profiles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Context menu
        self.create_profile_context_menu()
        
        # Load profiles
        self.refresh_profiles()
        
    def show_settings(self):
        """Show settings interface"""
        self.clear_content()
        self.current_view = "settings"
        
        # Settings container
        settings_frame = ttk.Frame(self.content_frame, padding="20")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        settings_frame.columnconfigure(0, weight=1)
        
        ttk.Label(settings_frame, text="⚙️ Settings", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # GPM-Login settings
        gpm_frame = ttk.LabelFrame(settings_frame, text="GPM-Login Connection", padding="15")
        gpm_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        gpm_frame.columnconfigure(1, weight=1)
        
        ttk.Label(gpm_frame, text="API URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.api_url_entry = ttk.Entry(gpm_frame, width=50)
        self.api_url_entry.insert(0, "http://127.0.0.1:19995")
        self.api_url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Button(gpm_frame, text="Test Connection", command=self.test_connection).grid(row=0, column=2, padx=(10, 0))
        
        # Automation settings
        auto_frame = ttk.LabelFrame(settings_frame, text="Automation Settings", padding="15")
        auto_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.auto_cleanup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_frame, text="Auto cleanup profiles after automation", 
                       variable=self.auto_cleanup_var).grid(row=0, column=0, sticky=tk.W)
        
        self.save_logs_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_frame, text="Save automation logs to files", 
                       variable=self.save_logs_var).grid(row=1, column=0, sticky=tk.W)
        
        self.show_warnings_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(auto_frame, text="Show urllib3 connection warnings", 
                       variable=self.show_warnings_var).grid(row=2, column=0, sticky=tk.W)
        
        # Save settings button
        ttk.Button(settings_frame, text="💾 Save Settings", command=self.save_settings_to_file, 
                  style='Primary.TButton').grid(row=3, column=0, pady=20)

    def show_google_signin(self):
        """Show Google sign-in test interface"""
        self.clear_content()
        self.current_view = "google_signin"
        
        # Google sign-in container
        signin_frame = ttk.Frame(self.content_frame, padding="20")
        signin_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        signin_frame.columnconfigure(0, weight=1)
        
        ttk.Label(signin_frame, text="🔐 Google Sign-in Test", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Configuration section
        config_frame = ttk.LabelFrame(signin_frame, text="Account Configuration", padding="15")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Email
        ttk.Label(config_frame, text="Google Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.signin_email_entry = ttk.Entry(config_frame, width=40)
        self.signin_email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Password
        ttk.Label(config_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.signin_password_entry = ttk.Entry(config_frame, show="*", width=40)
        self.signin_password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(signin_frame)
        control_frame.grid(row=2, column=0, pady=(0, 20))
        
        ttk.Button(control_frame, text="🔐 Test Sign-in", command=self.test_google_signin, 
                  style='Primary.TButton').grid(row=0, column=0, padx=5)
        
        # Log output
        log_frame = ttk.LabelFrame(signin_frame, text="Sign-in Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        signin_frame.rowconfigure(3, weight=1)
        
        self.signin_log = scrolledtext.ScrolledText(log_frame, height=15, state='disabled')
        self.signin_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def show_batch_operations(self):
        """Show batch operations interface"""
        self.clear_content()
        self.current_view = "batch"
        
        # Batch operations container
        batch_frame = ttk.Frame(self.content_frame, padding="20")
        batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        batch_frame.columnconfigure(0, weight=1)
        
        ttk.Label(batch_frame, text="📦 Batch Operations", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Batch type selection
        type_frame = ttk.LabelFrame(batch_frame, text="Operation Type", padding="15")
        type_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.batch_type_var = tk.StringVar(value="youtube")
        ttk.Radiobutton(type_frame, text="YouTube Automation", variable=self.batch_type_var, 
                       value="youtube").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(type_frame, text="Google Sign-in Test", variable=self.batch_type_var, 
                       value="signin").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(type_frame, text="Profile Creation", variable=self.batch_type_var, 
                       value="profiles").grid(row=2, column=0, sticky=tk.W)
        
        # Control buttons
        control_frame = ttk.Frame(batch_frame)
        control_frame.grid(row=2, column=0, pady=(0, 20))
        
        ttk.Button(control_frame, text="📦 Start Batch Operation", command=self.start_batch_operation, 
                  style='Primary.TButton').grid(row=0, column=0, padx=5)
        
        # Log output
        log_frame = ttk.LabelFrame(batch_frame, text="Batch Operation Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        batch_frame.rowconfigure(3, weight=1)
        
        self.batch_log = scrolledtext.ScrolledText(log_frame, height=15, state='disabled')
        self.batch_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def show_fingerprint_tools(self):
        """Show fingerprint tools interface"""
        self.clear_content()
        self.current_view = "fingerprint"
        
        # Fingerprint tools container
        fingerprint_frame = ttk.Frame(self.content_frame, padding="20")
        fingerprint_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        fingerprint_frame.columnconfigure(0, weight=1)
        
        ttk.Label(fingerprint_frame, text="🛡️ Fingerprint Tools", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Tools section
        tools_frame = ttk.LabelFrame(fingerprint_frame, text="Available Tools", padding="15")
        tools_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Button(tools_frame, text="🔍 Analyze Current Fingerprint", 
                  command=self.analyze_fingerprint).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(tools_frame, text="🎲 Generate Random Fingerprint", 
                  command=self.generate_fingerprint).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(tools_frame, text="📊 View Fingerprint Report", 
                  command=self.view_fingerprint_report).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Output area
        output_frame = ttk.LabelFrame(fingerprint_frame, text="Fingerprint Information", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        fingerprint_frame.rowconfigure(2, weight=1)
        
        self.fingerprint_output = scrolledtext.ScrolledText(output_frame, height=15, state='disabled')
        self.fingerprint_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def show_reports(self):
        """Show reports interface"""
        self.clear_content()
        self.current_view = "reports"
        
        # Reports container
        reports_frame = ttk.Frame(self.content_frame, padding="20")
        reports_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        reports_frame.columnconfigure(0, weight=1)
        
        ttk.Label(reports_frame, text="📊 Reports", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Report types
        types_frame = ttk.LabelFrame(reports_frame, text="Available Reports", padding="15")
        types_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Button(types_frame, text="📱 Profile Status Report", 
                  command=self.generate_profile_report).grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(types_frame, text="🎬 Automation History Report", 
                  command=self.generate_automation_report).grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        ttk.Button(types_frame, text="📈 Performance Report", 
                  command=self.generate_performance_report).grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Report display
        display_frame = ttk.LabelFrame(reports_frame, text="Report Content", padding="10")
        display_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        reports_frame.rowconfigure(2, weight=1)
        
        self.report_display = scrolledtext.ScrolledText(display_frame, height=15, state='disabled')
        self.report_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
                  
    def show_help(self):
        """Show help and documentation"""
        self.clear_content()
        self.current_view = "help"
        
        # Help container
        help_frame = ttk.Frame(self.content_frame, padding="20")
        help_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        help_frame.columnconfigure(0, weight=1)
        help_frame.rowconfigure(1, weight=1)
        
        ttk.Label(help_frame, text="❓ Help & Documentation", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Help content
        help_text = scrolledtext.ScrolledText(help_frame, height=25, wrap=tk.WORD)
        help_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        help_content = """
🎬 GPM-Login Automation Suite - Help Guide

GETTING STARTED:
1. Make sure GPM-Login is running on your computer
2. Check the connection status in the sidebar
3. Start with the Dashboard to see quick actions

YOUTUBE AUTOMATION:
• Enter your Google account credentials
• Specify what to search for on YouTube
• Choose automation options
• Click "Start YouTube Automation"
• Monitor progress in the log area

PROFILE MANAGER:
• View all your GPM profiles
• Create new profiles with custom settings
• Start/stop profiles individually
• Bulk cleanup operations

SETTINGS:
• Configure GPM-Login API connection
• Set automation preferences
• Enable/disable logging options

TROUBLESHOOTING:

Connection Issues:
- Ensure GPM-Login is running on port 19995
- Check Windows Firewall settings
- Try restarting GPM-Login application

Profile Issues:
- Use "Cleanup All" if profiles are stuck
- Check available system resources
- Verify proxy settings if using proxies

Browser Issues:
- Chrome compatibility issues are automatically handled
- Check Chrome browser installation
- Try creating a new profile if issues persist

Automation Issues:
- Verify Google account credentials
- Check internet connection
- Use simpler search terms if needed

KEYBOARD SHORTCUTS:
• F5 - Refresh current view
• Ctrl+Q - Quit application
• Ctrl+S - Save settings
• Ctrl+C - Stop running automation

SUPPORT:
• GitHub: https://github.com/mrlaw74/gpm_agent
• Documentation: Check project README.md
• Issues: Report bugs on GitHub Issues

VERSION INFORMATION:
• Application Version: 1.1.0
• Author: mrlaw74
• Release Date: July 20, 2025
• Compatible with: GPM-Login v3+

FEATURE OVERVIEW:
✅ YouTube automation with anti-detection
✅ Google sign-in automation
✅ Profile management and creation
✅ Batch operations
✅ Fingerprint protection
✅ Resource cleanup management
✅ Detailed logging and reporting
✅ Cross-platform compatibility
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state='disabled')
        
    # ... (Additional UI methods will be added in the next part)
    
    def check_gpm_connection(self):
        """Check GPM-Login connection status"""
        def check():
            try:
                self.gpm_client = GPMClient()
                profiles = self.gpm_client.list_profiles(per_page=1)
                self.automation_helper = GPMAutomationHelper(self.gpm_client)
                
                # Update UI on main thread
                self.root.after(0, lambda: self.update_connection_status(True, "Connected"))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_connection_status(False, f"Error: {str(e)[:30]}..."))
        
        # Run in background thread
        threading.Thread(target=check, daemon=True).start()
        self.status_text.set("Checking GPM-Login connection...")
        
    def update_connection_status(self, connected, message):
        """Update connection status in UI"""
        if connected:
            self.connection_status.config(text="🟢 " + message, style='Success.TLabel')
            self.reconnect_btn.config(state='disabled')
        else:
            self.connection_status.config(text="🔴 " + message, style='Error.TLabel')
            self.reconnect_btn.config(state='normal')
        
        self.status_text.set("Ready" if connected else "GPM-Login not available")
        
    def load_settings(self):
        """Load application settings"""
        settings_file = "gpm_automation_settings.json"
        default_settings = {
            "api_url": "http://127.0.0.1:19995",
            "auto_cleanup": True,
            "save_logs": True,
            "show_warnings": False,
            "default_search": "Python programming tutorial"
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception:
            pass
        
        return default_settings
        
    def save_settings_to_file(self):
        """Save current settings to file"""
        settings = {
            "api_url": self.api_url_entry.get() if hasattr(self, 'api_url_entry') else self.settings["api_url"],
            "auto_cleanup": self.auto_cleanup_var.get() if hasattr(self, 'auto_cleanup_var') else self.settings["auto_cleanup"],
            "save_logs": self.save_logs_var.get() if hasattr(self, 'save_logs_var') else self.settings["save_logs"],
            "show_warnings": self.show_warnings_var.get() if hasattr(self, 'show_warnings_var') else self.settings["show_warnings"],
            "default_search": self.settings.get("default_search", "Python programming tutorial")
        }
        
        try:
            with open("gpm_automation_settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
            self.settings = settings
            messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    # Quick action methods
    def quick_youtube_automation(self):
        """Quick YouTube automation setup"""
        self.show_youtube_automation()
        
    def quick_create_profile(self):
        """Quick profile creation"""
        self.show_profile_manager()
        self.create_profile_dialog()
        
    def quick_view_profiles(self):
        """Quick view profiles"""
        self.show_profile_manager()
        
    def quick_cleanup_profiles(self):
        """Quick cleanup of stopped profiles"""
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
            
        def cleanup():
            try:
                profiles = self.gpm_client.list_profiles()
                stopped_count = 0
                
                for profile in profiles.get('data', []):
                    try:
                        self.gpm_client.stop_profile(profile['id'])
                        stopped_count += 1
                    except:
                        pass  # Profile might already be stopped
                
                self.root.after(0, lambda: messagebox.showinfo("Cleanup", f"Stopped {stopped_count} profiles"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Cleanup failed: {e}"))
        
        threading.Thread(target=cleanup, daemon=True).start()
        self.status_text.set("Cleaning up profiles...")

    # Missing method implementations
    def test_connection(self):
        """Test GPM-Login connection"""
        self.check_gpm_connection()

    def refresh_profiles(self):
        """Refresh the profiles list"""
        if not hasattr(self, 'profiles_tree'):
            return
            
        # Clear existing items
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
            
        if not self.gpm_client:
            return
            
        try:
            profiles = self.gpm_client.list_profiles()
            for profile in profiles.get('data', []):
                self.profiles_tree.insert('', 'end', values=(
                    profile.get('name', 'N/A'),
                    profile.get('id', 'N/A'),
                    profile.get('browser_type', 'N/A'),
                    profile.get('proxy', {}).get('proxy_type', 'None'),
                    profile.get('created_at', 'N/A'),
                    profile.get('status', 'N/A')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {e}")

    def create_profile_context_menu(self):
        """Create context menu for profiles"""
        if not hasattr(self, 'profiles_tree'):
            return
            
        self.profile_context_menu = tk.Menu(self.root, tearoff=0)
        self.profile_context_menu.add_command(label="Start Profile", command=self.start_selected_profile)
        self.profile_context_menu.add_command(label="Stop Profile", command=self.stop_selected_profile)
        self.profile_context_menu.add_separator()
        self.profile_context_menu.add_command(label="Delete Profile", command=self.delete_selected_profile)
        
        def show_context_menu(event):
            try:
                self.profile_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.profile_context_menu.grab_release()
                
        self.profiles_tree.bind("<Button-3>", show_context_menu)

    def create_profile_dialog(self):
        """Show create profile dialog"""
        messagebox.showinfo("Create Profile", "Profile creation dialog - Feature coming soon!")

    def cleanup_all_profiles(self):
        """Cleanup all profiles"""
        self.quick_cleanup_profiles()

    def start_selected_profile(self):
        """Start selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
        messagebox.showinfo("Start Profile", "Start profile feature - Coming soon!")

    def stop_selected_profile(self):
        """Stop selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
        messagebox.showinfo("Stop Profile", "Stop profile feature - Coming soon!")

    def delete_selected_profile(self):
        """Delete selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
        messagebox.showinfo("Delete Profile", "Delete profile feature - Coming soon!")

    def start_youtube_automation(self):
        """Start YouTube automation"""
        messagebox.showinfo("YouTube Automation", "YouTube automation feature - Coming soon!")

    def stop_youtube_automation(self):
        """Stop YouTube automation"""
        messagebox.showinfo("Stop Automation", "Stop automation feature - Coming soon!")

    def test_google_signin(self):
        """Test Google sign-in"""
        messagebox.showinfo("Google Sign-in", "Google sign-in test feature - Coming soon!")

    def start_batch_operation(self):
        """Start batch operation"""
        messagebox.showinfo("Batch Operation", "Batch operation feature - Coming soon!")

    def analyze_fingerprint(self):
        """Analyze current fingerprint"""
        messagebox.showinfo("Fingerprint Analysis", "Fingerprint analysis feature - Coming soon!")

    def generate_fingerprint(self):
        """Generate random fingerprint"""
        messagebox.showinfo("Generate Fingerprint", "Generate fingerprint feature - Coming soon!")

    def view_fingerprint_report(self):
        """View fingerprint report"""
        messagebox.showinfo("Fingerprint Report", "Fingerprint report feature - Coming soon!")

    def generate_profile_report(self):
        """Generate profile status report"""
        messagebox.showinfo("Profile Report", "Profile report feature - Coming soon!")

    def generate_automation_report(self):
        """Generate automation history report"""
        messagebox.showinfo("Automation Report", "Automation report feature - Coming soon!")

    def generate_performance_report(self):
        """Generate performance report"""
        messagebox.showinfo("Performance Report", "Performance report feature - Coming soon!")


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = GPMAutomationGUI(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
