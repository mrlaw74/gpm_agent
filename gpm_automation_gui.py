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
        self.root.title("GPM-Login Automation v1.1.0")
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
        title_label = ttk.Label(main_frame, text="🎬 GPM-Login Automation", style='Title.TLabel')
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
        
        # Search query (required)
        ttk.Label(config_frame, text="Search Query (Required):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_entry = ttk.Entry(config_frame, width=40, font=('Arial', 10, 'bold'))
        self.search_entry.insert(0, "Python programming tutorial")
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Separator for optional login
        separator_frame = ttk.Frame(config_frame)
        separator_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        ttk.Label(separator_frame, text="Google Account Login (Optional)", style='Subtitle.TLabel').grid(row=0, column=0)
        
        # Email (optional)
        ttk.Label(config_frame, text="Google Email (Optional):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(config_frame, width=40)
        self.email_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Password (optional)
        ttk.Label(config_frame, text="Password (Optional):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(config_frame, show="*", width=40)
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Info label
        info_label = ttk.Label(config_frame, text="ℹ️ Login is optional. Automation will work without Google account.", 
                              font=('Arial', 9), foreground='#7f8c8d')
        info_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Proxy (optional)
        ttk.Label(config_frame, text="Proxy (Optional):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.proxy_entry = ttk.Entry(config_frame, width=40)
        self.proxy_entry.insert(0, "proxy.server.com:8080:user:pass")
        self.proxy_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
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
        
        # Add double-click handler for starting profiles
        self.profiles_tree.bind("<Double-1>", self.on_profile_double_click)
        
        # Add keyboard shortcuts
        self.profiles_tree.bind("<Return>", lambda e: self.start_selected_profile())
        self.profiles_tree.bind("<Delete>", lambda e: self.delete_selected_profile())
        self.profiles_tree.bind("<F5>", lambda e: self.refresh_profiles())
        
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
🎬 GPM-Login Automation - Help Guide

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
            self.status_text.set("Loading profiles...")
            profiles = self.gpm_client.list_profiles()
            
            total_profiles = len(profiles.get('data', []))
            
            for profile in profiles.get('data', []):
                # Format proxy information
                proxy_info = profile.get('proxy', {})
                if proxy_info and proxy_info.get('proxy_type'):
                    proxy_display = f"{proxy_info.get('proxy_type', 'Unknown')}"
                    if proxy_info.get('proxy_host'):
                        proxy_display += f" ({proxy_info.get('proxy_host')})"
                else:
                    proxy_display = 'None'
                
                # Format creation date
                created_at = profile.get('created_at', 'N/A')
                if created_at != 'N/A':
                    try:
                        # Try to format the date nicely
                        from datetime import datetime
                        if 'T' in created_at:
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_at = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass  # Keep original format if parsing fails
                
                # Get status from profile data
                status = profile.get('status', 'Unknown')
                if status == 'Active':
                    status = 'Running'
                elif status in ['Inactive', 'Stopped']:
                    status = 'Stopped'
                
                self.profiles_tree.insert('', 'end', values=(
                    profile.get('name', 'N/A'),
                    profile.get('id', 'N/A'),
                    profile.get('browser_type', 'Chrome'),
                    proxy_display,
                    created_at,
                    status
                ))
            
            # Update status with summary
            self.status_text.set(f"Loaded {total_profiles} profiles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {e}")
            self.status_text.set("Failed to load profiles")

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
            
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        # Get selected profile data
        item = selection[0]
        profile_data = self.profiles_tree.item(item)['values']
        
        if not profile_data or len(profile_data) < 2:
            messagebox.showerror("Error", "Invalid profile data")
            return
            
        profile_name = profile_data[0]
        profile_id = profile_data[1]
        
        # Confirm action
        result = messagebox.askyesno("Start Profile", 
                                   f"Start profile '{profile_name}'?\n\nThis will open a new browser window.")
        if not result:
            return
        
        def start_profile_thread():
            try:
                self.status_text.set(f"Starting profile: {profile_name}")
                
                # Start the profile using GPM API
                start_result = self.gpm_client.start_profile(profile_id)
                
                if start_result.get('success', False):
                    # Profile started successfully
                    browser_url = start_result.get('data', {}).get('http', '')
                    selenium_address = start_result.get('data', {}).get('selenium_address', '')
                    
                    success_msg = f"Profile '{profile_name}' started successfully!"
                    if browser_url:
                        success_msg += f"\n\nBrowser URL: {browser_url}"
                    if selenium_address:
                        success_msg += f"\nSelenium Address: {selenium_address}"
                    
                    self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
                    self.root.after(0, lambda: self.refresh_profiles())  # Refresh to show updated status
                    self.root.after(0, lambda: self.status_text.set(f"Profile '{profile_name}' started"))
                else:
                    error_msg = start_result.get('message', 'Unknown error occurred')
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start profile:\n{error_msg}"))
                    self.root.after(0, lambda: self.status_text.set("Ready"))
                    
            except Exception as e:
                error_msg = f"Failed to start profile '{profile_name}':\n{str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.status_text.set("Ready"))
        
        # Start in background thread to avoid blocking UI
        threading.Thread(target=start_profile_thread, daemon=True).start()

    def stop_selected_profile(self):
        """Stop selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
            
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        # Get selected profile data
        item = selection[0]
        profile_data = self.profiles_tree.item(item)['values']
        
        if not profile_data or len(profile_data) < 2:
            messagebox.showerror("Error", "Invalid profile data")
            return
            
        profile_name = profile_data[0]
        profile_id = profile_data[1]
        
        # Confirm action
        result = messagebox.askyesno("Stop Profile", 
                                   f"Stop profile '{profile_name}'?\n\nThis will close the browser window.")
        if not result:
            return
        
        def stop_profile_thread():
            try:
                self.status_text.set(f"Stopping profile: {profile_name}")
                
                # Stop the profile using GPM API
                stop_result = self.gpm_client.stop_profile(profile_id)
                
                if stop_result.get('success', False):
                    # Profile stopped successfully
                    success_msg = f"Profile '{profile_name}' stopped successfully!"
                    self.root.after(0, lambda: messagebox.showinfo("Success", success_msg))
                    self.root.after(0, lambda: self.refresh_profiles())  # Refresh to show updated status
                    self.root.after(0, lambda: self.status_text.set(f"Profile '{profile_name}' stopped"))
                else:
                    error_msg = stop_result.get('message', 'Unknown error occurred')
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to stop profile:\n{error_msg}"))
                    self.root.after(0, lambda: self.status_text.set("Ready"))
                    
            except Exception as e:
                error_msg = f"Failed to stop profile '{profile_name}':\n{str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                self.root.after(0, lambda: self.status_text.set("Ready"))
        
        # Start in background thread to avoid blocking UI
        threading.Thread(target=stop_profile_thread, daemon=True).start()

    def on_profile_double_click(self, event):
        """Handle double-click on profile - start the profile"""
        self.start_selected_profile()

    def delete_selected_profile(self):
        """Delete selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
        messagebox.showinfo("Delete Profile", "Delete profile feature - Coming soon!")

    def start_youtube_automation(self):
        """Start YouTube automation with optional Gmail login"""
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        # Get search query - this is required
        search_query = self.search_entry.get().strip()
        if not search_query:
            messagebox.showerror("Error", "Please enter a YouTube search query")
            self.search_entry.focus()
            return
        
        # Get optional Gmail credentials
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        use_login = bool(email and password)
        
        # Get proxy settings
        proxy_str = self.proxy_entry.get().strip()
        proxy_config = None
        if proxy_str and proxy_str != "proxy.server.com:8080:user:pass":
            try:
                # Parse proxy string: host:port:username:password
                proxy_parts = proxy_str.split(':')
                if len(proxy_parts) >= 2:
                    proxy_config = {
                        'proxy_type': 'http',
                        'proxy_host': proxy_parts[0],
                        'proxy_port': int(proxy_parts[1]),
                        'proxy_user': proxy_parts[2] if len(proxy_parts) > 2 else '',
                        'proxy_password': proxy_parts[3] if len(proxy_parts) > 3 else ''
                    }
            except (ValueError, IndexError):
                messagebox.showerror("Error", "Invalid proxy format. Use: host:port:user:pass")
                return
        
        # Get automation options
        auto_cleanup = self.cleanup_var.get()
        take_screenshot = self.screenshot_var.get()
        keep_open = self.keep_open_var.get()
        
        # Confirm start
        confirmation_text = f"Start YouTube automation?\n\nSearch: {search_query}"
        if use_login:
            confirmation_text += f"\nLogin: {email}"
        if proxy_config:
            confirmation_text += f"\nProxy: {proxy_config['proxy_host']}:{proxy_config['proxy_port']}"
        
        if not messagebox.askyesno("Start Automation", confirmation_text):
            return
        
        # Disable start button and enable stop button
        self.start_youtube_btn.config(state='disabled')
        self.stop_youtube_btn.config(state='normal')
        
        # Clear log
        self.youtube_log.config(state='normal')
        self.youtube_log.delete(1.0, tk.END)
        self.youtube_log.config(state='disabled')
        
        # Start automation in background thread
        def youtube_automation_thread():
            try:
                self.log_youtube_message("🎬 Starting YouTube automation...")
                self.status_text.set("Creating profile for automation")
                
                # Create a new profile for automation
                profile_data = {
                    'name': f'YouTube_Auto_{int(time.time())}',
                    'browser_type': 'chrome',
                    'os_type': 'windows',
                    'start_url': 'https://youtube.com'
                }
                
                # Add proxy if configured
                if proxy_config:
                    profile_data['proxy'] = proxy_config
                    self.log_youtube_message(f"📡 Using proxy: {proxy_config['proxy_host']}:{proxy_config['proxy_port']}")
                
                # Create profile
                profile_result = self.gpm_client.create_profile(profile_data)
                
                if not profile_result.get('success', False):
                    raise Exception(f"Failed to create profile: {profile_result.get('message', 'Unknown error')}")
                
                profile_id = profile_result['data']['id']
                profile_name = profile_result['data']['name']
                self.log_youtube_message(f"✅ Created profile: {profile_name}")
                
                # Start the profile
                self.log_youtube_message("🚀 Starting browser profile...")
                start_result = self.gpm_client.start_profile(profile_id)
                
                if not start_result.get('success', False):
                    raise Exception(f"Failed to start profile: {start_result.get('message', 'Unknown error')}")
                
                # Get connection details
                connection_data = start_result['data']
                selenium_address = connection_data.get('selenium_address', '')
                browser_port = connection_data.get('port', '')
                
                self.log_youtube_message(f"🌐 Browser started on port {browser_port}")
                
                # Connect to browser using Selenium
                self.log_youtube_message("🔗 Connecting to browser...")
                
                try:
                    from selenium import webdriver
                    from selenium.webdriver.common.by import By
                    from selenium.webdriver.support.ui import WebDriverWait
                    from selenium.webdriver.support import expected_conditions as EC
                    from selenium.webdriver.chrome.options import Options
                    from selenium.webdriver.common.keys import Keys
                except ImportError:
                    raise Exception("Selenium is not installed. Please install it using: pip install selenium")
                
                # Configure Chrome options
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{browser_port}")
                
                # Connect to the browser
                driver = webdriver.Chrome(options=chrome_options)
                self.log_youtube_message("✅ Connected to browser successfully")
                
                try:
                    # Navigate to YouTube
                    self.log_youtube_message("📺 Navigating to YouTube...")
                    driver.get("https://www.youtube.com")
                    
                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    self.log_youtube_message("✅ YouTube loaded successfully")
                    
                    # Optional: Login to Gmail/Google
                    if use_login:
                        self.log_youtube_message(f"🔐 Attempting to login with {email}...")
                        
                        # Look for sign-in button
                        try:
                            # Try to find and click sign-in button
                            sign_in_selectors = [
                                "a[href*='accounts.google.com']",
                                "[aria-label*='Sign in']",
                                "ytd-button-renderer#signin",
                                "#sign-in-button"
                            ]
                            
                            sign_in_clicked = False
                            for selector in sign_in_selectors:
                                try:
                                    sign_in_btn = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                    )
                                    sign_in_btn.click()
                                    sign_in_clicked = True
                                    self.log_youtube_message("🔘 Clicked sign-in button")
                                    break
                                except:
                                    continue
                            
                            if sign_in_clicked:
                                # Wait for Google login page
                                WebDriverWait(driver, 10).until(
                                    lambda d: "accounts.google.com" in d.current_url
                                )
                                
                                # Enter email
                                email_input = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.ID, "identifierId"))
                                )
                                email_input.send_keys(email)
                                email_input.send_keys(Keys.ENTER)
                                self.log_youtube_message("📧 Entered email address")
                                
                                # Wait a bit and enter password
                                time.sleep(2)
                                password_input = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.NAME, "password"))
                                )
                                password_input.send_keys(password)
                                password_input.send_keys(Keys.ENTER)
                                self.log_youtube_message("🔑 Entered password")
                                
                                # Wait for redirect back to YouTube
                                WebDriverWait(driver, 15).until(
                                    lambda d: "youtube.com" in d.current_url
                                )
                                self.log_youtube_message("✅ Successfully logged in!")
                            else:
                                self.log_youtube_message("⚠️ Could not find sign-in button, continuing without login")
                                
                        except Exception as login_error:
                            self.log_youtube_message(f"⚠️ Login failed: {str(login_error)}, continuing without login")
                    
                    # Search for the specified query
                    self.log_youtube_message(f"🔍 Searching for: {search_query}")
                    
                    # Find search box
                    search_selectors = [
                        "input#search",
                        "input[name='search_query']",
                        "#search-input input",
                        "input[placeholder*='Search']"
                    ]
                    
                    search_box = None
                    for selector in search_selectors:
                        try:
                            search_box = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            break
                        except:
                            continue
                    
                    if not search_box:
                        raise Exception("Could not find YouTube search box")
                    
                    # Clear and enter search query
                    search_box.clear()
                    search_box.send_keys(search_query)
                    search_box.send_keys(Keys.ENTER)
                    self.log_youtube_message("🔍 Search query submitted")
                    
                    # Wait for search results
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
                    )
                    self.log_youtube_message("📋 Search results loaded")
                    
                    # Click on first video
                    first_video = driver.find_element(By.CSS_SELECTOR, "ytd-video-renderer a#video-title")
                    video_title = first_video.get_attribute("title") or "Unknown Video"
                    
                    self.log_youtube_message(f"▶️ Playing video: {video_title}")
                    first_video.click()
                    
                    # Wait for video page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
                    )
                    self.log_youtube_message("🎬 Video page loaded successfully")
                    
                    # Take screenshot if requested
                    if take_screenshot:
                        try:
                            screenshot_path = f"youtube_screenshot_{int(time.time())}.png"
                            driver.save_screenshot(screenshot_path)
                            self.log_youtube_message(f"📸 Screenshot saved: {screenshot_path}")
                        except Exception as e:
                            self.log_youtube_message(f"⚠️ Screenshot failed: {str(e)}")
                    
                    # Wait a bit to let video load
                    time.sleep(3)
                    self.log_youtube_message("✅ YouTube automation completed successfully!")
                    
                    # Keep browser open if requested
                    if keep_open:
                        self.log_youtube_message("🔄 Keeping browser open as requested")
                        self.log_youtube_message("ℹ️ You can manually close the browser or use 'Stop Automation'")
                    else:
                        # Close browser
                        driver.quit()
                        self.log_youtube_message("🔒 Browser closed")
                        
                        # Stop profile if auto cleanup enabled
                        if auto_cleanup:
                            self.log_youtube_message("🧹 Cleaning up profile...")
                            self.gpm_client.stop_profile(profile_id)
                            self.log_youtube_message("✅ Profile cleanup completed")
                
                finally:
                    # If we're not keeping the browser open and didn't quit above
                    if not keep_open:
                        try:
                            driver.quit()
                        except:
                            pass
                
            except Exception as e:
                error_msg = f"❌ YouTube automation failed: {str(e)}"
                self.log_youtube_message(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Automation Failed", str(e)))
            
            finally:
                # Re-enable buttons
                self.root.after(0, lambda: self.start_youtube_btn.config(state='normal'))
                self.root.after(0, lambda: self.stop_youtube_btn.config(state='disabled'))
                self.root.after(0, lambda: self.status_text.set("Ready"))
        
        # Start automation thread
        self.running_automations['youtube'] = threading.Thread(target=youtube_automation_thread, daemon=True)
        self.running_automations['youtube'].start()
    
    def log_youtube_message(self, message):
        """Log message to YouTube automation log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        def update_log():
            self.youtube_log.config(state='normal')
            self.youtube_log.insert(tk.END, log_entry)
            self.youtube_log.see(tk.END)
            self.youtube_log.config(state='disabled')
        
        # Update log on main thread
        self.root.after(0, update_log)

    def stop_youtube_automation(self):
        """Stop YouTube automation"""
        if 'youtube' not in self.running_automations:
            messagebox.showinfo("Stop Automation", "No YouTube automation is currently running")
            return
        
        result = messagebox.askyesno("Stop Automation", 
                                   "Stop the running YouTube automation?\n\nThis will close the browser and cleanup the profile.")
        if not result:
            return
        
        try:
            # Log stop message
            self.log_youtube_message("⏹️ Stopping YouTube automation...")
            
            # The automation thread will handle cleanup when it detects the stop flag
            # For now, we'll disable the stop button and enable start button
            self.stop_youtube_btn.config(state='disabled')
            self.start_youtube_btn.config(state='normal')
            
            # Remove from running automations
            if 'youtube' in self.running_automations:
                del self.running_automations['youtube']
            
            self.log_youtube_message("✅ YouTube automation stopped")
            self.status_text.set("Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop automation: {str(e)}")
            self.log_youtube_message(f"❌ Failed to stop automation: {str(e)}")

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
