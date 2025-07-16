"""
Help and documentation module for Revolution Idle Sacrifice Automation.

This module provides comprehensive help information about the script's
functionality, configuration options, and usage instructions.
"""

from utils.display_utils import show_message


def get_help_text():
    """Returns the help text as a string for GUI use."""
    return """
    --- Revolution Idle Sacrifice Automation Script Help ---

    This script automates the zodiac sacrificing process in Revolution Idle.
    It has two main modes:

    1.  Setup Mode:
        Allows you to define the key locations and colors on your screen
        that the automation will interact with. You will be prompted to:
        -   Left-click on multiple Zodiac Slots (unlimited by default).
            Each slot's color will be remembered for matching.
            You can configure fewer slots than the maximum if desired.
        -   Right-click when finished adding zodiac slots to proceed.
        -   Left-click on the Sacrifice Drag Box (where zodiacs are dragged).
        -   Left-click on the Sacrifice Button (color hardcoded to (219, 124, 0)).
        After setting these, the configuration is saved to 'revolution_idle_zodiac_automation_config.json'.
        
        NOTE: If you need help identifying the correct click points, check the visual guide
        in the GitHub repository at: https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation

    2.  Automation Mode:
        Runs the automated sacrificing process using the saved configuration.
        The script will continuously:
        -   Check the colors of all configured Zodiac Slots in each cycle.
        -   When any zodiac slot's color matches its target, drag that zodiac to the Sacrifice Box.
        -   Check the color of the Sacrifice Button after each drag.
        -   If the Sacrifice Button's color matches, click it and restart the cycle.
        -   If the Sacrifice Button's color does NOT match, continue checking zodiac slots.

    --- User Configurable Settings (Edit these in the user_settings.json file) ---

    All settings are now configured through an external 'user_settings.json' file that is
    automatically created when you first run the script. You can edit this file with any
    text editor and reload settings using option 4 in the main menu.

    Key settings include:

    -   Multiple Zodiac Slots Configuration:
        -   max_zodiac_slots: Maximum number of zodiac slots that can be configured.
            Set to -1 for unlimited slots (default), or a positive number to limit the maximum.
            During setup, you can configure fewer slots than this maximum if desired.

    -   Color Matching Tolerance:
        -   color_tolerance: Sets how close colors need to be to match (0 = exact match, higher = more tolerant).
            Allows RGB values to differ by up to X points per channel (default X=15).
            If zodiac automation only works on some slots, try increasing this value.

    -   Debug Color Detection:
        -   debug_color_matching: Set to true to show detailed color matching information during automation.
            This helps troubleshoot color tolerance issues by showing exact RGB differences.
            Useful when zodiac slots don't match as expected.

    -   Delay Timings (in seconds):
        -   delay_before_check: Delay before checking pixel colors in the automation loop.
        -   delay_after_press: Delay immediately after a mouse press.
        -   delay_drag_duration: Duration of the mouse drag action.
        -   delay_after_drag: Delay after completing a drag action.
        -   delay_after_click: Delay after performing a click action.
        (Adjust these values in seconds, e.g., 0.05 for 50 milliseconds)

    -   Automation Exit Key:
        -   stop_key: The keyboard key that will stop the automation. Default is "q".
            You can set this to a single character (e.g., "q", "p") or a special key name.
            Common special key names include: "esc", "f1", "f2", ..., "f12", "space",
            "enter", "shift", "ctrl", "alt", "up", "down", "left", "right", etc.
            Ensure you use the exact string representation (e.g., "esc" not "Escape").

    -   Message Verbosity:
        -   message_level: Controls the amount of information printed to the console.
            -   "info": Shows standard operational messages. (Default)
            -   "debug": Shows more detailed messages, useful for troubleshooting.

    For detailed information about all settings, see the SETTINGS_GUIDE.md file.

    --- Performance Information ---

    Based on testing with Revolution Idle:
    -   Script Performance: Approximately 230 sacrifices per minute with 1 slot configured
        and optimal timing settings.
    -   Manual vs Automation: I can achieve ~6 unities per second, while the script
        reaches a soft limit of ~3.8 sacrifices per second due to timing constraints.
    -   Performance Factors: Your results may vary depending on:
        •   Timing settings (faster settings = higher risk of inconsistency)
        •   Computer performance and responsiveness
        •   Current game progression and zodiac generation rate
        •   Number of zodiac slots configured (more slots may reduce per-slot efficiency)
    -   Optimization Tips: For maximum performance, use a single slot with the fastest
        timing settings that still maintain reliability.

    NOTE: The 230 sacrifices/minute rate represents a practical soft limit due to game
    timing constraints and automation overhead. Individual results may vary.

    --- How to Use ---
    1.  Install dependencies: `pip install -r requirements.txt`
    2.  Run the script: `python main.py`
    3.  Choose 'setup' (or 1) first to configure your click points and zodiac slots.
    4.  Then, choose 'automation' (or 2) to start the process.
    5.  Use 'settings' (or 4) to reload settings from user_settings.json after making changes.
    6.  Press the configured stop_key (default 'q') during automation to return to the main menu.
    7.  To exit the script completely, type 'exit' (or 5) in the main menu, or press Ctrl+C.
    """


def display_help():
    """Displays information about the script and its configurable options."""
    help_message = get_help_text()
    show_message(help_message, level="info")
