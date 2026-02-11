"""
System Status Widgets with Progress Bars

Provides system monitoring widgets with visual progress bars
showing usage percentages and current/max values.
"""
import tkinter as tk
import psutil


class BaseWidget:
    """Base class for system status widgets."""
    
    def __init__(self, parent, title, update_interval=1000):
        self.title = title
        self.update_interval = update_interval
        self.frame = tk.Frame(parent, relief="ridge", borderwidth=2)
        # NOTE: Do NOT pack or grid the frame here - parent will handle it
        
        # Header
        self.header = tk.Label(
            self.frame,
            text=self.title,
            font=("Helvetica", 12, "bold")
        )
        self.header.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Progress bar canvas
        self.bar_canvas = tk.Canvas(
            self.frame,
            height=20,
            bg="#333333",
            highlightthickness=0
        )
        self.bar_canvas.pack(fill="x", padx=10, pady=5)
        
        # Value label
        self.label = tk.Label(
            self.frame,
            text="",
            font=("Helvetica", 10)
        )
        self.label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Store colors for theming
        self._bar_bg = "#333333"
        self._bar_fill = "#00d4ff"
    
    def set_colors(self, bg_color, fg_color, accent_color):
        """Apply theme colors to the widget."""
        self.frame.configure(bg=bg_color)
        self.header.configure(bg=bg_color, fg=fg_color)
        self.label.configure(bg=bg_color, fg=fg_color)
        self.bar_canvas.configure(bg=self._darken_color(bg_color, 0.2))
        self._bar_fill = accent_color or fg_color
    
    def _darken_color(self, hex_color, factor):
        """Darken a hex color by a factor."""
        try:
            hex_color = hex_color.lstrip("#")
            r = max(0, int(hex_color[0:2], 16) * (1 - factor))
            g = max(0, int(hex_color[2:4], 16) * (1 - factor))
            b = max(0, int(hex_color[4:6], 16) * (1 - factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return "#333333"
    
    def _draw_progress_bar(self, percentage, max_text="100%"):
        """Draw a progress bar on the canvas."""
        self.bar_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.bar_canvas.winfo_width()
        height = 20
        
        if width < 10:
            return  # Canvas not ready yet
        
        # Draw background
        self.bar_canvas.create_rectangle(
            0, 0, width, height,
            fill=self._darken_color(
                self.frame.cget('bg'), 0.2
            ) if self.frame.cget('bg') else "#333333",
            outline=""
        )
        
        # Draw fill
        fill_width = int(width * percentage / 100)
        if fill_width > 0:
            self.bar_canvas.create_rectangle(
                0, 0, fill_width, height,
                fill=self._bar_fill,
                outline=""
            )
        
        # Draw percentage text
        self.bar_canvas.create_text(
            width / 2, height / 2,
            text=f"{percentage:.1f}%",
            fill="#ffffff" if percentage > 50 else "#000000",
            font=("Helvetica", 8, "bold")
        )
    
    def start(self):
        """Start the update loop."""
        self.update()
    
    def update(self):
        """Override this in subclasses."""
        pass


class CPUWidget(BaseWidget):
    """CPU usage widget with progress bar."""
    
    title = "CPU"
    
    def __init__(self, parent):
        super().__init__(parent, self.title, update_interval=1000)
        self.start()
    
    def update(self):
        """Update CPU usage display."""
        cpu_percent = psutil.cpu_percent(interval=0)
        self._draw_progress_bar(cpu_percent)
        self.label.config(
            text=f"Usage: {cpu_percent:.1f}% | Cores: {psutil.cpu_count()}"
        )
        self.frame.after(1000, self.update)


class MemoryWidget(BaseWidget):
    """Memory usage widget with progress bar."""
    
    title = "Memory"
    
    def __init__(self, parent):
        super().__init__(parent, self.title, update_interval=2000)
        self.start()
    
    def update(self):
        """Update memory usage display."""
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024 ** 3)
        total_gb = mem.total / (1024 ** 3)
        percentage = mem.percent
        
        self._draw_progress_bar(percentage)
        self.label.config(
            text=f"Used: {used_gb:.1f}GB / {total_gb:.1f}GB"
        )
        self.frame.after(2000, self.update)


class DiskWidget(BaseWidget):
    """Disk usage widget with progress bar."""
    
    title = "Disk"
    
    def __init__(self, parent):
        super().__init__(parent, self.title, update_interval=5000)
        self.start()
    
    def update(self):
        """Update disk usage display."""
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024 ** 3)
        total_gb = disk.total / (1024 ** 3)
        percentage = (disk.used / disk.total) * 100
        
        self._draw_progress_bar(percentage)
        self.label.config(
            text=f"Used: {used_gb:.1f}GB / {total_gb:.1f}GB"
        )
        self.frame.after(5000, self.update)
