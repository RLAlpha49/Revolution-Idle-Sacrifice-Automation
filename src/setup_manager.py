"""
Setup mode handler for Revolution Idle Sacrifice Automation.

This module manages the interactive setup process where users configure
zodiac slots, sacrifice box, and sacrifice button coordinates and colors.
"""

import logging
import time
from typing import Callable, Optional

import pygetwindow as gw  # type: ignore

from config.settings import MAX_ZODIAC_SLOTS
from src.input_handlers import MouseHandler, SetupState
from utils.display_utils import show_message

# Set up module logger
logger = logging.getLogger(__name__)


class SetupManager:
    """Manages the setup process for configuring automation coordinates and colors."""

    def __init__(self, config_manager) -> None:
        self.config_manager = config_manager
        self.setup_state = SetupState()
        self.mouse_handler = MouseHandler(self.setup_state, self._on_setup_complete)
        self.setup_complete: bool = False
        self.setup_cancelled: bool = False

        # GUI callback functions
        self.gui_update_instructions: Optional[Callable[[str], None]] = None
        self.gui_log_message: Optional[Callable[[str], None]] = None
        self.gui_show_error: Optional[Callable[[str, str], None]] = None

        logger.debug("SetupManager initialized")

    def set_gui_callbacks(
        self,
        update_instructions_callback: Callable[[str], None],
        log_message_callback: Callable[[str], None],
        show_error_callback: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        """Set callback functions for GUI integration.

        Args:
            update_instructions_callback: Callback to update setup instructions
            log_message_callback: Callback to log messages
            show_error_callback: Optional callback to show error dialogs
        """
        self.gui_update_instructions = update_instructions_callback
        self.gui_log_message = log_message_callback
        self.gui_show_error = show_error_callback

        # Also set callbacks for the mouse handler
        self.mouse_handler.set_gui_callbacks(
            update_instructions_callback, log_message_callback
        )

        logger.debug("GUI callbacks set for SetupManager")

    def cancel_setup(self) -> None:
        """Cancel the setup process."""
        logger.info("Setup cancelled by user")
        self.setup_cancelled = True
        self.setup_complete = True  # This will exit the setup loop

    def run_setup_mode(self) -> None:
        """Handle the interactive setup process for multiple zodiac slots."""
        logger.info("Starting setup mode")

        # Check if Revolution Idle game is running before starting setup
        if not self._check_revolution_idle_running():
            error_title = "Revolution Idle Game Not Detected"
            error_message = (
                "Revolution Idle game not detected!\n\n"
                "Please make sure the Revolution Idle game is running before starting setup.\n"
                "The setup process requires the game window to be open to capture coordinates and colors."
            )

            logger.warning("Setup cancelled - Revolution Idle game not detected")

            if self.gui_show_error:
                # Show error dialog like advanced mode does
                self.gui_show_error(error_title, error_message)
                if self.gui_log_message:
                    self.gui_log_message(
                        "Setup cancelled: Revolution Idle game not detected."
                    )
            elif self.gui_log_message:
                # Fallback to instructions update if no error dialog available
                self.gui_log_message(
                    "Setup cancelled: Revolution Idle game not detected."
                )
                if self.gui_update_instructions:
                    self.gui_update_instructions(error_message)
            else:
                # CLI mode fallback
                show_message(
                    "Setup cancelled: Revolution Idle game not detected.", level="error"
                )
                show_message(error_message, level="error")

            # Mark setup as cancelled and complete
            self.setup_cancelled = True
            self.setup_complete = True
            return

        # Reset for a new setup session
        self.setup_state.reset()
        self.setup_complete = False
        self.setup_cancelled = False

        # Set mouse handler to setup mode
        self.mouse_handler.set_mode("setup")

        self._display_setup_instructions()

        # Keep the setup process active until completed
        logger.debug("Entering setup wait loop")
        while not self.setup_complete:
            time.sleep(0.1)  # Small sleep to prevent busy-waiting

        if not self.setup_cancelled and not self.gui_log_message:
            logger.info("Setup mode completed successfully")
            show_message("Setup mode completed. Returning to main menu.", level="info")
        elif self.setup_cancelled:
            logger.info("Setup mode was cancelled")

    def _display_setup_instructions(self) -> None:
        """Display instructions for the setup process."""
        logger.debug("Displaying setup instructions")

        if self.gui_update_instructions:
            # GUI mode - show instructions in the GUI window
            instructions = "Entering Setup Mode for Revolution Idle with Multiple Zodiac Slots support.\n\n"

            if MAX_ZODIAC_SLOTS == -1:
                instructions += "You can configure unlimited zodiac slots for sacrifice automation.\n\n"
                logger.debug("Setup mode: unlimited zodiac slots")
            else:
                instructions += f"You can configure up to {MAX_ZODIAC_SLOTS} zodiac slots for sacrifice automation.\n\n"
                logger.debug("Setup mode: maximum %d zodiac slots", MAX_ZODIAC_SLOTS)

            instructions += "IMPORTANT: Only clicks on the exact 'Revolution Idle' game window will be registered during setup.\n"
            instructions += "Clicks on this setup window, the main automation window, or any other windows will be ignored.\n"
            instructions += "Note: Discord overlay is automatically handled - clicks will register on Revolution Idle beneath it.\n"
            instructions += "If you're having issues with window detection, use the 'Disable Window Detection' button below.\n\n"

            instructions += "Setup Steps:\n"
            instructions += "1. Left-click on each Zodiac Slot you want to monitor (at least 1 required)\n"
            instructions += "2. Right-click when finished adding zodiac slots to proceed to Sacrifice Drag Box\n"
            instructions += "3. Left-click on the Sacrifice Drag Box (where zodiacs are dragged to)\n"
            instructions += "4. Left-click on the Sacrifice Button (its color is hardcoded for reliability)\n\n"
            instructions += "Ready to capture Zodiac Slot 1. Left-click on the first zodiac slot in the 'Revolution Idle' game window."

            self.gui_update_instructions(instructions)
            logger.debug("Setup instructions displayed in GUI")

            if self.gui_log_message:
                self.gui_log_message(
                    "Setup instructions displayed. Only clicks on the exact 'Revolution Idle' game window will be registered."
                )
        else:
            # CLI mode - use original display method
            logger.debug("Displaying CLI setup instructions")
            show_message(
                "Entering Setup Mode for Revolution Idle with Multiple Zodiac Slots support.",
                level="info",
            )

            if MAX_ZODIAC_SLOTS == -1:
                show_message(
                    "You can configure unlimited zodiac slots for sacrifice automation.",
                    level="info",
                )
            else:
                show_message(
                    f"You can configure up to {MAX_ZODIAC_SLOTS} zodiac slots for sacrifice automation.",
                    level="info",
                )

            show_message(
                "IMPORTANT: Only clicks on the exact 'Revolution Idle' game window will be registered during setup.",
                level="info",
            )
            show_message(
                "Clicks on script windows or other applications will be ignored to prevent accidental captures.",
                level="info",
            )
            show_message(
                "Note: Discord overlay is automatically handled, but other overlays are not.",
                level="info",
            )
            show_message(
                "1. Left-click on each Zodiac Slot you want to monitor (at least 1 required).",
                level="info",
            )
            show_message(
                "2. Right-click when you're finished adding zodiac slots to proceed to the Sacrifice Drag Box.",
                level="info",
            )
            show_message(
                "3. Left-click on the Sacrifice Drag Box (where zodiacs are dragged to).",
                level="info",
            )
            show_message(
                "4. Left-click on the Sacrifice Button (its color is hardcoded for reliability).",
                level="info",
            )
            show_message(
                "Ready to capture Zodiac Slot 1. Left-click on the first zodiac slot in the exact 'Revolution Idle' game window."
            )

    def _on_setup_complete(self) -> None:
        """Callback when setup is completed."""
        if self.setup_cancelled:
            logger.info("Setup completion callback received but setup was cancelled")
            if self.gui_log_message:
                self.gui_log_message("Setup cancelled by user.")
            else:
                show_message("Setup cancelled by user.", level="info")
            return

        logger.info("Setup completed, saving configuration")

        # Copy setup data to config manager
        self.config_manager.click_coords = self.setup_state.click_coords.copy()
        self.config_manager.target_rgbs = self.setup_state.target_rgbs.copy()

        # Save configuration
        if self.config_manager.save_config():
            logger.info("Configuration saved successfully")
            if self.gui_log_message:
                self.gui_log_message("Configuration saved successfully!")
            else:
                show_message("Configuration saved successfully!")
        else:
            logger.error("Failed to save configuration")
            if self.gui_log_message:
                self.gui_log_message("Failed to save configuration.")
            else:
                show_message("Failed to save configuration.", level="info")

        self.setup_complete = True

    def get_mouse_handler(self) -> MouseHandler:
        """Get the mouse handler for listener registration."""
        return self.mouse_handler

    def _check_revolution_idle_running(self) -> bool:
        """Check if Revolution Idle game is currently running.

        Returns:
            bool: True if Revolution Idle window is found, False otherwise.
        """
        try:
            # Look for windows with "Revolution Idle" in the title
            all_windows = gw.getAllWindows()

            game_windows = []
            for window in all_windows:
                window_title = window.title.strip()

                # Only accept windows with EXACTLY "Revolution Idle" as the title
                # This is much stricter and avoids matching editors, file paths, etc.
                if window_title == "Revolution Idle":
                    # Additional validation: check if window has reasonable game dimensions
                    # Game windows are typically larger than 400x300 pixels
                    try:
                        width = window.width
                        height = window.height

                        if width >= 400 and height >= 300:
                            game_windows.append(window)
                            logger.debug(
                                "Found valid Revolution Idle game window: '%s' (%dx%d)",
                                window_title,
                                width,
                                height,
                            )
                        else:
                            logger.debug(
                                "Skipping small window '%s' (%dx%d) - likely not the game",
                                window_title,
                                width,
                                height,
                            )
                    except (AttributeError, TypeError):
                        # If we can't get dimensions, skip this window
                        logger.debug(
                            "Skipping window '%s' - cannot get dimensions", window_title
                        )
                        continue
                else:
                    # Log any window that contains "Revolution Idle" but doesn't match exactly
                    if "revolution idle" in window_title.lower():
                        logger.debug(
                            "Skipping non-exact match: '%s' (not exactly 'Revolution Idle')",
                            window_title,
                        )

            if game_windows:
                logger.info(
                    "Revolution Idle game detected - %d valid game window(s) found",
                    len(game_windows),
                )
                return True
            else:
                logger.warning(
                    "No Revolution Idle game windows found (must be exactly titled 'Revolution Idle')"
                )
                return False

        except Exception as e:
            logger.error(
                "Error checking for Revolution Idle game: %s", e, exc_info=True
            )
            # If there's an error detecting windows, be conservative and assume game is NOT running
            # This prevents false positives
            return False

    def disable_window_detection(self) -> None:
        """Disable window detection for the mouse handler."""
        logger.info("Disabling window detection for setup")
        self.mouse_handler.disable_window_filtering()

    def enable_debug_mode(self) -> None:
        """Enable debug mode for detailed window detection logging."""
        logger.info("Enabling debug mode for setup")
        self.mouse_handler.enable_debug_mode()
