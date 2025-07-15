"""
Configuration settings for Revolution Idle Sacrifice Automation Script.

This module contains all user-configurable settings that control the behavior
of the automation script. Users can modify these values to customize the script
for their specific setup and preferences.
"""

# --- User Configurable Settings ---
# You can easily change these values to customize the script's behavior.

# Color Matching Tolerance
# RGB values can vary slightly due to lighting, compression, etc.
# When clicking on a zodiac slot, the RGB may darken during capture.
# The default value of 15 works well.
# This sets how close colors need to be to match (0 = exact match, higher = more tolerant)
COLOR_TOLERANCE = 15  # Allow RGB values to differ by up to 15 points per channel

# Delay Timings (in seconds)
# Adjust these if the automation is too fast or too slow for your system/game.
# These are the fastest timings I could get while keeping consistency.
DELAY_BEFORE_CHECK = 0.02  # Delay before checking pixel colors in the automation loop
DELAY_AFTER_PRESS = 0.02  # Delay immediately after a mouse press
DELAY_DRAG_DURATION = 0.02  # Duration of the mouse drag action
DELAY_AFTER_DRAG = 0.11  # Delay after completing a drag action
DELAY_AFTER_CLICK = 0.01  # Delay after performing a click action

# Automation Exit Key
# The keyboard key that will stop the automation. Default is 'q'.
# Can be a single character (e.g., 'q', 'p') or a special key name (e.g., 'esc', 'f1', 'space', 'shift', 'ctrl').
# For a list of special key names, refer to pynput.keyboard.Key documentation.
STOP_KEY = "q"

# Multiple Zodiac Slots Configuration
# Maximum number of zodiac slots that can be configured for sacrifice.
# Set this to the number of zodiac slots you want to monitor.
# Set to -1 for unlimited slots, or a positive number to limit the maximum.
# During setup, you can configure fewer slots than this maximum if desired.
MAX_ZODIAC_SLOTS = -1  # -1 = unlimited slots, or set a positive number to limit

# Debug Color Detection
# Set to True to show detailed color matching information during automation.
# This helps troubleshoot color tolerance issues.
# MESSAGE_LEVEL must be set to 'debug' to see these messages.
# Note: With unlimited zodiac slots, debug output will show all configured slots.
DEBUG_COLOR_MATCHING = False  # Set to True for detailed color matching info

# Message Verbosity
# Set to 'info' for standard messages. Set to 'debug' for more detailed output.
MESSAGE_LEVEL = "info"  # Options: 'info', 'debug'

# Configuration file name
CONFIG_FILE = "revolution_idle_zodiac_automation_config.json"
