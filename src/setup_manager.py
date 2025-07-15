"""
Setup mode handler for Revolution Idle Sacrifice Automation.

This module manages the interactive setup process where users configure
zodiac slots, sacrifice box, and sacrifice button coordinates and colors.
"""

import time

from config.settings import MAX_ZODIAC_SLOTS
from src.input_handlers import MouseHandler, SetupState
from utils.display_utils import show_message


class SetupManager:
    """Manages the setup process for configuring automation coordinates and colors."""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.setup_state = SetupState()
        self.mouse_handler = MouseHandler(self.setup_state, self._on_setup_complete)
        self.setup_complete = False

    def run_setup_mode(self):
        """Handle the interactive setup process for multiple zodiac slots."""
        # Reset for a new setup session
        self.setup_state.reset()
        self.setup_complete = False

        # Set mouse handler to setup mode
        self.mouse_handler.set_mode("setup")

        self._display_setup_instructions()

        # Keep the setup process active until completed
        while not self.setup_complete:
            time.sleep(0.1)  # Small sleep to prevent busy-waiting

        show_message("Setup mode completed. Returning to main menu.", level="info")

    def _display_setup_instructions(self):
        """Display instructions for the setup process."""
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
            "Ready to capture Zodiac Slot 1. Left-click on the first zodiac slot."
        )

    def _on_setup_complete(self):
        """Callback when setup is completed."""
        # Copy setup data to config manager
        self.config_manager.click_coords = self.setup_state.click_coords.copy()
        self.config_manager.target_rgbs = self.setup_state.target_rgbs.copy()

        # Save configuration
        if self.config_manager.save_config():
            show_message("Configuration saved successfully!")
        else:
            show_message("Failed to save configuration.", level="info")

        self.setup_complete = True

    def get_mouse_handler(self):
        """Get the mouse handler for listener registration."""
        return self.mouse_handler
