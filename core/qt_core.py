import tkinter as tk
from tkinter import ttk
import math
from core.color_config import get_color_config


class ColorWheelPicker:
    """
    A beautiful circular color wheel picker using HSV color space.
    Click on the wheel to select colors with smooth transitions.
    """
    
    def __init__(
        self,
        parent,
        initial_color="#ffffff",
        size=200,
        callback=None
    ):
        """
        Initialize the color wheel picker.
        
        Args:
            parent: Parent widget.
            initial_color: Initial color in hex format.
            size: Diameter of the color wheel.
            callback: Function to call with selected color.
        """
        self.parent = parent
        self.size = size
        self.callback = callback
        self.initial_color = initial_color
        self.selected_color = initial_color
        
        # HSV values for initial color
        self.hue = 0
        self.saturation = 0
        self.value = 1
        
        # Convert initial hex to HSV
        self._hex_to_hsv(initial_color)
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Color Wheel Picker")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#2c3e50")
        
        # Center the dialog
        dialog_x = parent.winfo_x() + (parent.winfo_width() - size - 100) // 2
        dialog_y = parent.winfo_y() + (parent.winfo_height() - size - 150) // 2
        self.dialog.geometry(f"{size + 60}x{size + 120}+{dialog_x}+{dialog_y}")
        
        # Main container
        main_frame = tk.Frame(self.dialog, bg="#2c3e50")
        main_frame.pack(padx=20, pady=20)
        
        # Create the color wheel canvas
        self.canvas = tk.Canvas(
            main_frame,
            width=size,
            height=size,
            bg="#2c3e50",
            highlightthickness=0,
            cursor="crosshair",
            relief="flat"
        )
        self.canvas.pack(pady=(0, 15))
        
        # Draw the color wheel using pure Tkinter
        self._draw_color_wheel_tkinter()
        
        # Current color preview
        preview_frame = tk.Frame(main_frame, bg="#2c3e50")
        preview_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            preview_frame,
            text="Selected:",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Arial", 10, "bold")
        ).pack(side="left")
        
        self.preview_box = tk.Frame(
            preview_frame,
            width=60,
            height=25,
            bg=self.selected_color,
            relief="sunken",
            borderwidth=2
        )
        self.preview_box.pack(side="left", padx=10)
        self.preview_box.pack_propagate(False)
        
        # Hex color entry
        entry_frame = tk.Frame(main_frame, bg="#2c3e50")
        entry_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            entry_frame,
            text="Hex:",
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Arial", 10)
        ).pack(side="left")
        
        self.hex_var = tk.StringVar(value=self.initial_color)
        self.hex_entry = tk.Entry(
            entry_frame,
            textvariable=self.hex_var,
            font=("Arial", 10, "bold"),
            width=10,
            justify="center",
            bg="#ffffff",
            fg="#000000"
        )
        self.hex_entry.pack(side="left", padx=5)
        self.hex_var.trace_add("write", self._on_hex_change)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2c3e50")
        btn_frame.pack(pady=(0, 0))
        
        ok_btn = tk.Button(
            btn_frame,
            text="✓ Apply",
            bg="#27ae60",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            width=10,
            relief="flat",
            cursor="hand2",
            command=self._on_ok
        )
        ok_btn.pack(side="left", padx=8)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="✗ Cancel",
            bg="#e74c3c",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            width=10,
            relief="flat",
            cursor="hand2",
            command=self._on_cancel
        )
        cancel_btn.pack(side="left", padx=8)
        
        # Bind canvas click
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        
        # Update indicator
        self._update_indicator()
        self._update_preview()
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def _hex_to_hsv(self, hex_color):
        """Convert hex color to HSV values."""
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            diff = max_val - min_val
            
            # Hue
            if diff == 0:
                h = 0
            elif max_val == r:
                h = (60 * ((g - b) / diff) + 360) % 360
            elif max_val == g:
                h = (60 * ((b - r) / diff) + 120) % 360
            else:
                h = (60 * ((r - g) / diff) + 240) % 360
            
            # Saturation
            if max_val == 0:
                s = 0
            else:
                s = diff / max_val
            
            # Value
            v = max_val
            
            self.hue = h
            self.saturation = s
            self.value = v
        except (ValueError, IndexError):
            self.hue = 0
            self.saturation = 0
            self.value = 1
    
    def _hsv_to_hex(self, h, s, v):
        """Convert HSV to hex color."""
        r, g, b = hsv_to_rgb(h / 360, s, v)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    
    def _draw_color_wheel_tkinter(self):
        """Draw color wheel using pure Tkinter canvas arcs."""
        center = self.size // 2
        radius = (self.size // 2) - 5
        
        # Draw color wheel using overlapping arcs
        # Each arc represents a segment of the hue spectrum
        num_segments = 360
        
        for i in range(num_segments):
            # Calculate start and end angles
            start_angle = i
            end_angle = i + 1
            
            # Calculate saturation for this ring
            saturation = 1.0
            
            # Get color for this hue
            r, g, b = hsv_to_rgb(i / 360, saturation, 1.0)
            color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
            
            # Draw arc at outer edge
            self.canvas.create_arc(
                center - radius, center - radius,
                center + radius, center + radius,
                start=start_angle - 90,
                end=end_angle - 90,
                fill=color,
                outline=color,
                style=tk.ARC,
                width=radius
            )
        
        # Draw saturation gradient rings
        for s in [0.75, 0.5, 0.25]:
            inner_radius = int(radius * s)
            
            for i in range(0, 360, 10):
                r, g, b = hsv_to_rgb(i / 360, s, 1.0)
                color = f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
                
                self.canvas.create_arc(
                    center - inner_radius, center - inner_radius,
                    center + inner_radius, center + inner_radius,
                    start=i - 90,
                    end=i + 10,
                    fill=color,
                    outline=color,
                    style=tk.ARC,
                    width=2
                )
        
        # Draw center white dot (full saturation = 0)
        self.canvas.create_oval(
            center - 8, center - 8,
            center + 8, center + 8,
            fill="#ffffff",
            outline="#bdc3c7",
            width=1
        )
        
        # Draw outer ring
        self.canvas.create_oval(
            center - radius - 2, center - radius - 2,
            center + radius + 2, center + radius + 2,
            outline="#34495e",
            width=4
        )
    
    def _update_indicator(self):
        """Update the color selection indicator."""
        center = self.size // 2
        radius = (self.size // 2) - 5
        
        # Calculate indicator position based on current HSV
        angle = math.radians(self.hue)
        dist = self.saturation * radius
        
        x = center + dist * math.cos(angle)
        y = center + dist * math.sin(angle)
        
        # Remove old indicator
        self.canvas.delete("indicator")
        
        # Draw selection indicator
        self.canvas.create_oval(
            x - 10, y - 10, x + 10, y + 10,
            outline="#ffffff",
            width=3,
            tags="indicator"
        )
        self.canvas.create_oval(
            x - 6, y - 6, x + 6, y + 6,
            outline="#000000",
            width=2,
            tags="indicator"
        )
        self.canvas.create_oval(
            x - 3, y - 3, x + 3, y + 3,
            fill=self.selected_color,
            outline="",
            tags="indicator"
        )
    
    def _on_canvas_click(self, event):
        """Handle canvas click to select color."""
        self._select_color(event.x, event.y)
    
    def _on_canvas_drag(self, event):
        """Handle canvas drag to select color."""
        self._select_color(event.x, event.y)
    
    def _select_color(self, x, y):
        """Select color at the given position."""
        center = self.size // 2
        radius = (self.size // 2) - 5
        
        dx = x - center
        dy = y - center
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance <= radius:
            # Calculate HSV
            angle = math.atan2(dy, dx)
            hue = (angle * 180 / math.pi + 180) % 360
            saturation = min(distance / radius, 1.0)
            
            self.hue = hue
            self.saturation = saturation
            
            # Convert to hex
            self.selected_color = self._hsv_to_hex(hue, saturation, 1.0)
            
            # Update UI
            self.hex_var.set(self.selected_color)
            self._update_preview()
            self._update_indicator()
    
    def _on_hex_change(self, *args):
        """Handle hex color entry changes."""
        hex_color = self.hex_var.get()
        if hex_color.startswith("#") and len(hex_color) == 7:
            try:
                # Validate hex color
                int(hex_color[1:], 16)
                self.selected_color = hex_color
                self._hex_to_hsv(hex_color)
                self._update_preview()
                self._update_indicator()
            except ValueError:
                pass
    
    def _update_preview(self):
        """Update the color preview."""
        try:
            self.preview_box.config(bg=self.selected_color)
        except tk.TclError:
            pass
    
    def _get_luminance(self, hex_color):
        """Calculate luminance of a hex color."""
        try:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            return 0.299 * r + 0.587 * g + 0.114 * b
        except (ValueError, IndexError):
            return 1.0
    
    def _on_ok(self):
        """Handle OK button click."""
        if self.callback:
            self.callback(self.selected_color)
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.selected_color = self.initial_color
        self.dialog.destroy()


def hsv_to_rgb(h, s, v):
    """
    Convert HSV color to RGB.
    
    Args:
        h: Hue (0-1)
        s: Saturation (0-1)
        v: Value (0-1)
    
    Returns:
        Tuple of (r, g, b) values in range 0-1
    """
    if s == 0:
        return v, v, v
    
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    
    i = i % 6
    
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    
    return v, v, v


class App:

    def __init__(
        self,
        title="Modular App",
        single=True,
        bg_color=None
    ):
        self.root = tk.Tk()
        self.root.title(title)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size (80% of screen, minimum 800x600)
        min_width, min_height = 800, 600
        window_width = max(min_width, int(screen_width * 0.8))
        window_height = max(min_height, int(screen_height * 0.8))
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(min_width, min_height)
        
        # Initialize color configuration
        self.color_config = get_color_config()
        
        # Load window background color from config
        window_colors = self.color_config.get_window_colors()
        self.bg_color = bg_color or window_colors.get("bg_color", "#00c8f9")
        self.fg_color = window_colors.get("fg_color", "#ffffff")
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
        self.modules = []
        self.enabled_modules = []  # Track enabled/disabled modules
        self.single = single
        self.active_module = None

        # Fonts and styles
        self.button_font = ("Helvetica", 12, "bold")

        # Register all existing modules with color config
        self._register_modules_with_color_config()

        # Create Menu Bar
        self._create_menu_bar()

        # Sidebar only in grid/dashboard mode
        self.sidebar = None
        if not self.single:
            self.sidebar = tk.Frame(self.root, width=220, bg="#2c3e50")
            self.sidebar.pack(side="left", fill="y")

        # Content area
        self.content = tk.Frame(self.root, bg="white")
        self.content.pack(side="right", expand=True, fill="both")

        # Notebook for tab mode
        self.notebook = None
        if self.single:
            self.notebook = ttk.Notebook(self.content)
            self.notebook.pack(expand=True, fill="both")

        # Color customization panel reference
        self.color_panel = None
        self._is_color_panel_open = False

    def _create_menu_bar(self):
        """Create the menu bar with Modules and Colors options."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Modules menu with toggle checkboxes
        modules_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Modules", menu=modules_menu)
        
        # Store references to checkbuttons for state management
        self.module_checkbuttons = {}
        
        for module in self.modules:
            module_name = getattr(module, 'name', None)
            if callable(module_name):
                module_name = module_name()
            
            if module_name:
                # Default to enabled
                var = tk.IntVar(value=1)
                self.module_checkbuttons[module_name] = var
                
                modules_menu.add_checkbutton(
                    label=module_name,
                    variable=var,
                    command=self._on_module_toggle
                )

        # Colors menu
        colors_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Colors", menu=colors_menu)
        colors_menu.add_command(
            label="Customize Colors...",
            command=self._toggle_color_panel
        )
    
    def _on_module_toggle(self):
        """Handle module toggle - rebuild UI."""
        # Rebuild navigation to reflect changes
        self.build_navigation()

    def _toggle_color_panel(self):
        """Toggle the color customization panel."""
        if self._is_color_panel_open:
            self._close_color_panel()
        else:
            self._open_color_panel()

    def _open_color_panel(self):
        """Open the color customization panel."""
        if self.color_panel is None:
            self.color_panel = ColorCustomizationPanel(
                self.root,
                self,
                on_close=self._close_color_panel
            )

        self.color_panel.show()
        self._is_color_panel_open = True

    def _close_color_panel(self):
        """Close the color customization panel."""
        if self.color_panel:
            self.color_panel.hide()
            self.color_panel = None
        self._is_color_panel_open = False

    def _register_modules_with_color_config(self):
        """Register all modules with the color configuration system."""
        for module in self.modules:
            module_name = getattr(module, 'name', None)

            # Handle modules where name is a property/method
            if callable(module_name):
                module_name = module_name()

            if module_name:
                # Get default colors from module
                default_bg = getattr(module, 'bg_color', '#ffffff')
                default_fg = getattr(module, 'fg_color', '#000000')

                # Register with color config
                self.color_config.register_module(
                    module_name,
                    default_bg=default_bg,
                    default_fg=default_fg
                )

    def register_module(self, module_or_list):
        """
        Accepts either a single module instance or a list of module instances.
        Also registers modules with color config.
        """
        if isinstance(module_or_list, list):
            self.modules.extend(module_or_list)
        else:
            self.modules.append(module_or_list)

        # Register new modules with color config
        self._register_modules_with_color_config()

    def _apply_colors_to_module(self, module):
        """
        Apply stored colors to a module instance.

        Args:
            module: Module instance.
        """
        module_name = getattr(module, 'name', None)

        # Handle modules where name is a property/method
        if callable(module_name):
            module_name = module_name()

        if module_name:
            colors = self.color_config.get_module_colors(module_name)

            if 'bg_color' in colors:
                module.bg_color = colors['bg_color']
            if 'fg_color' in colors:
                module.fg_color = colors['fg_color']

    def build_navigation(self):
        """Build navigation based on enabled/disabled modules."""
        if self.single:
            self.build_tabs()
        else:
            # Sidebar buttons display module names
            for module in self.modules:
                module_name = getattr(module, "name", None)
                if callable(module_name):
                    module_name = module_name()
                
                # Check if module is enabled
                if module_name in self.module_checkbuttons:
                    if self.module_checkbuttons[module_name].get() == 0:
                        continue  # Skip disabled modules
                
                # Apply colors to module
                self._apply_colors_to_module(module)

                btn = tk.Button(
                    self.sidebar,
                    text=module_name,
                    font=self.button_font,
                    fg="white",
                    bg="#34495e",
                    activebackground="#1abc9c",
                    activeforeground="white",
                    relief="flat",
                    command=lambda m=module: self.show_module(m)
                )
                btn.pack(fill="x", pady=5, padx=5)

            # Show first enabled module by default
            enabled_modules = []
            for m in self.modules:
                m_name = getattr(m, 'name', None)
                if callable(m_name):
                    m_name = m_name()
                if m_name and m_name in self.module_checkbuttons:
                    if self.module_checkbuttons[m_name].get() == 1:
                        enabled_modules.append(m)
            
            if enabled_modules:
                self.show_module(enabled_modules[0])

    def show_module(self, module):
        # Apply colors to module before showing
        self._apply_colors_to_module(module)

        # Remove previous content
        for widget in self.content.winfo_children():
            widget.destroy()

        # Build module in content frame
        module.build(self.content)
        self.active_module = module

    def build_tabs(self):
        """Tabs layout with up to 6 modules per tab"""
        modules_per_tab = 6
        num_tabs = math.ceil(len(self.modules) / modules_per_tab)

        for tab_idx in range(num_tabs):
            tab_frame = tk.Frame(self.notebook, bg="#ecf0f1")
            self.notebook.add(tab_frame, text=f"Tab {tab_idx + 1}")

            start = tab_idx * modules_per_tab
            end = start + modules_per_tab
            for idx, module in enumerate(self.modules[start:end]):
                # Apply colors to module
                self._apply_colors_to_module(module)

                frame = tk.Frame(
                    tab_frame,
                    relief="ridge",
                    borderwidth=1,
                    bg=module.bg_color if hasattr(module, 'bg_color') else "white"
                )
                frame.grid(
                    row=idx // 3,
                    column=idx % 3,
                    padx=10,
                    pady=10,
                    sticky="nsew"
                )
                # Make grid expandable
                row = idx // 3
                col = idx % 3
                tab_frame.rowconfigure(row, weight=1)
                tab_frame.columnconfigure(col, weight=1)
                module.build(frame)

    def run(self):
        self.build_navigation()
        self.root.mainloop()


class ColorCustomizationPanel:
    """
    Panel that displays all registered modules and allows
    customization of their colors.
    """

    def __init__(
        self,
        parent,
        app,
        on_close=None,
        width=300,
        height=400
    ):
        """
        Initialize the color customization panel.

        Args:
            parent: Parent widget.
            app: Reference to the main App instance.
            on_close: Callback function when panel is closed.
            width: Width of the panel.
            height: Height of the panel.
        """
        self.parent = parent
        self.app = app
        self.on_close = on_close
        self.width = width
        self.height = height
        self.color_vars = {}
        self.entries = {}

        # Create the panel (initially hidden)
        self._create_panel()

    def _create_panel(self):
        """Create the customization panel."""
        # Main frame with border and shadow effect
        self.frame = tk.Frame(
            self.parent,
            bg="#ecf0f1",
            width=self.width,
            height=self.height,
            relief="raised",
            borderwidth=2
        )

        # Title bar
        self.title_bar = tk.Frame(self.frame, bg="#34495e", height=30)
        self.title_bar.pack(fill="x")
        self.title_bar.pack_propagate(False)

        # Title label
        self.title_label = tk.Label(
            self.title_bar,
            text="Module Colors",
            bg="#34495e",
            fg="#ffffff",
            font=("Arial", 10, "bold")
        )
        self.title_label.pack(side="left", padx=10)

        # Close button
        self.close_btn = tk.Button(
            self.title_bar,
            text="X",
            bg="#34495e",
            fg="#ffffff",
            font=("Arial", 9, "bold"),
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            command=self.hide
        )
        self.close_btn.pack(side="right", padx=5, pady=2)

        # Scrollable canvas for modules
        self.canvas = tk.Canvas(self.frame, bg="#ecf0f1")
        self.scrollbar = tk.Scrollbar(
            self.frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ecf0f1")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack scrollable area
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", expand=True, fill="both")

        # Add module color controls
        self._populate_modules()

    def _populate_modules(self):
        """Populate the panel with registered modules."""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.color_vars.clear()
        self.entries.clear()

        # Add Window Colors section
        self._create_window_section(self.scrollable_frame)

        # Separator
        separator = tk.Frame(self.scrollable_frame, bg="#bdc3c7", height=1)
        separator.pack(fill="x", padx=15, pady=10)

        # Add section for each module
        for module in self.app.modules:
            module_name = getattr(module, 'name', None)

            # Handle modules where name is a property/method
            if callable(module_name):
                module_name = module_name()

            if not module_name:
                continue

            # Create module section
            self._create_module_section(
                self.scrollable_frame,
                module_name,
                module
            )

        # Apply & Restart button
        self.apply_btn = tk.Button(
            self.scrollable_frame,
            text="✓ Apply & Restart",
            bg="#27ae60",
            fg="#ffffff",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._apply_and_restart
        )
        self.apply_btn.pack(pady=15, padx=20, fill="x")

        # Reset button
        self.reset_btn = tk.Button(
            self.scrollable_frame,
            text="Reset to Defaults",
            bg="#e74c3c",
            fg="#ffffff",
            font=("Arial", 9),
            relief="flat",
            cursor="hand2",
            command=self._reset_colors
        )
        self.reset_btn.pack(pady=(0, 15), padx=20, fill="x")

    def _create_window_section(self, parent):
        """Create window color customization section."""
        # Window header
        header = tk.Label(
            parent,
            text="Window Colors",
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Arial", 12, "bold")
        )
        header.pack(anchor="w", padx=15, pady=(15, 5))

        # Get current window colors
        window_colors = self.app.color_config.get_window_colors()
        window_bg = window_colors.get("bg_color", "#00c8f9")
        window_fg = window_colors.get("fg_color", "#ffffff")

        # Container for color controls
        container = tk.Frame(parent, bg="#ecf0f1")
        container.pack(fill="x", padx=15, pady=5)

        # Window background color
        self._create_color_entry(
            container,
            "Background:",
            None,  # No module, special case
            "window_bg",
            row=0,
            current_color=window_bg
        )

        # Window foreground color
        self._create_color_entry(
            container,
            "Text:",
            None,  # No module, special case
            "window_fg",
            row=1,
            current_color=window_fg
        )

    def _create_module_section(self, parent, module_name, module):
        """
        Create a color customization section for a module.

        Args:
            parent: Parent widget.
            module_name: Name of the module.
            module: Module instance.
        """
        # Module header
        header = tk.Label(
            parent,
            text=module_name,
            bg="#ecf0f1",
            fg="#2c3e50",
            font=("Arial", 11, "bold")
        )
        header.pack(anchor="w", padx=15, pady=(15, 5))

        # Container for color controls
        container = tk.Frame(parent, bg="#ecf0f1")
        container.pack(fill="x", padx=15, pady=5)

        # Background color
        self._create_color_entry(
            container,
            "Background:",
            module,
            "bg_color",
            row=0
        )

        # Foreground color
        self._create_color_entry(
            container,
            "Foreground:",
            module,
            "fg_color",
            row=1
        )

        # Separator
        separator = tk.Frame(parent, bg="#bdc3c7", height=1)
        separator.pack(fill="x", padx=15, pady=10)

    def _create_color_entry(
        self,
        parent,
        label_text,
        module,
        color_attr,
        row,
        current_color=None
    ):
        """
        Create a color input entry with preview.

        Args:
            parent: Parent widget.
            label_text: Label text for the color type.
            module: Module instance (None for window colors).
            color_attr: Attribute name ('bg_color' or 'fg_color').
            row: Grid row position.
            current_color: Current color value (for window colors).
        """
        # Label
        label = tk.Label(
            parent,
            text=label_text,
            bg="#ecf0f1",
            fg="#7f8c8d",
            font=("Arial", 9),
            width=12,
            anchor="e"
        )
        label.grid(row=row, column=0, padx=(0, 5), pady=2)

        # Get current color value
        if current_color is None:
            current_color = getattr(module, color_attr, "#ffffff")

        # Color variable - use special key for window colors
        if module is None:
            key = f"window_{color_attr}"
        else:
            key = f"{module.name}_{color_attr}"
        
        color_var = tk.StringVar(value=current_color)
        self.color_vars[key] = color_var

        # Color entry
        entry = tk.Entry(
            parent,
            textvariable=color_var,
            font=("Arial", 9),
            width=10,
            bg="#ffffff",
            fg="#2c3e50"
        )
        entry.grid(row=row, column=1, padx=5, pady=2)
        self.entries[key] = entry

        # Color preview button
        preview_btn = tk.Button(
            parent,
            bg=current_color,
            width=3,
            relief="flat",
            cursor="hand2",
            command=lambda: self._pick_color(
                color_var,
                preview_btn,
                key
            )
        )
        preview_btn.grid(row=row, column=2, padx=(5, 0), pady=2)

    def _pick_color(self, color_var, preview_btn, key):
        """
        Open color picker dialog using tkcolorpicker.

        Args:
            color_var: StringVar to store the selected color.
            preview_btn: Button to update with selected color.
            key: Key to identify the color entry.
        """
        try:
            from tkcolorpicker import askcolor
        except ImportError:
            # Fallback to manual picker
            self._manual_color_picker(color_var)
            return
        
        # Get current color
        current_color = color_var.get()
        
        # Convert to RGB tuple if needed
        try:
            if current_color.startswith('#'):
                r = int(current_color[1:3], 16)
                g = int(current_color[3:5], 16)
                b = int(current_color[5:7], 16)
                initial = (r, g, b)
            else:
                initial = (255, 255, 255)
        except Exception:
            initial = (255, 255, 255)
        
        # Open color picker dialog
        color = askcolor(
            color=initial,
            title="Choose Color",
            parent=self.parent
        )
        
        if color and color[1]:  # color is ((r,g,b), hex)
            hex_color = color[1]
            color_var.set(hex_color)
            
            # Update preview button
            try:
                preview_btn.config(bg=hex_color)
                self.entries[key].config(bg=hex_color)
            except tk.TclError:
                pass
            
            # Auto-apply if enabled
            if hasattr(self.app, 'color_config'):
                settings = self.app.color_config.get_settings()
                if settings.get('auto_apply', True):
                    self._apply_colors()

    def _manual_color_picker(self, color_var):
        """
        Fallback manual color picker dialog.

        Args:
            color_var: StringVar to store the selected color.

        Returns:
            Tuple with (name, hex_color) or None if cancelled.
        """
        # Create color picker dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Choose Color")
        dialog.transient(self.parent)
        dialog.grab_set()

        # Center the dialog
        dialog.geometry("+{}+{}".format(
            self.parent.winfo_x() + 100,
            self.parent.winfo_y() + 100
        ))

        # Color preview
        preview = tk.Label(dialog, bg=color_var.get(), width=40, height=3)
        preview.pack(padx=20, pady=(20, 10))

        # Color entry
        entry = tk.Entry(dialog, textvariable=color_var, font=("Arial", 12))
        entry.pack(padx=20, pady=5)

        # Preview on change
        def on_change(*args):
            try:
                preview.config(bg=color_var.get())
            except tk.TclError:
                pass

        color_var.trace_add("write", on_change)

        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)

        result = [None]

        def on_ok():
            result[0] = ("Custom", color_var.get())
            dialog.destroy()

        def on_cancel():
            result[0] = None
            dialog.destroy()

        ok_btn = tk.Button(
            btn_frame,
            text="OK",
            bg="#27ae60",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=on_ok
        )
        ok_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            bg="#e74c3c",
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=on_cancel
        )
        cancel_btn.pack(side="left", padx=10)

        # Wait for dialog
        dialog.wait_window()

        return result[0]

    def show(self):
        """Show the panel."""
        self.frame.place(
            x=50,
            y=40,
            anchor="nw"
        )
        self._populate_modules()

    def hide(self):
        """Hide the panel."""
        if self.frame and self.frame.winfo_exists():
            self.frame.place_forget()
        if self.on_close:
            # Check if already processing a close to avoid recursion
            self.on_close = None

    def destroy(self):
        """Destroy the panel."""
        self.frame.destroy()

    def _apply_colors(self):
        """Apply the selected colors to all modules."""
        for key, color_var in self.color_vars.items():
            parts = key.split("_")
            module_name = "_".join(parts[:-1])
            color_attr = "_".join(parts[-1:])

            # Check if this is a window color
            if module_name == "window":
                # Save window color to config
                if hasattr(self.app, 'color_config'):
                    self.app.color_config.set_window_color(
                        color_attr.replace("window_", ""),
                        color_var.get()
                    )
                continue

            # Find the module
            for module in self.app.modules:
                module_n = getattr(module, 'name', None)
                if callable(module_n):
                    module_n = module_n()

                if module_n == module_name:
                    # Update module color
                    setattr(module, color_attr, color_var.get())

                    # Save to config
                    if hasattr(self.app, 'color_config'):
                        self.app.color_config.set_module_color(
                            module_name,
                            color_attr,
                            color_var.get()
                        )

        # Rebuild current module to show changes
        if self.app.active_module:
            self.app.show_module(self.app.active_module)

    def _apply_and_restart(self):
        """Apply colors and restart the application."""
        # Save all colors
        self._apply_colors()
        
        # Close the panel
        self.hide()
        
        # Restart the application
        import sys
        import os
        
        # Destroy the current root
        self.app.root.destroy()
        
        # Reset the color config singleton
        from core.color_config import reset_color_config
        reset_color_config()
        
        # Restart the application
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _reset_colors(self):
        """Reset all colors to defaults."""
        if hasattr(self.app, 'color_config'):
            self.app.color_config.reset_to_defaults()

        # Re-populate with defaults
        self._populate_modules()

        # Rebuild current module
        if self.app.active_module:
            self.app.show_module(self.app.active_module)

