import tkinter as tk
from datetime import datetime
import os


class LogModule:
    """Module to display log files in real-time."""
    
    name = "Log"
    
    # Terminal-style theme
    THEME = {
        "name": "Terminal",
        "bg_color": "#000000",
        "fg_color": "#00ff00",
        "accent_color": "#00ff00",
        "secondary_bg": "#111111"
    }
    
    def __init__(
        self,
        app,
        log_file=None,
        bg_color=None,
        fg_color=None,
        font=("Courier", 10)
    ):
        """
        Initialize the Log module.

        Args:
            app: Reference to the main App instance.
            log_file: Path to the log file to display.
            bg_color: Background color (uses theme default if None).
            fg_color: Foreground color (uses theme default if None).
            font: Font for the log text.
        """
        self.app = app
        self.name = "Log"
        self.log_file = log_file
        # Use theme defaults if colors not specified
        self.bg_color = bg_color or self.THEME["bg_color"]
        self.fg_color = fg_color or self.THEME["fg_color"]
        self.font = font
        self.text_area = None
        self._last_modified = None
        self._last_size = None

    def build(self, parent):
        # Clear existing content
        for widget in parent.winfo_children():
            widget.destroy()

        # Create a Text widget for displaying logs
        self.text_area = tk.Text(
            parent,
            state="disabled",
            bg=self.bg_color,
            fg=self.fg_color,
            font=self.font
        )
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)

        # If a log file is provided, read and display its content
        if self.log_file:
            self.load_log_file()
            self.start_watching()

    def load_log_file(self):
        """Load and display the entire log file content."""
        try:
            with open(self.log_file, "r") as f:
                log_content = f.read()
            self.text_area.config(state="normal")
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, log_content)
            self.text_area.config(state="disabled")
            # Track file state
            self._last_modified = os.path.getmtime(self.log_file)
            self._last_size = os.path.getsize(self.log_file)
        except Exception as e:
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, f"Error loading log file: {e}\n")
            self.text_area.config(state="disabled")

    def start_watching(self, check_interval=500):
        """Start watching the log file for real-time updates."""
        if self.log_file and os.path.exists(self.log_file):
            self._check_for_updates()

    def _check_for_updates(self, check_interval=500):
        """Check if the log file has been modified and update the display."""
        if not self.log_file or not os.path.exists(self.log_file):
            return

        try:
            current_modified = os.path.getmtime(self.log_file)
            current_size = os.path.getsize(self.log_file)

            # Check if file was modified or size increased
            if current_modified > self._last_modified or current_size > self._last_size:
                self._last_modified = current_modified
                self._last_size = current_size
                self._load_new_content()
        except (OSError, FileNotFoundError):
            pass

        # Schedule next check
        if self.text_area and self.text_area.winfo_exists():
            self.text_area.after(check_interval, self._check_for_updates)

    def _load_new_content(self):
        """Load only the new content from the log file."""
        try:
            with open(self.log_file, "r") as f:
                current_content = f.read()

            # Get current displayed content
            self.text_area.config(state="normal")
            current_displayed = self.text_area.get(1.0, tk.END).rstrip("\n")

            # Find the new content by comparing
            if current_displayed != current_content.rstrip("\n"):
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, current_content)
                # Scroll to the end
                self.text_area.see(tk.END)

            self.text_area.config(state="disabled")
        except Exception as e:
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, f"Error reading log file: {e}\n")
            self.text_area.config(state="disabled")

    def log_message(self, message):
        """Programmatically add a log message to the display."""
        if self.text_area:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.text_area.config(state="normal")
            self.text_area.insert(tk.END, formatted_message)
            self.text_area.see(tk.END)
            self.text_area.config(state="disabled")
