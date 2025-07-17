"""
Main GUI application for Revolution Idle Sacrifice Automation using CustomTkinter.

This module provides a modern, user-friendly graphical interface for the
Revolution Idle Sacrifice Automation script, replacing the CLI interface
when GUI mode is selected.
"""

import threading
import time
from typing import Optional

import customtkinter as ctk  # type: ignore
import pynput.keyboard
import pynput.mouse

from config.config_manager import ConfigManager
from src.automation_engine import AutomationEngine
from src.gui.help_window import HelpWindow
from src.gui.setup_window import SetupInstructionsWindow
from src.gui.utils import log_message
from src.input_handlers import KeyboardHandler
from src.setup_manager import SetupManager


class RevolutionIdleGUI:
    """GUI application controller for Revolution Idle Sacrifice Automation."""

    def __init__(self) -> None:
        """Initialize the GUI application."""
        # Initialize core components
        self.config_manager = ConfigManager()
        self.automation_engine = AutomationEngine()
        self.setup_manager = SetupManager(self.config_manager)
        self.keyboard_handler = KeyboardHandler(self._on_stop_automation)

        # Input listeners
        self.mouse_listener: Optional[pynput.mouse.Listener] = None
        self.keyboard_listener: Optional[pynput.keyboard.Listener] = None

        # GUI components
        self.root: Optional[ctk.CTk] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.log_textbox: Optional[ctk.CTkTextbox] = None
        self.automation_button: Optional[ctk.CTkButton] = None
        self.setup_button: Optional[ctk.CTkButton] = None

        # Windows
        self.setup_window: Optional[SetupInstructionsWindow] = None

        # State management
        self.automation_thread: Optional[threading.Thread] = None
        self.is_automation_running = False
        self.setup_in_progress = False
        self.window_detection_disabled = False

    def run(self) -> None:
        """Initialize and run the GUI application."""
        self._create_gui()
        self._load_initial_config()
        if self.root:
            self.root.mainloop()

    def _create_gui(self) -> None:
        """Create the main GUI window and components."""
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Revolution Idle Sacrifice Automation")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)

        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Title label
        title_label = ctk.CTkLabel(
            main_frame,
            text="Revolution Idle Sacrifice Automation",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=(20, 10))

        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame, text="Ready", font=ctk.CTkFont(size=14)
        )
        self.status_label.grid(row=1, column=0, columnspan=4, pady=(0, 20))

        # Control buttons
        self.setup_button = ctk.CTkButton(
            main_frame,
            text="Setup Mode",
            command=self._on_setup_click,
            width=150,
            height=40,
        )
        self.setup_button.grid(row=2, column=0, padx=10, pady=10)

        self.automation_button = ctk.CTkButton(
            main_frame,
            text="Start Automation",
            command=self._on_automation_click,
            width=150,
            height=40,
        )
        self.automation_button.grid(row=2, column=1, padx=10, pady=10)

        help_button = ctk.CTkButton(
            main_frame, text="Help", command=self._on_help_click, width=150, height=40
        )
        help_button.grid(row=2, column=2, padx=10, pady=10)

        settings_button = ctk.CTkButton(
            main_frame,
            text="Reload Settings",
            command=self._on_settings_click,
            width=150,
            height=40,
        )
        settings_button.grid(row=2, column=3, padx=10, pady=10)

        # Log frame
        log_frame = ctk.CTkFrame(self.root)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        # Log label
        log_label = ctk.CTkLabel(
            log_frame, text="Activity Log:", font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Log textbox
        self.log_textbox = ctk.CTkTextbox(log_frame, height=200, wrap="word")
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        # Initially disable automation button if no config
        self._update_button_states()

        # Log initial message
        self._log_message("Welcome to Revolution Idle Sacrifice Automation!")

    def _load_initial_config(self) -> None:
        """Load configuration at startup."""
        if self.config_manager.load_config():
            from config.settings import (  # pylint: disable=import-outside-toplevel
                CONFIG_FILE,
            )

            self._log_message(f"Configuration loaded from {CONFIG_FILE}")
            self._update_status("Configuration loaded")
        else:
            self._log_message("No configuration found. Please run Setup Mode first.")
            self._update_status("No configuration - Setup required")

        self._update_button_states()

    def _update_status(self, message: str) -> None:
        """Update the status label."""
        if self.status_label:
            self.status_label.configure(text=message)

    def _log_message(self, message: str) -> None:
        """Add a message to the log textbox."""
        log_message(self.log_textbox, message)

    def _update_button_states(self) -> None:
        """Update button states based on current configuration and automation status."""
        has_config = self.config_manager.validate_config()

        if self.automation_button:
            if self.is_automation_running:
                self.automation_button.configure(text="Stop Automation", fg_color="red")
            elif has_config:
                self.automation_button.configure(
                    text="Start Automation", fg_color=("green", "green")
                )
                self.automation_button.configure(state="normal")
            else:
                self.automation_button.configure(
                    text="Start Automation", state="disabled"
                )

        if self.setup_button:
            if self.setup_in_progress:
                self.setup_button.configure(
                    text="Setup in Progress...", state="disabled"
                )
            else:
                self.setup_button.configure(text="Setup Mode", state="normal")

    def _on_setup_click(self) -> None:
        """Handle setup button click."""
        if self.setup_in_progress:
            return

        # Reset window detection state for new setup session
        self.window_detection_disabled = False

        self.setup_in_progress = True
        self._update_button_states()
        self._update_status("Setup mode active")
        self._log_message("Starting setup mode...")

        # Show instructions window
        self._show_setup_instructions()

        # Set up the setup manager to use GUI callbacks
        self.setup_manager.set_gui_callbacks(
            self._update_setup_instructions, self._log_message
        )

        # Run setup in a separate thread to avoid blocking GUI
        setup_thread = threading.Thread(target=self._run_setup_thread)
        setup_thread.daemon = True
        setup_thread.start()

    def _run_setup_thread(self) -> None:
        """Run setup mode in a separate thread."""
        try:
            # Start input listeners for setup
            self._start_listeners()

            # Run setup mode
            self.setup_manager.run_setup_mode()

            # Update GUI after setup completion
            if self.root and not self.setup_manager.setup_cancelled:
                self.root.after(0, self._on_setup_complete)
            elif self.root and self.setup_manager.setup_cancelled:
                self.root.after(0, self._on_setup_cancelled)

        except Exception as e:  # pylint: disable=broad-except
            if self.root:
                self.root.after(0, lambda err=str(e): self._on_setup_error(err))
        finally:
            # Stop listeners
            self._stop_listeners()

    def _start_listeners(self) -> None:
        """Start mouse and keyboard listeners."""
        # Start mouse listener for setup
        self.mouse_listener = pynput.mouse.Listener(
            on_click=self.setup_manager.on_click
        )
        self.mouse_listener.start()

    def _start_automation_keyboard_listener(self) -> None:
        """Start keyboard listener for automation."""
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press=self.keyboard_handler.on_press
        )
        self.keyboard_listener.start()
        self._log_message("Press F8 to stop automation")

    def _stop_automation_keyboard_listener(self) -> None:
        """Stop the keyboard listener for automation."""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def _stop_listeners(self) -> None:
        """Stop all input listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None

    def _on_setup_complete(self) -> None:
        """Handle setup completion."""
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup complete")
        self._log_message("Setup completed successfully!")

        # Close setup instructions window
        self._close_setup_window()

        # Update button states to enable automation
        self._update_button_states()

    def _on_setup_error(self, error_msg: str) -> None:
        """Handle setup error."""
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup failed")
        self._log_message(f"Setup failed: {error_msg}")
        self._close_setup_window()

    def _on_setup_cancelled(self) -> None:
        """Handle setup cancellation."""
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup cancelled")
        self._log_message("Setup was cancelled")
        self._close_setup_window()

    def _show_setup_instructions(self) -> None:
        """Show the setup instructions window."""
        self.setup_window = SetupInstructionsWindow(
            self.root,
            self._cancel_setup,
            self._disable_window_detection,
        )

    def _update_setup_instructions(self, message: str) -> None:
        """Update the setup instructions text."""
        if self.setup_window:
            self.setup_window.update_instructions(message)

    def _cancel_setup(self) -> None:
        """Cancel the setup process."""
        if self.setup_manager:
            self.setup_manager.cancel_setup()
            self._log_message("Setup cancelled by user")

        self._close_setup_window()
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup cancelled")

    def _disable_window_detection(self) -> None:
        """Disable window detection for setup."""
        self.window_detection_disabled = True
        self.setup_manager.disable_window_detection()
        self._log_message("Window detection disabled for this setup session")

    def _close_setup_window(self) -> None:
        """Close the setup instructions window."""
        if self.setup_window:
            self.setup_window.close()
            self.setup_window = None

    def _on_automation_click(self) -> None:
        """Handle automation button click."""
        if self.is_automation_running:
            self._stop_automation()
        else:
            self._start_automation()

    def _start_automation(self) -> None:
        """Start the automation process."""
        if self.is_automation_running:
            return

        self.is_automation_running = True
        self._update_button_states()
        self._update_status("Automation running")
        self._log_message("Starting automation...")
        self._log_message("Switch to the game window within 3 seconds...")

        # Start keyboard listener for stopping automation
        self._start_automation_keyboard_listener()

        # Run automation in a separate thread
        self.automation_thread = threading.Thread(target=self._run_automation_thread)
        self.automation_thread.daemon = True
        self.automation_thread.start()

    def _run_automation_thread(self) -> None:
        """Run automation in a separate thread."""
        try:
            # Define a stop callback that checks if automation should stop
            def stop_callback() -> bool:
                return not self.is_automation_running

            # Start automation with delay to allow switching to game window
            time.sleep(3)
            self.automation_engine.run_automation(stop_callback)

            # Update GUI after automation completion
            if self.root:
                self.root.after(0, self._on_automation_stopped)

        except Exception as e:  # pylint: disable=broad-except
            if self.root:
                self.root.after(0, lambda err=str(e): self._on_automation_error(err))

    def _stop_automation(self) -> None:
        """Stop the automation process."""
        if not self.is_automation_running:
            return

        self.is_automation_running = False
        self._update_status("Stopping automation...")
        self._log_message("Stopping automation...")

    def _on_stop_automation(self) -> None:
        """Handle stop automation callback from keyboard handler."""
        if self.is_automation_running and self.root:
            self.root.after(0, self._on_keyboard_stop_automation)

    def _on_keyboard_stop_automation(self) -> None:
        """Handle keyboard stop automation event."""
        self._log_message("Automation stopped by keyboard (F8)")
        self._stop_automation()

    def _on_automation_stopped(self) -> None:
        """Handle automation stopped event."""
        self.is_automation_running = False
        self._update_button_states()
        self._update_status("Automation stopped")
        self._log_message("Automation stopped")
        self._stop_automation_keyboard_listener()

    def _on_automation_error(self, error_msg: str) -> None:
        """Handle automation error."""
        self.is_automation_running = False
        self._update_button_states()
        self._update_status("Automation error")
        self._log_message(f"Automation error: {error_msg}")
        self._stop_automation_keyboard_listener()

    def _on_help_click(self) -> None:
        """Handle help button click."""
        self._show_help_window()

    def _show_help_window(self) -> None:
        """Show the help window."""
        if self.root:
            help_window = HelpWindow(self.root)

    def _on_settings_click(self) -> None:
        """Handle settings button click."""
        # Reload settings
        if self.config_manager.load_config():
            self._log_message("Settings reloaded successfully")
            self._update_status("Settings reloaded")
        else:
            self._log_message("Failed to reload settings")
            self._update_status("Settings reload failed")
