"""
Input handlers for mouse and keyboard events.

This module handles mouse clicks during setup mode and keyboard presses
during automation mode for the Revolution Idle automation script.
"""

from typing import Any, Callable, Optional

import pygetwindow as gw  # type: ignore
import pynput.keyboard
import pynput.mouse

from config.settings import MAX_ZODIAC_SLOTS, STOP_KEY
from utils.color_utils import get_pixel_color
from utils.display_utils import show_message


class SetupState:
    """Manages the state during setup mode."""

    def __init__(self) -> None:
        # "zodiac_slots", "sacrifice_box", "sacrifice_button", "complete"
        self.current_step: str = "zodiac_slots"
        self.zodiac_slot_count: int = 0
        self.click_coords: dict = {}
        self.target_rgbs: dict = {}

    def reset(self) -> None:
        """Reset setup state for a new setup session."""
        self.current_step = "zodiac_slots"
        self.zodiac_slot_count = 0
        self.click_coords = {}
        self.target_rgbs = {}


class MouseHandler:
    """Handles mouse click events during setup mode."""

    def __init__(
        self, setup_state: SetupState, on_setup_complete: Optional[Callable] = None
    ) -> None:
        self.setup_state = setup_state
        self.on_setup_complete = on_setup_complete
        self.current_mode: Optional[str] = None

        # GUI callback functions
        self.gui_update_instructions: Optional[Callable[[str], None]] = None
        self.gui_log_message: Optional[Callable[[str], None]] = None

        # Window detection settings
        self.window_filtering_enabled: bool = True
        self.debug_mode: bool = False

        # Debugging and filtering options
        self.debug_mode = False
        self.window_filtering_enabled = True

    def set_gui_callbacks(
        self,
        update_instructions_callback: Callable[[str], None],
        log_message_callback: Callable[[str], None],
    ) -> None:
        """Set callback functions for GUI integration."""
        self.gui_update_instructions = update_instructions_callback
        self.gui_log_message = log_message_callback

    def set_mode(self, mode: str) -> None:
        """Set the current operation mode."""
        self.current_mode = mode

    def enable_debug_mode(self) -> None:
        """Enable debug mode to show all window detection details."""
        self.debug_mode = True

    def disable_window_filtering(self) -> None:
        """Disable window filtering for compatibility with unusual setups."""
        self.window_filtering_enabled = False

    def on_click(
        self, x: int, y: int, button: pynput.mouse.Button, pressed: bool
    ) -> None:
        """
        Callback function executed when a mouse button is pressed or released.
        Behavior depends on the current mode ('setup' or 'automation').
        """
        # We only care about button presses, not releases
        if not pressed:
            return

        if self.current_mode == "setup":
            self._handle_setup_click(x, y, button)
        elif self.current_mode == "automation":
            show_message(
                f"Click detected at: X={x}, Y={y}. In automation mode, "
                "clicks are performed by the script, not used for setup.",
                level="debug",
            )

    def _handle_setup_click(self, x: int, y: int, button: pynput.mouse.Button) -> None:
        """Handle mouse clicks during setup mode."""
        # Check if the click is on the Revolution Idle window (if filtering is enabled)
        if self.window_filtering_enabled and not self._is_click_on_revolution_idle(
            x, y
        ):
            return  # Ignore clicks that are not on the Revolution Idle window

        if button == pynput.mouse.Button.left:
            if self.setup_state.current_step == "zodiac_slots":
                self._handle_zodiac_slot_click(x, y)
            elif self.setup_state.current_step == "sacrifice_box":
                self._handle_sacrifice_box_click(x, y)
            elif self.setup_state.current_step == "sacrifice_button":
                self._handle_sacrifice_button_click(x, y)

        elif button == pynput.mouse.Button.right:
            if (
                self.setup_state.current_step == "zodiac_slots"
                and self.setup_state.zodiac_slot_count > 0
            ):
                self._finish_zodiac_slots()
            else:
                right_click_message = "Right-click detected. In setup mode, right-click is only used to finish adding zodiac slots."
                if self.gui_log_message:
                    self.gui_log_message(right_click_message)
                else:
                    show_message(right_click_message, level="info")

    def _handle_zodiac_slot_click(self, x: int, y: int) -> None:
        """Handle clicks for zodiac slot setup."""
        # Initialize zodiac slots lists if not already done
        if "zodiac_slots" not in self.setup_state.click_coords:
            self.setup_state.click_coords["zodiac_slots"] = []
            self.setup_state.target_rgbs["zodiac_slots"] = []

        # Capture zodiac slot coordinates and color
        self.setup_state.click_coords["zodiac_slots"].append((x, y))
        slot_color = get_pixel_color(x, y)
        self.setup_state.target_rgbs["zodiac_slots"].append(slot_color)
        self.setup_state.zodiac_slot_count += 1

        # Display message based on GUI or CLI mode
        capture_message = f"Zodiac Slot {self.setup_state.zodiac_slot_count} captured: ({x}, {y}) with color {slot_color}."

        if self.gui_log_message:
            self.gui_log_message(capture_message)
        else:
            show_message(capture_message)

        # Update instructions for next step
        if MAX_ZODIAC_SLOTS == -1:
            # Unlimited slots - show option to continue or finish
            next_instructions = (
                f"Zodiac Slot {self.setup_state.zodiac_slot_count} captured!\n\n"
            )
            next_instructions += f"Left-click to add Zodiac Slot {self.setup_state.zodiac_slot_count + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
        elif self.setup_state.zodiac_slot_count < MAX_ZODIAC_SLOTS:
            # Limited slots - show current count and option to continue
            next_instructions = (
                f"Zodiac Slot {self.setup_state.zodiac_slot_count} captured!\n\n"
            )
            next_instructions += f"Left-click to add Zodiac Slot {self.setup_state.zodiac_slot_count + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
        else:
            # Reached maximum limit
            next_instructions = (
                f"Maximum zodiac slots ({MAX_ZODIAC_SLOTS}) reached!\n\n"
            )
            next_instructions += "Now left-click to set the Sacrifice Drag Box."
            self.setup_state.current_step = "sacrifice_box"

        if self.gui_update_instructions:
            self.gui_update_instructions(next_instructions)
        else:
            if MAX_ZODIAC_SLOTS == -1:
                show_message(
                    f"Left-click to add Zodiac Slot {self.setup_state.zodiac_slot_count + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
                )
            elif self.setup_state.zodiac_slot_count < MAX_ZODIAC_SLOTS:
                show_message(
                    f"Left-click to add Zodiac Slot {self.setup_state.zodiac_slot_count + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
                )
            else:
                show_message(
                    f"Maximum zodiac slots ({MAX_ZODIAC_SLOTS}) reached. Now left-click to set the Sacrifice Drag Box."
                )

    def _handle_sacrifice_box_click(self, x: int, y: int) -> None:
        """Handle clicks for sacrifice box setup."""
        self.setup_state.click_coords["sacrifice_box"] = (x, y)

        capture_message = f"Sacrifice Drag Box captured: ({x}, {y})."
        next_instructions = "Sacrifice Drag Box captured!\n\nNow left-click to set the Sacrifice Button."

        if self.gui_log_message:
            self.gui_log_message(capture_message)
        else:
            show_message(capture_message)

        if self.gui_update_instructions:
            self.gui_update_instructions(next_instructions)
        else:
            show_message("Now left-click to set the Sacrifice Button.")

        self.setup_state.current_step = "sacrifice_button"

    def _handle_sacrifice_button_click(self, x: int, y: int) -> None:
        """Handle clicks for sacrifice button setup."""
        # Hardcoded RGB for the Sacrifice Button (for reliability)
        sacrifice_button_rgb = (219, 124, 0)

        self.setup_state.click_coords["sacrifice_button"] = (x, y)
        # Hardcoded RGB for the Sacrifice Button
        self.setup_state.target_rgbs["sacrifice_button"] = sacrifice_button_rgb

        capture_message = f"Sacrifice Button captured: ({x}, {y}). Its target color is hardcoded to {sacrifice_button_rgb}."
        completion_message = f"Setup complete! Configured {len(self.setup_state.click_coords['zodiac_slots'])} zodiac slots. Saving Revolution Idle configuration."
        final_instructions = "Setup Complete!\n\nAll components have been configured successfully. The configuration will now be saved."

        if self.gui_log_message:
            self.gui_log_message(capture_message)
            self.gui_log_message(completion_message)
        else:
            show_message(capture_message)
            show_message(completion_message)

        if self.gui_update_instructions:
            self.gui_update_instructions(final_instructions)

        self.setup_state.current_step = "complete"

        if self.on_setup_complete:
            self.on_setup_complete()

    def _finish_zodiac_slots(self) -> None:
        """Finish adding zodiac slots and proceed to sacrifice box."""
        message = f"Finished adding zodiac slots. {self.setup_state.zodiac_slot_count} zodiac slots configured."
        next_instructions = f"Zodiac slots configuration complete!\n\n{self.setup_state.zodiac_slot_count} zodiac slots have been configured.\n\nNow left-click to set the Sacrifice Drag Box."

        if self.gui_log_message:
            self.gui_log_message(message)
        else:
            show_message(message)

        if self.gui_update_instructions:
            self.gui_update_instructions(next_instructions)
        else:
            show_message("Now left-click to set the Sacrifice Drag Box.")

        self.setup_state.current_step = "sacrifice_box"

    def _is_click_on_revolution_idle(self, x: int, y: int) -> bool:
        """
        Check if the click coordinates are within the Revolution Idle window.

        Args:
            x: X coordinate of the click
            y: Y coordinate of the click

        Returns:
            True if click is on Revolution Idle window, False otherwise
        """
        try:
            # Get all windows at the click position
            windows_at_position = gw.getWindowsAt(x, y)

            if not windows_at_position:
                return False

            # Get the topmost window
            top_window = windows_at_position[0]
            top_window_title = top_window.title.strip()

            # Check if the topmost window is Revolution Idle
            if top_window_title == "Revolution Idle":
                if self.gui_log_message:
                    self.gui_log_message(
                        "Click registered on Revolution Idle game window"
                    )
                return True

            # Special case: If the top window is Discord overlay, check the window beneath it
            if top_window_title.lower() == "discord overlay":
                for window in windows_at_position[
                    1:
                ]:  # Skip the first (Discord overlay)
                    window_title = window.title.strip()
                    if window_title == "Revolution Idle":
                        if self.gui_log_message:
                            self.gui_log_message(
                                "Click registered on Revolution Idle game window (beneath Discord overlay)"
                            )
                        return True

                # Discord overlay detected but no Revolution Idle beneath
                if self.gui_log_message:
                    self.gui_log_message(
                        "Click ignored - Discord overlay detected but no Revolution Idle window found beneath it"
                    )
                return False

            # Check for browser tabs that might contain "Revolution Idle" as the exact title
            browser_keywords = ["chrome", "firefox", "edge", "browser", "webkit"]
            if any(browser in top_window_title.lower() for browser in browser_keywords):
                if (
                    "Revolution Idle" in top_window_title
                    and "Revolution Idle Sacrifice Automation" not in top_window_title
                    and "Setup Instructions" not in top_window_title
                ):
                    if self.gui_log_message:
                        self.gui_log_message(
                            f"Click registered on browser window with Revolution Idle: {top_window_title}"
                        )
                    return True

            # Log what was clicked for debugging
            if self.gui_log_message:
                self.gui_log_message(
                    f"Click ignored - not on Revolution Idle game window. Clicked on: '{top_window_title}'"
                )
            elif self.current_mode == "setup":
                show_message(
                    f"Click ignored - not on Revolution Idle game window. Clicked on: '{top_window_title}'",
                    level="debug",
                )

            return False

        except Exception as e:  # pylint: disable=broad-except
            # If window detection fails, log the error but allow the click
            # This ensures the setup still works even if window detection has issues
            error_msg = f"Window detection failed: {e}. Processing click anyway for compatibility."
            if self.gui_log_message:
                self.gui_log_message(error_msg)
            else:
                show_message(error_msg, level="debug")
            return True


