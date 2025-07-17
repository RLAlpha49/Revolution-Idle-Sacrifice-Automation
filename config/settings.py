"""
Configuration settings for Revolution Idle Sacrifice Automation Script.

This module loads user-configurable settings from an external settings file,
allowing users to customize the script behavior even when compiled to an executable.
Settings are loaded from 'user_settings.json' with fallback to default values.
"""

import json
import os
import sys
from typing import Any, Dict


class SettingsLoader:
    """Loads and manages user settings from external configuration file."""

    def __init__(self) -> None:
        self._settings: Dict[str, Any] = {}
        self._load_settings()

    def _get_settings_file_path(self) -> str:
        """Get the path to the user settings file."""
        # Get the directory where the script is running from
        if hasattr(sys, "_MEIPASS"):
            # Running as compiled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        return os.path.join(base_dir, "user_settings.json")

    def _get_default_settings(self) -> Dict[str, Any]:
        """Return default settings values."""
        return {
            "color_tolerance": 15,
            "delay_before_check": 0.02,
            "delay_after_press": 0.02,
            "delay_drag_duration": 0.02,
            "delay_after_drag": 0.11,
            "delay_after_click": 0.01,
            "stop_key": "q",
            "max_zodiac_slots": -1,
            "debug_color_matching": False,
            "message_level": "info",
        }

    def _load_settings(self) -> None:
        """Load settings from external file or create with defaults."""
        settings_file = self._get_settings_file_path()
        defaults = self._get_default_settings()

        try:
            # Try to load existing settings file
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    user_settings = json.load(f)

                # Filter out comment fields (keys starting with _)
                filtered_settings = {
                    k: v for k, v in user_settings.items() if not k.startswith("_")
                }

                # Merge user settings with defaults (in case new settings are added)
                self._settings = defaults.copy()
                self._settings.update(filtered_settings)

                # Save back to ensure all settings are present
                self._save_settings()
            else:
                # Create default settings file
                self._settings = defaults
                self._save_settings()
                print(f"Created default settings file: {settings_file}")
                print("You can modify this file to customize the script behavior.")

        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load settings file: {e}")
            print("Using default settings.")
            self._settings = defaults

    def _save_settings(self) -> None:
        """Save current settings to file."""
        settings_file = self._get_settings_file_path()
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
        except (IOError, OSError) as e:
            print(f"Warning: Could not save settings file: {e}")

    def get(self, key: str) -> Any:
        """Get a setting value."""
        return self._settings.get(key)

    def reload(self) -> None:
        """Reload settings from file."""
        self._load_settings()


# Create global settings loader instance
_settings_loader = SettingsLoader()

# --- Exported Settings ---
# These are the settings that other modules will import

# Color Matching Tolerance
# RGB values can vary slightly due to lighting, compression, etc.
# When clicking on a zodiac slot, the RGB may darken during capture.
# The default value of 15 works well.
# This sets how close colors need to be to match (0 = exact match, higher = more tolerant)
COLOR_TOLERANCE = _settings_loader.get("color_tolerance")

# Delay Timings (in seconds)
# Adjust these if the automation is too fast or too slow for your system/game.
# These are the fastest timings I could get while keeping consistency.
DELAY_BEFORE_CHECK = _settings_loader.get(
    "delay_before_check"
)  # Delay before checking pixel colors in the automation loop
DELAY_AFTER_PRESS = _settings_loader.get(
    "delay_after_press"
)  # Delay immediately after a mouse press
DELAY_DRAG_DURATION = _settings_loader.get(
    "delay_drag_duration"
)  # Duration of the mouse drag action
DELAY_AFTER_DRAG = _settings_loader.get(
    "delay_after_drag"
)  # Delay after completing a drag action
DELAY_AFTER_CLICK = _settings_loader.get(
    "delay_after_click"
)  # Delay after performing a click action

# Automation Exit Key
# The keyboard key that will stop the automation. Default is 'q'.
# Can be a single character (e.g., 'q', 'p') or a special key name
# (e.g., 'esc', 'f1', 'space', 'shift', 'ctrl').
# For a list of special key names, refer to pynput.keyboard.Key documentation.
STOP_KEY = _settings_loader.get("stop_key")

# Multiple Zodiac Slots Configuration
# Maximum number of zodiac slots that can be configured for sacrifice.
# Set this to the number of zodiac slots you want to monitor.
# Set to -1 for unlimited slots, or a positive number to limit the maximum.
# During setup, you can configure fewer slots than this maximum if desired.
MAX_ZODIAC_SLOTS = _settings_loader.get(
    "max_zodiac_slots"
)  # -1 = unlimited slots, or set a positive number to limit

# Debug Color Detection
# Set to True to show detailed color matching information during automation.
# This helps troubleshoot color tolerance issues.
# MESSAGE_LEVEL must be set to 'debug' to see these messages.
# Note: With unlimited zodiac slots, debug output will show all configured slots.
DEBUG_COLOR_MATCHING = _settings_loader.get(
    "debug_color_matching"
)  # Set to True for detailed color matching info

# Message Verbosity
# Set to 'info' for standard messages. Set to 'debug' for more detailed output.
MESSAGE_LEVEL = _settings_loader.get("message_level")  # Options: 'info', 'debug'

# Configuration file name
CONFIG_FILE = "revolution_idle_zodiac_automation_config.json"


def reload_settings() -> None:
    """Reload settings from file and update global variables."""
    # pylint: disable=global-statement
    global COLOR_TOLERANCE, DELAY_BEFORE_CHECK, DELAY_AFTER_PRESS, DELAY_DRAG_DURATION
    global DELAY_AFTER_DRAG, DELAY_AFTER_CLICK, STOP_KEY, MAX_ZODIAC_SLOTS
    global DEBUG_COLOR_MATCHING, MESSAGE_LEVEL

    _settings_loader.reload()

    COLOR_TOLERANCE = _settings_loader.get("color_tolerance")
    DELAY_BEFORE_CHECK = _settings_loader.get("delay_before_check")
    DELAY_AFTER_PRESS = _settings_loader.get("delay_after_press")
    DELAY_DRAG_DURATION = _settings_loader.get("delay_drag_duration")
    DELAY_AFTER_DRAG = _settings_loader.get("delay_after_drag")
    DELAY_AFTER_CLICK = _settings_loader.get("delay_after_click")
    STOP_KEY = _settings_loader.get("stop_key")
    MAX_ZODIAC_SLOTS = _settings_loader.get("max_zodiac_slots")
    DEBUG_COLOR_MATCHING = _settings_loader.get("debug_color_matching")
    MESSAGE_LEVEL = _settings_loader.get("message_level")
