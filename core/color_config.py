"""
Color Configuration Manager

This module provides a ColorConfig class that manages the loading,
saving, and application of color configurations for application modules.
"""

import json
import os
from typing import Dict, Optional


class ColorConfig:
    """
    Manages color configuration for application modules.
    
    Supports loading from JSON files, saving changes, and applying
    colors to registered modules.
    """
    
    # Use absolute path from the application root directory
    # This ensures the config is found regardless of where the app is run from
    APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEFAULT_CONFIG_PATH = os.path.join(
        APP_ROOT,
        "config", 
        "colors.json"
    )
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the color configuration manager.
        
        Args:
            config_path: Path to the color configuration JSON file.
                        If None, uses the default path.
        """
        self.config_path = (
            config_path or self.DEFAULT_CONFIG_PATH
        )
        self.config: Dict = {}
        self.module_colors: Dict[str, Dict[str, str]] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """
        Load color configuration from the JSON file.
        Creates a default configuration if the file doesn't exist.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
                self.module_colors = self.config.get("modules", {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading color config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create and save a default color configuration."""
        self.config = {
            "version": "1.0",
            "description": "Color configuration for application modules",
            "modules": {},
            "window": {
                "bg_color": "#00c8f9",
                "fg_color": "#ffffff"
            },
            "settings": {
                "auto_apply": True,
                "preview_changes": True
            }
        }
        self.module_colors = {}
        self.save_config()
    
    def save_config(self, path: Optional[str] = None) -> None:
        """
        Save the current color configuration to a JSON file.
        
        Args:
            path: Path to save the config. If None, saves to the original path.
        """
        save_path = path or self.config_path
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Update the modules section with current colors
        self.config["modules"] = self.module_colors
        
        with open(save_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_module_color(self, module_name: str, color_type: str) -> Optional[str]:
        """
        Get a specific color for a module.
        
        Args:
            module_name: Name of the module.
            color_type: Type of color ('bg_color' or 'fg_color').
        
        Returns:
            The color hex string, or None if not found.
        """
        module_config = self.module_colors.get(module_name, {})
        return module_config.get(color_type)
    
    def set_module_color(
        self, 
        module_name: str, 
        color_type: str, 
        color_value: str,
        auto_save: bool = True
    ) -> None:
        """
        Set a specific color for a module.
        
        Args:
            module_name: Name of the module.
            color_type: Type of color ('bg_color' or 'fg_color').
            color_value: The color hex string (e.g., '#FF0000').
            auto_save: Whether to automatically save the config.
        """
        if module_name not in self.module_colors:
            self.module_colors[module_name] = {}
        
        self.module_colors[module_name][color_type] = color_value
        
        if auto_save:
            self.save_config()
    
    def get_all_colors(self) -> Dict[str, Dict[str, str]]:
        """
        Get all module color configurations.
        
        Returns:
            Dictionary mapping module names to their color configurations.
        """
        return self.module_colors.copy()
    
    def get_module_colors(self, module_name: str) -> Dict[str, str]:
        """
        Get all colors for a specific module.
        
        Args:
            module_name: Name of the module.
        
        Returns:
            Dictionary with 'bg_color' and 'fg_color' keys.
        """
        return self.module_colors.get(module_name, {}).copy()
    
    def register_module(
        self,
        module_name: str,
        default_bg: str = "#ffffff",
        default_fg: str = "#000000"
    ) -> None:
        """
        Register a new module with default colors if not already registered.
        Uses theme colors from module.THEME if available.
        
        Args:
            module_name: Name of the module to register.
            default_bg: Default background color.
            default_fg: Default foreground color.
        """
        # Theme colors for known modules
        module_themes = {
            "Dashboard": {"bg_color": "#ffffff", "fg_color": "#2c3e50"},
            "System Status": {"bg_color": "#1a1a2e", "fg_color": "#00d4ff"},
            "Git Manager": {"bg_color": "#0d1117", "fg_color": "#58a6ff"},
            "Log": {"bg_color": "#000000", "fg_color": "#00ff00"},
        }
        
        # Use theme colors if available for this module
        theme_colors = module_themes.get(module_name, {})
        theme_bg = theme_colors.get("bg_color", default_bg)
        theme_fg = theme_colors.get("fg_color", default_fg)
        
        if module_name not in self.module_colors:
            # Only set defaults if module doesn't exist in config
            self.module_colors[module_name] = {
                "bg_color": theme_bg,
                "fg_color": theme_fg
            }
            self.save_config()
    
    def apply_colors_to_module(self, module) -> None:
        """
        Apply stored colors to a module instance.
        
        Args:
            module: Module instance that has bg_color and fg_color attributes.
        """
        module_name = getattr(module, 'name', None)
        
        # Handle modules where name is a property/method
        if callable(module_name):
            module_name = module_name()
        
        if not module_name:
            return
        
        colors = self.get_module_colors(module_name)
        
        if 'bg_color' in colors:
            module.bg_color = colors['bg_color']
        if 'fg_color' in colors:
            module.fg_color = colors['fg_color']
    
    def get_applied_colors(self) -> Dict[str, Dict[str, str]]:
        """
        Get the current configuration of all module colors.
        
        Returns:
            Dictionary mapping module names to their color configurations.
        """
        return self.config.get("modules", {})
    
    def reset_to_defaults(self) -> None:
        """Reset all colors to default values and save."""
        self.module_colors = {}
        self.config["modules"] = {}
        # Reset window colors
        self.config["window"] = {
            "bg_color": "#00c8f9",
            "fg_color": "#ffffff"
        }
        self.save_config()
    
    def get_settings(self) -> Dict:
        """Get the settings section of the configuration."""
        return self.config.get("settings", {})
    
    def get_window_colors(self) -> Dict[str, str]:
        """
        Get window colors.
        
        Returns:
            Dictionary with 'bg_color' and 'fg_color' keys.
        """
        return self.config.get("window", {"bg_color": "#00c8f9", "fg_color": "#ffffff"}).copy()
    
    def set_window_color(self, color_type: str, color_value: str, auto_save: bool = True) -> None:
        """
        Set a window color.
        
        Args:
            color_type: Type of color ('bg_color' or 'fg_color').
            color_value: The color hex string (e.g., '#FF0000').
            auto_save: Whether to automatically save the config.
        """
        if "window" not in self.config:
            self.config["window"] = {"bg_color": "#00c8f9", "fg_color": "#ffffff"}
        
        self.config["window"][color_type] = color_value
        
        if auto_save:
            self.save_config()
    
    def update_settings(self, settings: Dict) -> None:
        """
        Update the settings section.
        
        Args:
            settings: Dictionary of settings to update.
        """
        if "settings" not in self.config:
            self.config["settings"] = {}
        self.config["settings"].update(settings)
        self.save_config()


# Singleton instance for easy access
_color_config_instance: Optional[ColorConfig] = None


def get_color_config(config_path: Optional[str] = None) -> ColorConfig:
    """
    Get the singleton ColorConfig instance.
    
    Args:
        config_path: Optional path to the config file.
    
    Returns:
        The ColorConfig singleton instance.
    """
    global _color_config_instance
    if _color_config_instance is None:
        _color_config_instance = ColorConfig(config_path)
    return _color_config_instance


def reset_color_config() -> None:
    """Reset the singleton instance (useful for testing)."""
    global _color_config_instance
    _color_config_instance = None