class KeyboardHandler:
    """Handles keyboard events during automation mode."""

    def __init__(self, on_stop_automation: Optional[Callable] = None) -> None:
        self.on_stop_automation = on_stop_automation
        self.stop_automation: bool = False

    def reset_stop_flag(self) -> None:
        """Reset the stop automation flag."""
        self.stop_automation = False

    def on_press(self, key: Any) -> None:
        """
        Callback function executed when a keyboard key is pressed.
        Used to detect the configured STOP_KEY to stop the automation.
        """
        # Only process the stop key if automation is currently running
        if not self.stop_automation:
            try:
                # Check if it's a character key
                if isinstance(key, pynput.keyboard.KeyCode):
                    if key.char == STOP_KEY:
                        show_message(
                            f" '{STOP_KEY}' key pressed. Stopping Revolution Idle Sacrifice Automation.",
                            level="info",
                        )
                        self.stop_automation = True
                        if self.on_stop_automation:
                            self.on_stop_automation()
                # Check if it's a special key
                elif isinstance(key, pynput.keyboard.Key):
                    if key.name == STOP_KEY:
                        show_message(
                            f" '{STOP_KEY}' key pressed. Stopping Revolution Idle Sacrifice Automation.",
                            level="info",
                        )
                        self.stop_automation = True
                        if self.on_stop_automation:
                            self.on_stop_automation()
            except AttributeError:
                # This catch block is for unexpected key types, though unlikely with pynput.
                show_message(
                    f"An unknown key type was pressed: {key}. Not the configured STOP_KEY.",
                    level="debug",
                )
