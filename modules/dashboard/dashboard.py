"""
Dashboard Module - User Session Display

A module that displays:
- Left: User information (from system)
- Middle: User image (optional, passed in constructor)
- Right: Time logged in since last logout and current date/time
"""
import tkinter as tk
from datetime import datetime
import os
import getpass
import subprocess

# Try to import PIL, but make it optional
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    ImageTk = None


def get_system_user():
    """Get the current system username."""
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get('USER', 'Unknown')


def get_linux_login_time():
    """
    Get the actual Linux session login time using 'who' command.
    Returns datetime object or None if not available.
    """
    try:
        # Run 'who' command to get login info
        result = subprocess.run(
            ['who'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    # Format: username tty date time
                    # Example: dpaulino pts/0 2026-02-11 10:30
                    username = parts[0]
                    if username == get_system_user():
                        # Parse the date and time
                        date_str = parts[2]  # YYYY-MM-DD
                        time_str = parts[3]  # HH:MM
                        datetime_str = f"{date_str} {time_str}"
                        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except Exception:
        pass
    
    return None


def get_system_login_time():
    """Get the system login time for current user."""
    login_time = get_linux_login_time()
    if login_time:
        return login_time
    # Fallback to current time if we can't get login time
    return datetime.now()


class DashboardModule:
    """
    Dashboard module displaying user session information.
    
    Left: User name and info (from system)
    Middle: User image (if provided)
    Right: Login duration + current date/time
    """
    
    name = "Dashboard"
    
    # Default theme
    THEME = {
        "name": "Clean Professional",
        "bg_color": "#ffffff",
        "fg_color": "#2c3e50",
        "accent_color": "#3498db",
        "secondary_bg": "#ecf0f1"
    }
    
    def __init__(
        self,
        app,
        user_name=None,
        user_image=None,
        login_time=None,
        bg_color="#ffffff",
        fg_color="#000000"
    ):
        """
        Initialize the Dashboard module.
        
        Args:
            app: Reference to the main App instance.
            user_name: Name of the user to display (defaults to system user).
            user_image: PIL Image object or file path (optional).
            login_time: datetime of last login (defaults to system login time).
            bg_color: Background color for the module.
            fg_color: Foreground color for the module.
        """
        self.app = app
        # Use system user if not provided
        self.user_name = user_name if user_name else get_system_user()
        self.bg_color = bg_color
        self.fg_color = fg_color
        
        # Handle user image
        self.user_image = None
        self.user_image_tk = None
        if user_image is not None and HAS_PIL:
            if isinstance(user_image, str):
                # It's a file path
                self._load_image_from_path(user_image)
            else:
                # It's already a PIL Image
                self.user_image = user_image
        
        # Set login time (use system login time if not provided)
        self.login_time = login_time if login_time else get_system_login_time()
        
        # Timer reference for cancellation
        self._update_timer = None
    
    def _load_image_from_path(self, image_path):
        """Load and prepare image from file path."""
        if not HAS_PIL:
            self.user_image = None
            return
        
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                # Resize to reasonable dimensions (max 200x200)
                img.thumbnail((200, 200), Image.LANCZOS)
                self.user_image = img
        except (OSError, IOError, Exception):
            # If image loading fails, just don't show anything
            self.user_image = None
    
    def _create_photo_image(self, pil_image):
        """Create PhotoImage from PIL Image for Tkinter display."""
        if pil_image is None or not HAS_PIL:
            return None
        
        try:
            # Convert to RGB if necessary (for PNG with transparency)
            if pil_image.mode in ('RGBA', 'P'):
                background = Image.new(
                    'RGB', pil_image.size, (255, 255, 255)
                )
                background.paste(
                    pil_image,
                    mask=pil_image.split()[-1] if pil_image.mode == 'RGBA' else None
                )
                pil_image = background
            
            return ImageTk.PhotoImage(pil_image)
        except Exception:
            return None
    
    def build(self, parent):
        """Build the Dashboard UI."""
        # Clear existing content
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Configure parent background
        parent.configure(bg=self.bg_color)
        
        # Main container with 3 columns
        main_frame = tk.Frame(parent, bg=self.bg_color)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Configure grid columns to be equally spaced
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        
        # --- LEFT SECTION: User Info ---
        left_frame = tk.Frame(main_frame, bg=self.bg_color)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # User icon placeholder (or use text)
        user_icon_label = tk.Label(
            left_frame,
            text="👤",
            font=("Arial", 48),
            bg=self.bg_color,
            fg=self.fg_color
        )
        user_icon_label.pack(pady=(0, 10))
        
        # User name label
        user_name_label = tk.Label(
            left_frame,
            text="Welcome,",
            font=("Arial", 14),
            bg=self.bg_color,
            fg="#7f8c8d"
        )
        user_name_label.pack()
        
        user_label = tk.Label(
            left_frame,
            text=self.user_name,
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg=self.fg_color
        )
        user_label.pack()
        
        # User status
        status_label = tk.Label(
            left_frame,
            text="● Online",
            font=("Arial", 12),
            bg=self.bg_color,
            fg="#27ae60"
        )
        status_label.pack(pady=(10, 0))
        
        # --- MIDDLE SECTION: User Image ---
        middle_frame = tk.Frame(main_frame, bg=self.bg_color)
        middle_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        if self.user_image is not None:
            # Create PhotoImage
            self.user_image_tk = self._create_photo_image(self.user_image)
            
            if self.user_image_tk is not None:
                image_label = tk.Label(
                    middle_frame,
                    image=self.user_image_tk,
                    bg=self.bg_color,
                    fg=self.fg_color,
                    relief="ridge",
                    borderwidth=2
                )
                image_label.image = self.user_image_tk  # Keep reference
                image_label.pack(expand=True)
            else:
                tk.Label(
                    middle_frame,
                    text="[Image Error]",
                    font=("Arial", 12),
                    bg=self.bg_color,
                    fg="#e74c3c"
                ).pack(expand=True)
        else:
            # No image provided - show placeholder or nothing
            tk.Label(
                middle_frame,
                text="",
                font=("Arial", 12),
                bg=self.bg_color,
                fg="#bdc3c7"
            ).pack(expand=True)
        
        # --- RIGHT SECTION: Time Info ---
        right_frame = tk.Frame(main_frame, bg=self.bg_color)
        right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        
        # Current date/time section
        datetime_label = tk.Label(
            right_frame,
            text="",
            font=("Arial", 14),
            bg=self.bg_color,
            fg=self.fg_color
        )
        datetime_label.pack(pady=(0, 5))
        
        # Time logged in section
        login_info_label = tk.Label(
            right_frame,
            text="Time Logged In:",
            font=("Arial", 12),
            bg=self.bg_color,
            fg="#7f8c8d"
        )
        login_info_label.pack()
        
        self.duration_label = tk.Label(
            right_frame,
            text="",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg="#3498db"
        )
        self.duration_label.pack(pady=(5, 0))
        
        # Login timestamp
        login_time_label = tk.Label(
            right_frame,
            text=f"Login: {self.login_time.strftime('%H:%M:%S')}",
            font=("Arial", 10),
            bg=self.bg_color,
            fg="#95a5a6"
        )
        login_time_label.pack(pady=(10, 0))
        
        # Function to update time displays
        def update_times():
            # Update current datetime
            now = datetime.now()
            current_time_str = now.strftime("%H:%M:%S")
            current_date_str = now.strftime("%Y-%m-%d")
            
            datetime_label.config(
                text=f"{current_date_str}\n{current_time_str}"
            )
            
            # Calculate logged in duration
            duration = now - self.login_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.duration_label.config(text=duration_str)
            
            # Schedule next update
            nonlocal _update_timer
            _update_timer = parent.after(1000, update_times)
        
        # Start time updates
        _update_timer = None
        update_times()
    
    def stop_updates(self):
        """Stop the time update timer."""
        if self._update_timer:
            try:
                # Try to cancel timer if parent is still valid
                if hasattr(self, '_duration_label') and \
                        self._duration_label.winfo_exists():
                    self._duration_label.master.after_cancel(self._update_timer)
            except Exception:
                pass
        self._update_timer = None

