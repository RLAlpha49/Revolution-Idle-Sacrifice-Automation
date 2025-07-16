"""
GUI application for Revolution Idle Sacrifice Automation using CustomTkinter.

This module provides a modern, user-friendly graphical interface for the
Revolution Idle Sacrifice Automation script, replacing the CLI interface
when GUI mode is selected.
"""

import threading
import time
from typing import Optional

import customtkinter as ctk
import pynput.keyboard
import pynput.mouse

from config.config_manager import ConfigManager
from src.automation_engine import AutomationEngine
from src.help import get_help_text
from src.input_handlers import KeyboardHandler
from src.setup_manager import SetupManager


class RevolutionIdleGUI:
    """GUI application controller for Revolution Idle Sacrifice Automation."""

    def __init__(self):
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
        self.instructions_window: Optional[ctk.CTkToplevel] = None
        self.instructions_label: Optional[ctk.CTkLabel] = None

        # State management
        self.automation_thread: Optional[threading.Thread] = None
        self.is_automation_running = False
        self.setup_in_progress = False

    def run(self):
        """Initialize and run the GUI application."""
        self._create_gui()
        self._load_initial_config()
        if self.root:
            self.root.mainloop()

    def _create_gui(self):
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

    def _load_initial_config(self):
        """Load configuration at startup."""
        if self.config_manager.load_config():
            from config.settings import CONFIG_FILE

            self._log_message(f"Configuration loaded from {CONFIG_FILE}")
            self._update_status("Configuration loaded")
        else:
            self._log_message("No configuration found. Please run Setup Mode first.")
            self._update_status("No configuration - Setup required")

        self._update_button_states()

    def _update_status(self, message: str):
        """Update the status label."""
        if self.status_label:
            self.status_label.configure(text=message)

    def _log_message(self, message: str):
        """Add a message to the log textbox."""
        if self.log_textbox:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"
            self.log_textbox.insert("end", formatted_message)
            self.log_textbox.see("end")

    def _update_button_states(self):
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

    def _on_setup_click(self):
        """Handle setup button click."""
        if self.setup_in_progress:
            return

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

    def _run_setup_thread(self):
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

    def _start_listeners(self):
        """Start mouse and keyboard listeners."""
        mouse_handler = self.setup_manager.get_mouse_handler()
        self.mouse_listener = pynput.mouse.Listener(on_click=mouse_handler.on_click)
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press=self.keyboard_handler.on_press
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

    def _stop_listeners(self):
        """Stop mouse and keyboard listeners."""
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener.join()

        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener.join()

    def _on_setup_complete(self):
        """Handle setup completion."""
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup completed")
        self._log_message("Setup mode completed successfully!")

        # Update instructions window instead of closing it
        if self.instructions_window and self.instructions_label:
            self.instructions_label.configure(
                text="Setup Complete!\n\nAll components have been configured successfully. The configuration has been saved.\n\nYou can now close this window and start automation."
            )

        # Reload configuration
        if self.config_manager.load_config():
            self._log_message("Configuration reloaded.")

    def _on_setup_error(self, error_msg: str):
        """Handle setup errors."""
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup failed")
        self._log_message(f"Setup mode failed: {error_msg}")

    def _on_setup_cancelled(self):
        """Handle setup cancellation."""
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup cancelled")
        self._log_message("Setup mode cancelled by user.")

        # Close instructions window
        if self.instructions_window:
            self.instructions_window.destroy()
            self.instructions_window = None
            self.instructions_label = None

    def _on_automation_click(self):
        """Handle automation button click."""
        if self.is_automation_running:
            self._stop_automation()
        else:
            self._start_automation()

    def _start_automation(self):
        """Start the automation process."""
        if not self.config_manager.validate_config():
            self._log_message(
                "Cannot start automation: Invalid or missing configuration."
            )
            self._log_message("Please run Setup Mode first.")
            return

        self.is_automation_running = True
        self._update_button_states()
        self._update_status("Automation running")
        self._log_message("Starting automation...")
        self._log_message("Press 'q' to stop automation at any time.")

        # Run automation in a separate thread
        self.automation_thread = threading.Thread(target=self._run_automation_thread)
        self.automation_thread.daemon = True
        self.automation_thread.start()

    def _run_automation_thread(self):
        """Run automation in a separate thread."""
        try:
            # Create a stop callback that checks our flag
            def stop_callback():
                return not self.is_automation_running

            self.automation_engine.run_automation(
                self.config_manager.click_coords,
                self.config_manager.target_rgbs,
                stop_callback,
            )

        except Exception as e:  # pylint: disable=broad-except
            if self.root:
                self.root.after(0, lambda err=str(e): self._on_automation_error(err))
        finally:
            # Update GUI after automation stops
            if self.root:
                self.root.after(0, self._on_automation_stopped)

    def _stop_automation(self):
        """Stop the automation process."""
        self.is_automation_running = False
        self.automation_engine.stop()
        self._log_message("Stopping automation...")

    def _on_stop_automation(self):
        """Callback when automation should be stopped."""
        self.automation_engine.stop()

    def _on_automation_stopped(self):
        """Handle automation stopping."""
        self.is_automation_running = False
        self._update_button_states()
        self._update_status("Automation stopped")
        self._log_message("Automation stopped.")

    def _on_automation_error(self, error_msg: str):
        """Handle automation errors."""
        self.is_automation_running = False
        self._update_button_states()
        self._update_status("Automation error")
        self._log_message(f"Automation error: {error_msg}")

    def _on_help_click(self):
        """Handle help button click."""
        self._show_help_window()

    def _show_help_window(self):
        """Show help information in a new window."""
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("Help - Revolution Idle Sacrifice Automation")
        help_window.geometry("700x500")
        help_window.transient(self.root)
        help_window.grab_set()

        # Help content frame
        help_frame = ctk.CTkFrame(help_window)
        help_frame.pack(fill="both", expand=True, padx=20, pady=20)
        help_frame.grid_rowconfigure(0, weight=1)
        help_frame.grid_columnconfigure(0, weight=1)

        # Help text
        help_textbox = ctk.CTkTextbox(help_frame, wrap="word")
        help_textbox.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))

        # Insert help content
        help_content = get_help_text()
        help_textbox.insert("0.0", help_content)
        help_textbox.configure(state="disabled")

        # Close button
        close_button = ctk.CTkButton(
            help_frame, text="Close", command=help_window.destroy, width=100
        )
        close_button.grid(row=1, column=0, pady=(0, 20))

    def _on_settings_click(self):
        """Handle settings button click."""
        try:
            from config.settings import reload_settings  # pylint: disable=import-outside-toplevel

            reload_settings()
            self._log_message("Settings reloaded successfully from user_settings.json")
            self._log_message(
                "Note: Some settings may require restarting the script to take effect."
            )
            self._update_status("Settings reloaded")
        except Exception as e:  # pylint: disable=broad-except
            self._log_message(f"Failed to reload settings: {e}")
            self._update_status("Settings reload failed")

    def _show_setup_instructions(self):
        """Show setup instructions in a dedicated window."""
        if self.instructions_window:
            self.instructions_window.destroy()

        self.instructions_window = ctk.CTkToplevel(self.root)
        self.instructions_window.title("Setup Instructions - Revolution Idle")
        self.instructions_window.geometry("650x500")
        self.instructions_window.transient(self.root)
        self.instructions_window.attributes("-topmost", True)

        # Make window stay open independently after a short delay
        def make_independent():
            if self.instructions_window:
                self.instructions_window.transient(None)

        self.instructions_window.after(100, make_independent)

        # Create main frame
        main_frame = ctk.CTkFrame(self.instructions_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Revolution Idle Setup Mode",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.grid(row=0, column=0, pady=(10, 20))

        # Instructions text area
        self.instructions_label = ctk.CTkLabel(
            main_frame,
            text="Initializing setup mode...",
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=600,
        )
        self.instructions_label.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(20, 10))
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Disable window detection button
        disable_detection_button = ctk.CTkButton(
            button_frame,
            text="Disable Window Detection",
            command=self._disable_window_detection,
            width=150,
            fg_color="orange",
        )
        disable_detection_button.grid(row=0, column=0, padx=5, pady=10)

        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel Setup",
            command=self._cancel_setup,
            width=120,
            fg_color="red",
        )
        cancel_button.grid(row=0, column=1, padx=5, pady=10)

        # Close button
        close_button = ctk.CTkButton(
            button_frame,
            text="Close Window",
            command=self._close_instructions_window,
            width=120,
            fg_color="gray",
        )
        close_button.grid(row=0, column=2, padx=5, pady=10)

    def _update_setup_instructions(self, message: str):
        """Update the setup instructions display."""
        if self.instructions_label:
            self.instructions_label.configure(text=message)

    def _cancel_setup(self):
        """Cancel the setup process."""
        if self.instructions_window:
            self.instructions_window.destroy()
            self.instructions_window = None
            self.instructions_label = None

        self.setup_manager.cancel_setup()
        self.setup_in_progress = False
        self._update_button_states()
        self._update_status("Setup cancelled")
        self._log_message("Setup mode cancelled by user.")
        self._stop_listeners()

    def _disable_window_detection(self):
        """Disable window detection for the current setup session."""
        if hasattr(self.setup_manager, "mouse_handler"):
            self.setup_manager.mouse_handler.disable_window_filtering()
            self._log_message(
                "Window detection disabled. All clicks will now be registered regardless of window."
            )
            self._update_setup_instructions(
                "Window detection disabled!\n\nAll clicks will now be registered regardless of which window you click on.\n\nPlease continue with the setup process."
            )

    def _close_instructions_window(self):
        """Close the instructions window manually."""
        if self.instructions_window:
            self.instructions_window.destroy()
            self.instructions_window = None
            self.instructions_label = None
            self._log_message("Instructions window closed manually.")
