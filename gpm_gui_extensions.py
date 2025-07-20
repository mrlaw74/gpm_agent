"""
Extended functionality for GPM Automation GUI
Additional methods and dialog classes for the main application

Author: mrlaw74
Date: July 20, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import subprocess
import sys
import os
import json
import webbrowser
from datetime import datetime


class ProfileCreationDialog:
    """Dialog for creating new profiles with advanced options"""
    
    def __init__(self, parent, gpm_client):
        self.parent = parent
        self.gpm_client = gpm_client
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Create New Profile")
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📱 Create New Profile", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Basic info
        basic_frame = ttk.LabelFrame(main_frame, text="Basic Information", padding="10")
        basic_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Profile name
        ttk.Label(basic_frame, text="Profile Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(basic_frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Browser settings
        browser_frame = ttk.LabelFrame(main_frame, text="Browser Settings", padding="10")
        browser_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(browser_frame, text="Browser:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.browser_combo = ttk.Combobox(browser_frame, values=["chrome", "firefox"], state="readonly")
        self.browser_combo.set("chrome")
        self.browser_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Proxy settings
        proxy_frame = ttk.LabelFrame(main_frame, text="Proxy Settings (Optional)", padding="10")
        proxy_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.use_proxy_var = tk.BooleanVar()
        ttk.Checkbutton(proxy_frame, text="Use Proxy", variable=self.use_proxy_var, 
                       command=self.toggle_proxy_fields).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(proxy_frame, text="Proxy Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.proxy_type_combo = ttk.Combobox(proxy_frame, values=["http", "socks5"], state="readonly")
        self.proxy_type_combo.set("http")
        self.proxy_type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Label(proxy_frame, text="Server:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.proxy_server_entry = ttk.Entry(proxy_frame, width=40, placeholder_text="proxy.server.com:8080")
        self.proxy_server_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Label(proxy_frame, text="Username:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.proxy_user_entry = ttk.Entry(proxy_frame, width=40)
        self.proxy_user_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Label(proxy_frame, text="Password:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.proxy_pass_entry = ttk.Entry(proxy_frame, show="*", width=40)
        self.proxy_pass_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Fingerprint settings
        fingerprint_frame = ttk.LabelFrame(main_frame, text="Fingerprint Protection", padding="10")
        fingerprint_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.optimize_fingerprint_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(fingerprint_frame, text="Enable fingerprint optimization", 
                       variable=self.optimize_fingerprint_var).grid(row=0, column=0, sticky=tk.W)
        
        self.random_user_agent_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(fingerprint_frame, text="Use random User-Agent", 
                       variable=self.random_user_agent_var).grid(row=1, column=0, sticky=tk.W)
        
        self.canvas_fingerprint_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(fingerprint_frame, text="Canvas fingerprint protection", 
                       variable=self.canvas_fingerprint_var).grid(row=2, column=0, sticky=tk.W)
        
        # Initially disable proxy fields
        self.toggle_proxy_fields()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Create Profile", command=self.create_profile).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
    def toggle_proxy_fields(self):
        """Enable/disable proxy fields based on checkbox"""
        state = 'normal' if self.use_proxy_var.get() else 'disabled'
        for widget in [self.proxy_type_combo, self.proxy_server_entry, self.proxy_user_entry, self.proxy_pass_entry]:
            widget.config(state=state)
    
    def create_profile(self):
        """Create the profile with specified settings"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Profile name is required")
            return
        
        # Prepare profile data
        profile_data = {
            "name": name,
            "browser_type": self.browser_combo.get(),
            "remark": f"Created via GUI on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        # Add proxy if enabled
        if self.use_proxy_var.get():
            server = self.proxy_server_entry.get().strip()
            if server:
                proxy_data = {
                    "proxy_type": self.proxy_type_combo.get(),
                    "proxy_host": server.split(':')[0] if ':' in server else server,
                    "proxy_port": int(server.split(':')[1]) if ':' in server and len(server.split(':')) > 1 else 8080
                }
                
                username = self.proxy_user_entry.get().strip()
                password = self.proxy_pass_entry.get().strip()
                if username:
                    proxy_data["proxy_username"] = username
                if password:
                    proxy_data["proxy_password"] = password
                
                profile_data["proxy"] = proxy_data
        
        try:
            if self.optimize_fingerprint_var.get():
                # Use fingerprint optimization method
                result = self.gpm_client.create_fingerprint_optimized_profile(
                    name=name,
                    browser_type=self.browser_combo.get(),
                    proxy_info=profile_data.get("proxy"),
                    custom_settings={
                        "random_user_agent": self.random_user_agent_var.get(),
                        "canvas_protection": self.canvas_fingerprint_var.get()
                    }
                )
            else:
                # Use standard creation
                result = self.gpm_client.create_profile(profile_data)
            
            if result.get('success'):
                self.result = result
                messagebox.showinfo("Success", f"Profile '{name}' created successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to create profile: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create profile: {str(e)}")
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class BatchOperationDialog:
    """Dialog for batch operations on profiles"""
    
    def __init__(self, parent, gpm_client):
        self.parent = parent
        self.gpm_client = gpm_client
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Batch Operations")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_profiles()
        
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="📦 Batch Operations", font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Profile selection
        selection_frame = ttk.LabelFrame(main_frame, text="Select Profiles", padding="10")
        selection_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Profile listbox with checkboxes (simulated)
        self.profiles_listbox = tk.Listbox(selection_frame, selectmode=tk.MULTIPLE, height=10)
        self.profiles_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(selection_frame, orient=tk.VERTICAL, command=self.profiles_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.profiles_listbox.config(yscrollcommand=scrollbar.set)
        
        # Selection buttons
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(select_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="Invert Selection", command=self.invert_selection).pack(side=tk.LEFT)
        
        # Operations
        operations_frame = ttk.LabelFrame(main_frame, text="Operations", padding="10")
        operations_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(operations_frame, text="🎬 Start YouTube Automation", command=self.batch_youtube).pack(fill=tk.X, pady=2)
        ttk.Button(operations_frame, text="▶️ Start Selected Profiles", command=self.start_profiles).pack(fill=tk.X, pady=2)
        ttk.Button(operations_frame, text="⏹️ Stop Selected Profiles", command=self.stop_profiles).pack(fill=tk.X, pady=2)
        ttk.Button(operations_frame, text="🗑️ Delete Selected Profiles", command=self.delete_profiles).pack(fill=tk.X, pady=2)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=(10, 0))
        
    def load_profiles(self):
        """Load profiles into listbox"""
        try:
            profiles = self.gpm_client.list_profiles()
            self.profile_data = profiles.get('data', [])
            
            self.profiles_listbox.delete(0, tk.END)
            for profile in self.profile_data:
                display_text = f"{profile['name']} (ID: {profile['id']})"
                self.profiles_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")
    
    def select_all(self):
        """Select all profiles"""
        self.profiles_listbox.select_set(0, tk.END)
    
    def select_none(self):
        """Deselect all profiles"""
        self.profiles_listbox.selection_clear(0, tk.END)
    
    def invert_selection(self):
        """Invert current selection"""
        selected = set(self.profiles_listbox.curselection())
        all_indices = set(range(self.profiles_listbox.size()))
        
        self.profiles_listbox.selection_clear(0, tk.END)
        for i in all_indices - selected:
            self.profiles_listbox.selection_set(i)
    
    def get_selected_profiles(self):
        """Get selected profile data"""
        selected_indices = self.profiles_listbox.curselection()
        return [self.profile_data[i] for i in selected_indices]
    
    def start_profiles(self):
        """Start selected profiles"""
        selected = self.get_selected_profiles()
        if not selected:
            messagebox.showwarning("Warning", "No profiles selected")
            return
        
        def start_batch():
            success_count = 0
            for profile in selected:
                try:
                    self.gpm_client.start_profile(profile['id'])
                    success_count += 1
                except Exception:
                    pass
            
            self.parent.after(0, lambda: messagebox.showinfo("Batch Start", f"Started {success_count}/{len(selected)} profiles"))
        
        threading.Thread(target=start_batch, daemon=True).start()
    
    def stop_profiles(self):
        """Stop selected profiles"""
        selected = self.get_selected_profiles()
        if not selected:
            messagebox.showwarning("Warning", "No profiles selected")
            return
        
        def stop_batch():
            success_count = 0
            for profile in selected:
                try:
                    self.gmp_client.stop_profile(profile['id'])
                    success_count += 1
                except Exception:
                    pass
            
            self.parent.after(0, lambda: messagebox.showinfo("Batch Stop", f"Stopped {success_count}/{len(selected)} profiles"))
        
        threading.Thread(target=stop_batch, daemon=True).start()
    
    def delete_profiles(self):
        """Delete selected profiles"""
        selected = self.get_selected_profiles()
        if not selected:
            messagebox.showwarning("Warning", "No profiles selected")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {len(selected)} profile(s)?"):
            return
        
        def delete_batch():
            success_count = 0
            for profile in selected:
                try:
                    self.gpm_client.delete_profile(profile['id'])
                    success_count += 1
                except Exception:
                    pass
            
            self.parent.after(0, lambda: messagebox.showinfo("Batch Delete", f"Deleted {success_count}/{len(selected)} profiles"))
            self.parent.after(100, self.load_profiles)  # Refresh the list
        
        threading.Thread(target=delete_batch, daemon=True).start()
    
    def batch_youtube(self):
        """Batch YouTube automation"""
        selected = self.get_selected_profiles()
        if not selected:
            messagebox.showwarning("Warning", "No profiles selected")
            return
        
        # Get credentials
        email = simpledialog.askstring("Google Email", "Enter Google email:")
        if not email:
            return
        
        password = simpledialog.askstring("Google Password", "Enter Google password:", show='*')
        if not password:
            return
        
        search_query = simpledialog.askstring("Search Query", "Enter YouTube search query:", 
                                            initialvalue="Python programming tutorial")
        if not search_query:
            search_query = "Python programming tutorial"
        
        messagebox.showinfo("Batch Automation", f"Starting YouTube automation for {len(selected)} profiles...")
        self.dialog.destroy()


# Extension methods for the main GUI class
class GPMAutomationGUIExtensions:
    """Additional methods for the main GUI application"""
    
    def start_youtube_automation(self):
        """Start YouTube automation in background thread"""
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        # Validate inputs
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        search_query = self.search_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Email and password are required")
            return
        
        if not search_query:
            search_query = "Python programming tutorial"
        
        # Disable start button, enable stop button
        self.start_youtube_btn.config(state='disabled')
        self.stop_youtube_btn.config(state='normal')
        
        # Clear log
        self.youtube_log.config(state='normal')
        self.youtube_log.delete(1.0, tk.END)
        self.youtube_log.config(state='disabled')
        
        # Prepare automation parameters
        automation_params = {
            'email': email,
            'password': password,
            'search_query': search_query,
            'proxy': self.proxy_entry.get().strip() if self.proxy_entry.get().strip() else None,
            'auto_cleanup': self.cleanup_var.get(),
            'take_screenshot': self.screenshot_var.get(),
            'keep_open': self.keep_open_var.get()
        }
        
        # Start automation in background
        self.automation_thread = threading.Thread(
            target=self.run_youtube_automation,
            args=(automation_params,),
            daemon=True
        )
        self.automation_thread.start()
        
        self.status_text.set("YouTube automation running...")
    
    def run_youtube_automation(self, params):
        """Run YouTube automation in background thread"""
        try:
            # Import the automation script
            from clean_youtube_automation import run_youtube_automation
            
            # Create a custom logger that writes to GUI
            class GUILogger:
                def __init__(self, log_widget, root):
                    self.log_widget = log_widget
                    self.root = root
                
                def info(self, message):
                    self.write_log(message, "INFO")
                
                def error(self, message):
                    self.write_log(message, "ERROR")
                
                def warning(self, message):
                    self.write_log(message, "WARNING")
                
                def write_log(self, message, level):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_message = f"[{timestamp}] {level}: {message}\n"
                    
                    def update_log():
                        self.log_widget.config(state='normal')
                        self.log_widget.insert(tk.END, log_message)
                        self.log_widget.see(tk.END)
                        self.log_widget.config(state='disabled')
                    
                    self.root.after(0, update_log)
            
            gui_logger = GUILogger(self.youtube_log, self.root)
            
            # Run automation
            result = run_youtube_automation(
                gpm_client=self.gmp_client,
                google_email=params['email'],
                google_password=params['password'],
                search_query=params['search_query'],
                proxy_string=params['proxy'],
                logger=gui_logger,
                auto_cleanup=params['auto_cleanup']
            )
            
            # Update UI on completion
            self.root.after(0, lambda: self.on_automation_complete(result))
            
        except Exception as e:
            error_msg = f"Automation failed: {str(e)}"
            self.root.after(0, lambda: self.on_automation_error(error_msg))
    
    def on_automation_complete(self, result):
        """Handle automation completion"""
        self.start_youtube_btn.config(state='normal')
        self.stop_youtube_btn.config(state='disabled')
        
        if result.get('success'):
            self.status_text.set("YouTube automation completed successfully")
            messagebox.showinfo("Success", "YouTube automation completed successfully!")
        else:
            self.status_text.set("YouTube automation failed")
            messagebox.showerror("Error", f"Automation failed: {result.get('error', 'Unknown error')}")
    
    def on_automation_error(self, error_msg):
        """Handle automation error"""
        self.start_youtube_btn.config(state='normal')
        self.stop_youtube_btn.config(state='disabled')
        self.status_text.set("YouTube automation failed")
        
        # Log error
        self.youtube_log.config(state='normal')
        self.youtube_log.insert(tk.END, f"\n[ERROR] {error_msg}\n")
        self.youtube_log.see(tk.END)
        self.youtube_log.config(state='disabled')
        
        messagebox.showerror("Error", error_msg)
    
    def stop_youtube_automation(self):
        """Stop running YouTube automation"""
        if hasattr(self, 'automation_thread') and self.automation_thread.is_alive():
            # Note: Python threading doesn't support direct termination
            # This is a graceful notification
            self.status_text.set("Stopping automation...")
            messagebox.showinfo("Stop", "Automation stop requested. It may take a moment to complete.")
        
        self.start_youtube_btn.config(state='normal')
        self.stop_youtube_btn.config(state='disabled')
    
    def refresh_profiles(self):
        """Refresh the profiles list"""
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        def load_profiles():
            try:
                profiles = self.gpm_client.list_profiles()
                profile_data = profiles.get('data', [])
                
                # Update UI on main thread
                self.root.after(0, lambda: self.update_profiles_tree(profile_data))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load profiles: {str(e)}"))
        
        threading.Thread(target=load_profiles, daemon=True).start()
        self.status_text.set("Loading profiles...")
    
    def update_profiles_tree(self, profile_data):
        """Update profiles tree with data"""
        # Clear existing items
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
        
        # Add profiles
        for profile in profile_data:
            values = (
                profile.get('name', 'N/A'),
                profile.get('id', 'N/A'),
                profile.get('browser_type', 'N/A'),
                'Yes' if profile.get('proxy') else 'No',
                profile.get('created_time', 'N/A'),
                profile.get('status', 'Unknown')
            )
            self.profiles_tree.insert('', tk.END, values=values, tags=(profile.get('id'),))
        
        self.status_text.set(f"Loaded {len(profile_data)} profiles")
    
    def create_profile_context_menu(self):
        """Create context menu for profiles tree"""
        self.profile_menu = tk.Menu(self.root, tearoff=0)
        self.profile_menu.add_command(label="▶️ Start Profile", command=self.start_selected_profile)
        self.profile_menu.add_command(label="⏹️ Stop Profile", command=self.stop_selected_profile)
        self.profile_menu.add_separator()
        self.profile_menu.add_command(label="🎬 YouTube Automation", command=self.youtube_selected_profile)
        self.profile_menu.add_separator()
        self.profile_menu.add_command(label="✏️ Edit Profile", command=self.edit_selected_profile)
        self.profile_menu.add_command(label="🗑️ Delete Profile", command=self.delete_selected_profile)
        
        def show_context_menu(event):
            # Select the item under cursor
            item = self.profiles_tree.identify_row(event.y)
            if item:
                self.profiles_tree.selection_set(item)
                self.profile_menu.post(event.x_root, event.y_root)
        
        self.profiles_tree.bind("<Button-3>", show_context_menu)  # Right-click
    
    def get_selected_profile_id(self):
        """Get the ID of the currently selected profile"""
        selection = self.profiles_tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        tags = self.profiles_tree.item(item, 'tags')
        return tags[0] if tags else None
    
    def start_selected_profile(self):
        """Start the selected profile"""
        profile_id = self.get_selected_profile_id()
        if not profile_id:
            messagebox.showwarning("Warning", "No profile selected")
            return
        
        def start():
            try:
                result = self.gpm_client.start_profile(profile_id)
                if result.get('success'):
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Profile started successfully"))
                    self.root.after(100, self.refresh_profiles)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to start profile"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start profile: {str(e)}"))
        
        threading.Thread(target=start, daemon=True).start()
    
    def stop_selected_profile(self):
        """Stop the selected profile"""
        profile_id = self.get_selected_profile_id()
        if not profile_id:
            messagebox.showwarning("Warning", "No profile selected")
            return
        
        def stop():
            try:
                result = self.gpm_client.stop_profile(profile_id)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Profile stopped"))
                self.root.after(100, self.refresh_profiles)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to stop profile: {str(e)}"))
        
        threading.Thread(target=stop, daemon=True).start()
    
    def delete_selected_profile(self):
        """Delete the selected profile"""
        profile_id = self.get_selected_profile_id()
        if not profile_id:
            messagebox.showwarning("Warning", "No profile selected")
            return
        
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this profile?"):
            return
        
        def delete():
            try:
                result = self.gpm_client.delete_profile(profile_id)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Profile deleted"))
                self.root.after(100, self.refresh_profiles)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to delete profile: {str(e)}"))
        
        threading.Thread(target=delete, daemon=True).start()
    
    def create_profile_dialog(self):
        """Show create profile dialog"""
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        dialog = ProfileCreationDialog(self.root, self.gpm_client)
        self.root.wait_window(dialog.dialog)
        
        # Refresh profiles if a profile was created
        if hasattr(dialog, 'result') and dialog.result:
            self.refresh_profiles()
    
    def show_batch_operations(self):
        """Show batch operations interface"""
        self.clear_content()
        self.current_view = "batch"
        
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        # Show batch operations dialog
        dialog = BatchOperationDialog(self.root, self.gpm_client)
    
    def show_fingerprint_tools(self):
        """Show fingerprint tools interface"""
        self.clear_content()
        self.current_view = "fingerprint"
        
        # Fingerprint tools container
        fingerprint_frame = ttk.Frame(self.content_frame, padding="20")
        fingerprint_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        fingerprint_frame.columnconfigure(0, weight=1)
        
        ttk.Label(fingerprint_frame, text="🛡️ Fingerprint Protection Tools", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Information section
        info_frame = ttk.LabelFrame(fingerprint_frame, text="Browser Fingerprinting Protection", padding="15")
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        info_text = """
🛡️ This application includes advanced fingerprint protection covering 13 major categories:

• User-Agent and Browser Headers
• Screen Resolution and Color Depth  
• Timezone and Language Settings
• Canvas and WebGL Fingerprinting
• Audio Context Fingerprinting
• Font Detection and Rendering
• Hardware Specifications
• Network and Connection Info
• Plugin and Extension Detection
• Behavioral Patterns
• Geolocation Data
• Clipboard and Storage Access
• Performance Metrics

All profiles created with fingerprint optimization automatically include these protections.
        """
        
        ttk.Label(info_frame, text=info_text, font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W)
        
        # Tools section
        tools_frame = ttk.LabelFrame(fingerprint_frame, text="Fingerprint Tools", padding="15")
        tools_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Button(tools_frame, text="🔍 Test Browser Fingerprint", 
                  command=lambda: webbrowser.open("https://browserleaks.com/")).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(tools_frame, text="📊 Canvas Fingerprint Test", 
                  command=lambda: webbrowser.open("https://browserleaks.com/canvas")).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(tools_frame, text="🔊 Audio Fingerprint Test", 
                  command=lambda: webbrowser.open("https://browserleaks.com/audio")).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(tools_frame, text="🌐 WebRTC Test", 
                  command=lambda: webbrowser.open("https://browserleaks.com/webrtc")).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
    
    def show_reports(self):
        """Show reports and logs interface"""
        self.clear_content()
        self.current_view = "reports"
        
        # Reports container
        reports_frame = ttk.Frame(self.content_frame, padding="20")
        reports_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        reports_frame.columnconfigure(0, weight=1)
        reports_frame.rowconfigure(2, weight=1)
        
        ttk.Label(reports_frame, text="📊 Reports & Logs", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Controls
        controls_frame = ttk.Frame(reports_frame)
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Button(controls_frame, text="📁 Open Logs Folder", command=self.open_logs_folder).grid(row=0, column=0, padx=5)
        ttk.Button(controls_frame, text="📊 Generate Report", command=self.generate_automation_report).grid(row=0, column=1, padx=5)
        ttk.Button(controls_frame, text="🧹 Clear Old Logs", command=self.clear_old_logs).grid(row=0, column=2, padx=5)
        
        # Log viewer
        log_frame = ttk.LabelFrame(reports_frame, text="Recent Activity Log", padding="10")
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.reports_log = scrolledtext.ScrolledText(log_frame, height=20, state='disabled')
        self.reports_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Load recent logs
        self.load_recent_logs()
    
    def open_logs_folder(self):
        """Open the logs folder in file explorer"""
        logs_folder = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_folder):
            os.makedirs(logs_folder)
        
        if sys.platform == "win32":
            os.startfile(logs_folder)
        elif sys.platform == "darwin":
            subprocess.run(["open", logs_folder])
        else:
            subprocess.run(["xdg-open", logs_folder])
    
    def generate_automation_report(self):
        """Generate a comprehensive automation report"""
        try:
            if not self.gpm_client:
                messagebox.showerror("Error", "GPM-Login not connected")
                return
            
            # Gather data
            profiles = self.gpm_client.list_profiles()
            
            report_data = {
                "report_generated": datetime.now().isoformat(),
                "total_profiles": profiles.get('pagination', {}).get('total', 0),
                "profiles": profiles.get('data', []),
                "application_version": "1.1.0",
                "gpm_connection": "Connected" if self.gpm_client else "Disconnected"
            }
            
            # Save report
            filename = f"gpm_automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialvalue=filename
            )
            
            if filepath:
                save_json_report(report_data, filepath)
                messagebox.showinfo("Success", f"Report saved to {filepath}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def clear_old_logs(self):
        """Clear old log files"""
        logs_folder = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(logs_folder):
            messagebox.showinfo("Info", "No logs folder found")
            return
        
        try:
            log_files = [f for f in os.listdir(logs_folder) if f.endswith('.log')]
            if not log_files:
                messagebox.showinfo("Info", "No log files found")
                return
            
            if messagebox.askyesno("Confirm", f"Delete {len(log_files)} log file(s)?"):
                for log_file in log_files:
                    os.remove(os.path.join(logs_folder, log_file))
                messagebox.showinfo("Success", f"Deleted {len(log_files)} log files")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")
    
    def load_recent_logs(self):
        """Load recent logs into the viewer"""
        try:
            logs_folder = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(logs_folder):
                self.reports_log.config(state='normal')
                self.reports_log.insert(tk.END, "No logs folder found. Logs will be created when automation runs.\n")
                self.reports_log.config(state='disabled')
                return
            
            # Find most recent log file
            log_files = [f for f in os.listdir(logs_folder) if f.endswith('.log')]
            if not log_files:
                self.reports_log.config(state='normal')
                self.reports_log.insert(tk.END, "No log files found. Logs will be created when automation runs.\n")
                self.reports_log.config(state='disabled')
                return
            
            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: os.path.getmtime(os.path.join(logs_folder, f)))
            log_path = os.path.join(logs_folder, latest_log)
            
            # Read and display recent log entries (last 100 lines)
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-100:] if len(lines) > 100 else lines
            
            self.reports_log.config(state='normal')
            self.reports_log.delete(1.0, tk.END)
            self.reports_log.insert(tk.END, f"=== Recent entries from {latest_log} ===\n\n")
            self.reports_log.insert(tk.END, ''.join(recent_lines))
            self.reports_log.config(state='disabled')
            
        except Exception as e:
            self.reports_log.config(state='normal')
            self.reports_log.insert(tk.END, f"Error loading logs: {str(e)}\n")
            self.reports_log.config(state='disabled')
    
    def test_connection(self):
        """Test GPM-Login connection with custom URL"""
        url = self.api_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "API URL is required")
            return
        
        def test():
            try:
                test_client = GPMClient(base_url=url)
                profiles = test_client.list_profiles(per_page=1)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Connection successful!"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Connection failed: {str(e)}"))
        
        threading.Thread(target=test, daemon=True).start()
    
    def show_google_signin(self):
        """Show Google sign-in test interface"""
        self.clear_content()
        self.current_view = "google_signin"
        
        # Google sign-in container
        signin_frame = ttk.Frame(self.content_frame, padding="20")
        signin_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        signin_frame.columnconfigure(0, weight=1)
        
        ttk.Label(signin_frame, text="🔐 Google Sign-in Test", style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Description
        desc_frame = ttk.LabelFrame(signin_frame, text="Description", padding="15")
        desc_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        desc_text = """
This tool allows you to test Google sign-in functionality with your GPM profiles.
It will create a new profile, open Google.com, and attempt to sign in with the provided credentials.
        """
        ttk.Label(desc_frame, text=desc_text).grid(row=0, column=0, sticky=tk.W)
        
        # Configuration
        config_frame = ttk.LabelFrame(signin_frame, text="Configuration", padding="15")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(config_frame, text="Google Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.signin_email_entry = ttk.Entry(config_frame, width=40)
        self.signin_email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        ttk.Label(config_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.signin_password_entry = ttk.Entry(config_frame, show="*", width=40)
        self.signin_password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Controls
        control_frame = ttk.Frame(signin_frame)
        control_frame.grid(row=3, column=0, pady=(0, 20))
        
        ttk.Button(control_frame, text="🔐 Test Google Sign-in", 
                  command=self.test_google_signin, style='Primary.TButton').grid(row=0, column=0)
        
        # Results
        results_frame = ttk.LabelFrame(signin_frame, text="Test Results", padding="10")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        signin_frame.rowconfigure(4, weight=1)
        
        self.signin_log = scrolledtext.ScrolledText(results_frame, height=15, state='disabled')
        self.signin_log.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def test_google_signin(self):
        """Test Google sign-in functionality"""
        if not self.gpm_client:
            messagebox.showerror("Error", "GPM-Login not connected")
            return
        
        email = self.signin_email_entry.get().strip()
        password = self.signin_password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Email and password are required")
            return
        
        # Clear log
        self.signin_log.config(state='normal')
        self.signin_log.delete(1.0, tk.END)
        self.signin_log.config(state='disabled')
        
        def run_test():
            try:
                # Import test automation
                from simple_youtube_automation import run_youtube_automation
                
                # Create GUI logger
                class GUILogger:
                    def __init__(self, log_widget, root):
                        self.log_widget = log_widget
                        self.root = root
                    
                    def info(self, message):
                        self.write_log(message, "INFO")
                    
                    def error(self, message):
                        self.write_log(message, "ERROR")
                    
                    def write_log(self, message, level):
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        log_message = f"[{timestamp}] {level}: {message}\n"
                        
                        def update_log():
                            self.log_widget.config(state='normal')
                            self.log_widget.insert(tk.END, log_message)
                            self.log_widget.see(tk.END)
                            self.log_widget.config(state='disabled')
                        
                        self.root.after(0, update_log)
                
                gui_logger = GUILogger(self.signin_log, self.root)
                
                # Run just the sign-in part (without YouTube automation)
                result = run_youtube_automation(
                    gpm_client=self.gpm_client,
                    google_email=email,
                    google_password=password,
                    search_query="test",  # Won't be used since we'll stop after sign-in
                    test_signin_only=True,  # Custom parameter to stop after sign-in
                    logger=gui_logger
                )
                
                if result.get('success'):
                    self.root.after(0, lambda: messagebox.showinfo("Success", "Google sign-in test completed successfully!"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Sign-in test failed: {result.get('error', 'Unknown error')}"))
                
            except Exception as e:
                error_msg = f"Sign-in test failed: {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        threading.Thread(target=run_test, daemon=True).start()
        self.status_text.set("Testing Google sign-in...")
