"""
System Status Module - Display CPU, Memory, and Disk usage

A module that displays system resource information:
- CPU widget: Shows CPU usage percentage with progress bar
- Memory widget: Shows memory usage with progress bar
- Disk widget: Shows disk usage with progress bar
"""
import tkinter as tk
import psutil
from .widgets import CPUWidget, MemoryWidget, DiskWidget


class SystemStatusModule:
    """
    System Status module displaying system resource information.
    
    Shows CPU, Memory, and Disk usage with real-time updates
    and visual progress bars.
    """

    name = "System Status"
    
    # Dark tech theme
    THEME = {
        "name": "Dark Tech",
        "bg_color": "#1a1a2e",
        "fg_color": "#00d4ff",
        "accent_color": "#00d4ff",
        "secondary_bg": "#16213e"
    }

    def __init__(
        self,
        app,
        widgets=None,
        rows=2,
        cols=2,
        bg_color=None,
        fg_color=None
    ):
        """
        Initialize the System Status module.

        Args:
            app: Reference to the main App instance.
            widgets: List of widget classes to display.
            rows: Number of rows in the grid layout.
            cols: Number of columns in the grid layout.
            bg_color: Background color (uses theme default if None).
            fg_color: Foreground color (uses theme default if None).
        """
        self.app = app
        self.widgets = widgets if widgets else []
        self.rows = rows
        self.cols = cols
        # Use theme colors if not specified
        self.bg_color = bg_color or self.THEME["bg_color"]
        self.fg_color = fg_color or self.THEME["fg_color"]
        self.accent_color = self.THEME.get("accent_color", fg_color)

    def build(self, parent):
        """Build the System Status UI."""
        # Clear existing content
        for widget in parent.winfo_children():
            widget.destroy()

        # Configure parent background
        parent.configure(bg=self.bg_color)

        # Default widgets if none specified
        display_widgets = self.widgets
        if not display_widgets:
            display_widgets = [CPUWidget, MemoryWidget, DiskWidget]

        for idx, WidgetClass in enumerate(display_widgets):
            r = idx // self.cols
            c = idx % self.cols

            widget_instance = WidgetClass(parent)
            widget_instance.set_colors(
                self.bg_color,
                self.fg_color,
                self.accent_color
            )

            frame = widget_instance.frame
            frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            # Make grid cells expandable
            parent.rowconfigure(r, weight=1)
            parent.columnconfigure(c, weight=1)

