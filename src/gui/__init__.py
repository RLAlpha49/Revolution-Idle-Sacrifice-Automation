"""
GUI package for Revolution Idle Sacrifice Automation.

This package contains all GUI-related modules and components.
"""

from src.gui.app import RevolutionIdleGUI
from src.gui.components import ControlButton, SettingsSection, StatusDisplay, TabView
from src.gui.help_window import HelpWindow
from src.gui.settings_window import SettingsWindow
from src.gui.setup_window import SetupInstructionsWindow
from src.gui.utils import log_message

__all__ = [
    "RevolutionIdleGUI",
    "ControlButton",
    "SettingsSection",
    "StatusDisplay",
    "TabView",
    "HelpWindow",
    "SettingsWindow",
    "SetupInstructionsWindow",
    "log_message",
]
