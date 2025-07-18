"""
Main application controller for Revolution Idle Sacrifice Automation.

This module orchestrates the different components of the application
and manages the main execution flow and user interface.
"""

from typing import Optional

import pynput.keyboard
import pynput.mouse

from config.config_manager import ConfigManager
from src.automation_engine import AutomationEngine
from src.help import display_help
from src.input_handlers import KeyboardHandler
from src.setup_manager import SetupManager
from utils.display_utils import show_message


class RevolutionIdleApp:
    """Main application controller for Revolution Idle Sacrifice Automation."""

    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        self.automation_engine = AutomationEngine()
        self.setup_manager = SetupManager(self.config_manager)
        self.keyboard_handler = KeyboardHandler(self._on_stop_automation)

        # Input listeners
        self.mouse_listener: Optional[pynput.mouse.Listener] = None
        self.keyboard_listener: Optional[pynput.keyboard.Listener] = None

        # Current mode
        self.current_mode: Optional[str] = None

    def run(self) -> None:
        """Main application entry point."""
        show_message(
            "Welcome to the Revolution Idle Sacrifice Automation Script!", level="info"
        )

        # Attempt to load configuration at startup
        if self.config_manager.load_config():
            from config.settings import (  # pylint: disable=import-outside-toplevel
                CONFIG_FILE,
            )

            show_message(f"Configuration loaded from {CONFIG_FILE}")

        # Start input listeners
        self._start_listeners()

        try:
            # Main application loop
            self._main_loop()
        finally:
            # Ensure listeners are stopped
            self._stop_listeners()

    def _start_listeners(self) -> None:
        """Start mouse and keyboard listeners."""
        mouse_handler = self.setup_manager.get_mouse_handler()
        self.mouse_listener = pynput.mouse.Listener(on_click=mouse_handler.on_click)
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press=self.keyboard_handler.on_press
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def _stop_listeners(self) -> None:
        """Stop mouse and keyboard listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener.join()

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener.join()

    def _main_loop(self) -> None:
        """Main application loop for mode selection."""
        while True:
            choice = self._get_user_choice()

            if choice in ["1", "setup"]:
                self._run_setup_mode()
            elif choice in ["2", "automation"]:
                self._run_automation_mode()
            elif choice in ["3", "help"]:
                display_help()
            elif choice in ["4", "settings"]:
                self._reload_settings()
            elif choice in ["5", "exit"]:
                show_message(
                    "Exiting Revolution Idle Sacrifice Automation Script. Goodbye!",
                    level="info",
                )
                break
            else:
                show_message(
                    "Invalid choice. Please enter '1', 'setup', '2', 'automation', "
                    "'3', 'help', '4', 'settings', '5', or 'exit'.",
                    level="info",
                )

            # Reset current mode after each operation
            self.current_mode = None

    def _get_user_choice(self) -> str:
        """Get user's mode selection choice."""
        show_message("\nSelect an option:", level="info")
        print("1. Setup Mode (Configure click points and colors)")
        print("2. Automation Mode (Run the automation)")
        print("3. Help (Learn more about the script and settings)")
        print("4. Reload Settings (Reload settings from user_settings.json)")
        print("5. Exit (Quit the script)")

        return (
            input(
                "Enter your choice (1/setup, 2/automation, 3/help, 4/settings, 5/exit): "
            )
            .lower()
            .strip()
        )

    def _run_setup_mode(self) -> None:
        """Run setup mode."""
        self.current_mode = "setup"
        self.setup_manager.get_mouse_handler().set_mode("setup")
        self.setup_manager.run_setup_mode()

    def _run_automation_mode(self) -> None:
        """Run automation mode."""
        self.current_mode = "automation"

        # Validate configuration before starting
        if not self.config_manager.validate_config():
            show_message(
                "Cannot start automation: Invalid or missing configuration. "
                "Please run setup mode first.",
                level="info",
            )
            return

        # Reset keyboard handler stop flag
        self.keyboard_handler.reset_stop_flag()

        # Set mouse handler to automation mode
        self.setup_manager.get_mouse_handler().set_mode("automation")

        # Run automation
        self.automation_engine.run_automation(
            self.config_manager.click_coords,
            self.config_manager.target_rgbs,
            lambda: self.keyboard_handler.stop_automation,
        )

    def _on_stop_automation(self) -> None:
        """Callback when automation should be stopped."""
        self.automation_engine.stop()

    def get_current_mode(self) -> Optional[str]:
        """Get the current operation mode."""
        return self.current_mode

    def _reload_settings(self) -> None:
        """Reload settings from user_settings.json file."""
        try:
            from config.settings import (  # pylint: disable=import-outside-toplevel
                reload_settings,
            )

            reload_settings()
            show_message(
                "Settings reloaded successfully from user_settings.json", level="info"
            )
            show_message(
                "Note: Some settings may require restarting the script to take effect.",
                level="info",
            )
        except Exception as e:  # pylint: disable=broad-except
            show_message(f"Failed to reload settings: {e}", level="info")
