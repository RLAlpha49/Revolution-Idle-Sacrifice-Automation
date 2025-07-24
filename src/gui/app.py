"""
Main GUI application for Revolution Idle Sacrifice Automation using CustomTkinter.

This module provides a modern, user-friendly graphical interface for the
Revolution Idle Sacrifice Automation script, replacing the CLI interface
when GUI mode is selected.
"""

import logging
import threading
import time
from typing import Optional, Dict, Any
import os
import sys
import json

import customtkinter as ctk  # type: ignore
import pynput.keyboard
import pynput.mouse

from config.config_manager import ConfigManager
from config.settings import STOP_KEY
from src.automation_engine import AutomationEngine
from .automation_config_window import AutomationConfigWindow
from .help_window import HelpWindow
from .settings_window import SettingsWindow
from .window_utils import WindowPositioner
from src.gui.setup_instructions_window import SetupInstructionsWindow
from src.gui.utils import log_message
from src.input_handlers import KeyboardHandler
from src.setup_manager import SetupManager

# Set up module logger
logger = logging.getLogger(__name__)


class RevolutionIdleGUI:
    """GUI application controller for Revolution Idle Sacrifice Automation."""

    def __init__(self) -> None:
        """Initialize the GUI application."""
        logger.info("Initializing GUI application")

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
        self.mode_switch: Optional[ctk.CTkSwitch] = None

        # Windows
        self.setup_window: Optional[SetupInstructionsWindow] = None
        self.settings_window: Optional[SettingsWindow] = None
        self.automation_config_window: Optional[AutomationConfigWindow] = None

        # State management
        self.automation_thread: Optional[threading.Thread] = None
        self.is_automation_running = False
        self.setup_in_progress = False
        self.window_detection_disabled = False

        # Get GUI scale factor from settings
        self.gui_scale = self._get_gui_scale_factor()

    def _get_gui_scale_factor(self) -> float:
        """Get the GUI scale factor from settings."""
        try:
            # Try to load from user_settings.json
            settings_file = self._get_settings_file_path()

            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                    if "gui_scale" in settings:
                        scale = settings["gui_scale"]
                        # Ensure scale is within reasonable bounds
                        if 0.5 <= scale <= 2.0:
                            return float(scale)

                        logger.warning(
                            "GUI scale out of bounds: %s, using default 1.0", scale
                        )
                    else:
                        logger.debug("No gui_scale found in settings")
            else:
                logger.debug("Settings file not found: %s", settings_file)

            logger.info("Using default GUI scale factor: 1.0")
            return 1.0  # Default scale
        except (json.JSONDecodeError, IOError, TypeError, ValueError) as e:
            logger.error("Error loading GUI scale: %s", e, exc_info=True)
            return 1.0  # Default scale on error

    def _get_settings_file_path(self) -> str:
        """Get the path to the user settings file."""
        # Get the directory where the script is running from
        if hasattr(sys, "_MEIPASS"):
            # Running as compiled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        path = os.path.join(base_dir, "user_settings.json")
        return path

    def run(self) -> None:
        """Initialize and run the GUI application."""
        self._create_gui()
        self._load_initial_config()
        if self.root:
            logger.info("Starting GUI main loop")
            self.root.mainloop()

    def _create_gui(self) -> None:
        """Create the main GUI window and components."""
        logger.debug("Creating GUI components")

        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Apply scaling factor
        ctk.set_widget_scaling(self.gui_scale)

        logger.info("Applied GUI scale factor: %s", self.gui_scale)

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Revolution Idle Sacrifice Automation")
        self.root.geometry("800x600")  # Smaller default size
        self.root.minsize(600, 450)  # Smaller minimum size

        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create header frame
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title and logo frame
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew")
        title_frame.grid_columnconfigure(1, weight=1)

        # App icon/logo (placeholder - you can replace with an actual logo)
        logo_label = ctk.CTkLabel(
            title_frame,
            text="⚡",  # Unicode lightning bolt as placeholder
            font=ctk.CTkFont(size=28),
            width=40,
            height=40,
        )
        logo_label.grid(row=0, column=0, padx=(0, 5), pady=5)

        # Title label with subtitle in a responsive container
        title_container = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_container.grid(row=0, column=1, sticky="w")

        title_label = ctk.CTkLabel(
            title_container,
            text="Revolution Idle Automation",  # Shortened title
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            title_container,
            text="Automate zodiac sacrificing",  # Shortened subtitle
            font=ctk.CTkFont(size=12),
            text_color=("gray70", "gray45"),
            anchor="w",
        )
        subtitle_label.pack(anchor="w")

        # Status indicator
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        status_frame.grid_columnconfigure(1, weight=1)

        status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=("gray60", "gray60"),
            width=15,
        )
        status_indicator.grid(row=0, column=0, padx=(0, 3))

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            anchor="w",
        )
        self.status_label.grid(row=0, column=1, sticky="w")

        # Main content frame with sidebar and main area - using responsive weights
        content_frame = ctk.CTkFrame(self.root)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=0)  # Sidebar doesn't grow
        content_frame.grid_columnconfigure(1, weight=1)  # Main area grows

        # Sidebar for buttons - fixed width but with responsive content
        sidebar_frame = ctk.CTkFrame(content_frame)
        sidebar_frame.grid(row=0, column=0, sticky="ns", padx=(0, 10), pady=0)
        sidebar_frame.grid_rowconfigure(4, weight=1)  # Push buttons to top

        # Dynamic button sizing
        button_width = 140  # Smaller buttons
        button_height = 35

        # Automation section (at the top, most prominent)
        automation_section = ctk.CTkFrame(
            sidebar_frame, fg_color=("gray90", "gray20"), corner_radius=8
        )
        automation_section.pack(fill="x", padx=5, pady=(0, 10), ipadx=5, ipady=5)

        # Automation header
        automation_header = ctk.CTkFrame(automation_section, fg_color="transparent")
        automation_header.pack(fill="x", padx=5, pady=(5, 3))

        # Automation icon and label
        auto_icon = ctk.CTkLabel(
            automation_header,
            text="🚀",  # Rocket emoji
            font=ctk.CTkFont(size=16),
        )
        auto_icon.pack(side="left", padx=(0, 3))

        auto_label = ctk.CTkLabel(
            automation_header,
            text="Automation",  # Shortened label
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        auto_label.pack(side="left")

        # Mode toggle frame in automation section
        mode_frame = ctk.CTkFrame(automation_section, fg_color="transparent")
        mode_frame.pack(fill="x", padx=5, pady=(5, 3))

        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Mode:",
            font=ctk.CTkFont(size=11),
            text_color=("gray70", "gray50"),
        )
        mode_label.pack(side="left", padx=(0, 5))

        # Mode toggle switch
        self.mode_switch = ctk.CTkSwitch(
            mode_frame,
            text="Advanced",
            command=self._on_mode_toggle,
            font=ctk.CTkFont(size=11),
            width=80,
        )
        self.mode_switch.pack(side="left")

        # Set initial mode based on config
        self._update_mode_switch()

        # Prominent automation button
        self.automation_button = ctk.CTkButton(
            automation_section,
            text="Start Automation",
            command=self._on_automation_click,
            width=button_width,
            height=button_height + 5,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("green", "green"),
            hover_color=(
                "#009000",
                "#009000",
            ),  # Slightly darker green for subtle hover effect
            corner_radius=6,
        )
        self.automation_button.pack(padx=5, pady=(0, 5), fill="x")

        # Divider
        divider = ctk.CTkFrame(sidebar_frame, height=1, fg_color=("gray80", "gray30"))
        divider.pack(fill="x", padx=10, pady=(0, 5))

        # Configuration section container - using pack for better dynamic sizing
        config_section = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        config_section.pack(fill="x", expand=False, padx=5)

        # Other controls section header
        controls_label = ctk.CTkLabel(
            config_section,
            text="CONFIGURATION",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray60"),
            anchor="w",
        )
        controls_label.pack(anchor="w", padx=5, pady=(0, 3))

        # Control buttons in sidebar
        self.setup_button = ctk.CTkButton(
            config_section,
            text="Automation Config",
            command=self._on_setup_click,
            width=button_width,
            height=button_height,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
        )
        self.setup_button.pack(fill="x", padx=5, pady=3)

        settings_button = ctk.CTkButton(
            config_section,
            text="Settings",
            command=self._on_settings_click,
            width=button_width,
            height=button_height,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
        )
        settings_button.pack(fill="x", padx=5, pady=3)

        # Help section - using pack for better dynamic sizing
        help_section = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        help_section.pack(fill="x", expand=False, padx=5, pady=(10, 0))

        help_label = ctk.CTkLabel(
            help_section,
            text="HELP & SUPPORT",
            font=ctk.CTkFont(size=11),
            text_color=("gray60", "gray60"),
            anchor="w",
        )
        help_label.pack(anchor="w", padx=5, pady=(0, 3))

        help_button = ctk.CTkButton(
            help_section,
            text="Help",
            command=self._on_help_click,
            width=button_width,
            height=button_height,
            font=ctk.CTkFont(size=12),
            corner_radius=6,
        )
        help_button.pack(fill="x", padx=5, pady=3)

        # Main area with log - now more responsive
        log_frame = ctk.CTkFrame(content_frame)
        log_frame.grid(row=0, column=1, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        # Log header with icon
        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 3))
        log_header.grid_columnconfigure(1, weight=1)

        log_icon = ctk.CTkLabel(
            log_header,
            text="📋",  # Unicode clipboard icon
            font=ctk.CTkFont(size=16),
        )
        log_icon.grid(row=0, column=0, padx=(0, 3))

        log_label = ctk.CTkLabel(
            log_header,
            text="Activity Log",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        log_label.grid(row=0, column=1, sticky="w")

        # Log textbox with border
        log_container = ctk.CTkFrame(log_frame)
        log_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        log_container.grid_rowconfigure(0, weight=1)
        log_container.grid_columnconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(
            log_container,
            wrap="word",
            font=ctk.CTkFont(size=12),
        )
        self.log_textbox.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        # Initially disable automation button if no config
        self._update_button_states()

        logger.debug("GUI components created")

    def _load_initial_config(self) -> None:
        """Load configuration at startup."""
        if self.config_manager.load_config():
            from config.settings import (  # pylint: disable=import-outside-toplevel
                CONFIG_FILE,
            )

            self._log_message(f"Configuration loaded from {CONFIG_FILE}")
            self._update_status("Configuration loaded")
            logger.info("Configuration loaded from %s", CONFIG_FILE)
        else:
            self._log_message("No configuration found. Please run Setup Mode first.")
            self._update_status("No configuration - Setup required")
            logger.info("No configuration found")

        self._update_button_states()
        self._update_mode_switch()

    def _update_status(self, message: str) -> None:
        """Update the status label and indicator."""
        if self.status_label:
            self.status_label.configure(text=message)

            # Find status indicator (sibling of status_label)
            status_frame = self.status_label.master
            for child in status_frame.winfo_children():
                if isinstance(child, ctk.CTkLabel) and child != self.status_label:
                    # Update color based on status message
                    if "error" in message.lower():
                        child.configure(text_color=("red", "red"))
                    elif "active" in message.lower() or "running" in message.lower():
                        child.configure(text_color=("green", "green"))
                    elif "setup" in message.lower():
                        child.configure(text_color=("orange", "orange"))
                    elif "loaded" in message.lower():
                        child.configure(text_color=("cyan", "cyan"))
                    else:
                        child.configure(text_color=("gray60", "gray60"))
                    break

            logger.debug("Status updated: %s", message)

    def _log_message(self, message: str) -> None:
        """Add a message to the log textbox."""
        log_message(self.log_textbox, message)
        logger.info(message)

    def _update_button_states(self) -> None:
        """Update button states based on current configuration and automation status."""
        has_config = self.config_manager.validate_config()

        if self.automation_button:
            if self.is_automation_running:
                self.automation_button.configure(
                    text="Stop Automation",
                    fg_color="red",
                    hover_color="#C00000",  # Slightly darker red for subtle hover effect
                )
                logger.debug("Automation button set to 'Stop'")
            elif has_config:
                self.automation_button.configure(
                    text="Start Automation",
                    fg_color=("green", "green"),
                    hover_color=(
                        "#009000",
                        "#009000",
                    ),  # Slightly darker green for subtle hover effect
                )
                self.automation_button.configure(state="normal")
                logger.debug("Automation button enabled")
            else:
                self.automation_button.configure(
                    text="Start Automation", state="disabled"
                )
                logger.debug("Automation button disabled - no config")

        if self.setup_button:
            if self.setup_in_progress:
                self.setup_button.configure(
                    text="Setup in Progress...", state="disabled"
                )
                logger.debug("Setup button disabled - setup in progress")
            else:
                self.setup_button.configure(text="Automation Config", state="normal")
                logger.debug("Setup button enabled")

    def _on_setup_click(self) -> None:
        """Handle setup button click."""
        if self.setup_in_progress:
            return

        # Create config data dictionary for the window
        # Only include the actual configuration data, not metadata
        base_config = {
            "click_coords": self.config_manager.click_coords,
            "target_rgbs": self.config_manager.target_rgbs,
        }

        # Add metadata for UI purposes
        config_data = {
            **base_config,
            "active_mode": self.config_manager.get_active_mode(),
            "has_simple_config": self.config_manager.has_simple_config(),
            "has_advanced_config": self.config_manager.has_advanced_config(),
        }

        # Add advanced config data if it exists
        if self.config_manager.has_advanced_config():
            advanced_config = self.config_manager.get_advanced_config()
            # Filter out metadata that might have been saved incorrectly
            clean_advanced = {
                k: v
                for k, v in advanced_config.items()
                if k
                not in [
                    "simple_config",
                    "advanced_config",
                    "has_simple_config",
                    "has_advanced_config",
                ]
            }
            config_data.update(clean_advanced)

        # Show the automation configuration window
        self.automation_config_window = AutomationConfigWindow(
            self.root, config_data, self._start_setup_process, self._on_config_saved
        )

        logger.debug("Automation configuration window opened")

    def _on_config_saved(self, config_data: Dict[str, Any]) -> None:
        """Handle configuration being saved from the automation config window.

        Args:
            config_data: The updated configuration data
        """
        try:
            # Check if this is advanced configuration
            if config_data.get("advanced_mode", False):
                # Save as advanced configuration
                if self.config_manager.save_advanced_config(config_data):
                    logger.info("Advanced configuration saved successfully")
                    self._log_message("Advanced configuration saved successfully!")
                else:
                    logger.error("Failed to save advanced configuration")
                    self._log_message("ERROR: Failed to save advanced configuration!")
            else:
                # Save as simple configuration
                if "click_coords" in config_data:
                    self.config_manager.click_coords = config_data["click_coords"]

                if "target_rgbs" in config_data:
                    self.config_manager.target_rgbs = config_data["target_rgbs"]

                # Save the configuration to file
                if self.config_manager.save_config("simple"):
                    logger.info("Simple configuration saved successfully")
                    self._log_message("Configuration saved successfully!")
                else:
                    logger.error("Failed to save simple configuration")
                    self._log_message("ERROR: Failed to save configuration!")

            # Update the UI to reflect the new configuration
            self._update_button_states()
            self._update_mode_switch()

        except Exception as e:
            logger.error("Error saving configuration: %s", e, exc_info=True)
            self._log_message(f"ERROR: Failed to save configuration: {e}")

    def _start_setup_process(self) -> None:
        """Start the actual setup process after configuration window."""
        # Reset window detection state for new setup session
        self.window_detection_disabled = False

        self.setup_in_progress = True
        self._update_button_states()
        self._update_status("Setup mode active")
        self._log_message("Starting setup mode...")
        logger.info("Setup mode started")

        # Show instructions window
        self._show_setup_instructions()

        # Set up the setup manager to use GUI callbacks
        self.setup_manager.set_gui_callbacks(
            self._update_setup_instructions, self._log_message, self._show_error_dialog
        )

        # Run setup in a separate thread to avoid blocking GUI
        setup_thread = threading.Thread(target=self._run_setup_thread)
        setup_thread.daemon = True
        setup_thread.start()
        logger.debug("Setup thread started")

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
        mouse_handler = self.setup_manager.get_mouse_handler()
        self.mouse_listener = pynput.mouse.Listener(on_click=mouse_handler.on_click)
        self.mouse_listener.start()

    def _start_automation_keyboard_listener(self) -> None:
        """Start keyboard listener for automation."""
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press=self.keyboard_handler.on_press
        )
        self.keyboard_listener.start()
        self._log_message(f"Press {STOP_KEY.upper()} to stop automation")

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
            self._enable_debug_mode,
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

    def _enable_debug_mode(self) -> None:
        """Enable debug mode for setup."""
        self.setup_manager.enable_debug_mode()
        self._log_message("Debug mode enabled for this setup session")

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
            self.automation_engine.run_automation(
                self.config_manager.click_coords,
                self.config_manager.target_rgbs,
                stop_callback,
            )

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
        self._log_message(f"Automation stopped by keyboard ({STOP_KEY.upper()})")
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

    def _on_mode_toggle(self) -> None:
        """Handle user toggling between simple and advanced mode."""
        try:
            if self.mode_switch:
                is_advanced = self.mode_switch.get()
                mode = "advanced" if is_advanced else "simple"

                # Update the active mode in config data
                self.config_manager.config_data["active_mode"] = mode

                # Save the configuration with the new mode
                if self.config_manager.save_config(mode):
                    self._log_message(f"Mode switched to: {mode.title()}")
                    logger.info("User switched to %s mode", mode)
                else:
                    self._log_message("Failed to save mode preference")
                    logger.error("Failed to save mode preference")

                self._update_button_states()
        except (AttributeError, ValueError) as e:
            logger.error("Error handling mode toggle: %s", e, exc_info=True)
            self._log_message("Error switching modes")

    def _update_mode_switch(self) -> None:
        """Update the mode switch based on current configuration."""
        try:
            if self.mode_switch:
                # Check if we have advanced configuration
                has_advanced = self.config_manager.has_advanced_config()
                current_mode = self.config_manager.get_active_mode()

                # Set switch based on current mode or presence of advanced config
                is_advanced = current_mode == "advanced" or (
                    has_advanced and current_mode != "simple"
                )

                self.mode_switch.select() if is_advanced else self.mode_switch.deselect()
                logger.debug(
                    "Mode switch updated to: %s",
                    "advanced" if is_advanced else "simple",
                )

        except (AttributeError, ValueError) as e:
            logger.error("Error updating mode switch: %s", e, exc_info=True)

    def _show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog to the user.

        Args:
            title: Title of the error dialog
            message: Error message to display
        """
        if self.root:
            error_window = ctk.CTkToplevel(self.root)
            error_window.title(title)
            error_window.transient(self.root)
            error_window.grab_set()

            # Position relative to main window with multi-monitor support
            WindowPositioner.position_window_relative(
                error_window, self.root, 450, 200, position="center"
            )

            # Error message label
            label = ctk.CTkLabel(
                error_window, text=message, wraplength=400, font=ctk.CTkFont(size=12)
            )
            label.pack(pady=20, padx=20, expand=True)

            # OK button
            button = ctk.CTkButton(
                error_window, text="OK", command=error_window.destroy, width=80
            )
            button.pack(pady=10)

            logger.debug("Error dialog shown: %s", title)

    def _show_help_window(self) -> None:
        """Show the help window."""
        if self.root:
            # Store the window instance to prevent it from being garbage collected
            # The window will be automatically destroyed when the user closes it
            HelpWindow(self.root)  # Window manages its own lifecycle

    def _on_settings_click(self) -> None:
        """Open the settings window."""
        logger.debug("Settings button clicked")
        if self.root and not self.settings_window:
            self._log_message("Opening settings editor...")
            self.settings_window = SettingsWindow(
                self.root, on_settings_saved=self._on_settings_saved
            )
            logger.debug("Settings window opened")

    def _on_settings_saved(self) -> None:
        """Handle settings saved event."""
        logger.debug("Settings saved callback triggered")
        self._log_message("Settings saved and reloaded.")
        self.settings_window = None
