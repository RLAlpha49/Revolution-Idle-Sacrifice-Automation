"""
Input handlers for mouse and keyboard events.

This module handles mouse clicks during setup mode and keyboard presses
during automation mode for the Revolution Idle automation script.
"""

import logging
from typing import Any, Callable, Optional

import pygetwindow as gw  # type: ignore
import pynput.keyboard
import pynput.mouse

from config.settings import MAX_ZODIAC_SLOTS, STOP_KEY
from utils.color_utils import get_pixel_color
from utils.display_utils import show_message

# Set up module logger
logger = logging.getLogger(__name__)


class SetupState:
    """Manages the state during setup mode."""

    def __init__(self) -> None:
        # "zodiac_slots", "sacrifice_box", "sacrifice_button", "complete"
        self.current_step: str = "zodiac_slots"
        self.zodiac_slot_count: int = 0
        self.click_coords: dict = {}
        self.target_rgbs: dict = {}
        logger.debug("SetupState initialized")

    def reset(self) -> None:
        """Reset setup state for a new setup session."""
        self.current_step = "zodiac_slots"
        self.zodiac_slot_count = 0
        self.click_coords = {}
        self.target_rgbs = {}
        logger.debug("SetupState reset")


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

        logger.debug("MouseHandler initialized")

    def set_gui_callbacks(
        self,
        update_instructions_callback: Callable[[str], None],
        log_message_callback: Callable[[str], None],
    ) -> None:
        """Set callback functions for GUI integration."""
        self.gui_update_instructions = update_instructions_callback
        self.gui_log_message = log_message_callback
        logger.debug("GUI callbacks set for MouseHandler")

    def set_mode(self, mode: str) -> None:
        """Set the current operation mode."""
        logger.debug("Setting mouse handler mode to: %s", mode)
        self.current_mode = mode

    def enable_debug_mode(self) -> None:
        """Enable debug mode to show all window detection details."""
        self.debug_mode = True
        logger.debug("Debug mode enabled for MouseHandler")

    def disable_window_filtering(self) -> None:
        """Disable window filtering for compatibility with unusual setups."""
        self.window_filtering_enabled = False
        logger.info("Window filtering disabled for setup")

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
            logger.debug("Setup click detected: (%d, %d) with button %s", x, y, button)
            self._handle_setup_click(x, y, button)
        elif self.current_mode == "automation":
            logger.debug(
                "Automation click detected: (%d, %d) with button %s", x, y, button
            )
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
            logger.debug(
                "Click at (%d, %d) ignored - not on Revolution Idle window", x, y
            )
            return  # Ignore clicks that are not on the Revolution Idle window

        if button == pynput.mouse.Button.left:
            logger.debug(
                "Left click at (%d, %d) in step: %s",
                x,
                y,
                self.setup_state.current_step,
            )
            if self.setup_state.current_step == "zodiac_slots":
                self._handle_zodiac_slot_click(x, y)
            elif self.setup_state.current_step == "sacrifice_box":
                self._handle_sacrifice_box_click(x, y)
            elif self.setup_state.current_step == "sacrifice_button":
                self._handle_sacrifice_button_click(x, y)

        elif button == pynput.mouse.Button.right:
            logger.debug(
                "Right click at (%d, %d) in step: %s",
                x,
                y,
                self.setup_state.current_step,
            )
            if (
                self.setup_state.current_step == "zodiac_slots"
                and self.setup_state.zodiac_slot_count > 0
            ):
                self._finish_zodiac_slots()
            else:
                right_click_message = "Right-click detected. In setup mode, right-click is only used to finish adding zodiac slots."
                logger.info(
                    "Right click ignored - not in zodiac slots step or no slots configured"
                )
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
            logger.debug("Initialized zodiac slots arrays")

        # Capture zodiac slot coordinates and color
        self.setup_state.click_coords["zodiac_slots"].append((x, y))
        slot_color = get_pixel_color(x, y)
        self.setup_state.target_rgbs["zodiac_slots"].append(slot_color)
        self.setup_state.zodiac_slot_count += 1

        logger.info(
            "Zodiac Slot %d captured: (%d, %d) with color %s",
            self.setup_state.zodiac_slot_count,
            x,
            y,
            slot_color,
        )

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
            logger.info(
                "Maximum zodiac slots (%d) reached, moving to sacrifice box step",
                MAX_ZODIAC_SLOTS,
            )

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
        logger.info("Sacrifice Drag Box captured: (%d, %d)", x, y)

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
        logger.debug("Moving to sacrifice_button step")

    def _handle_sacrifice_button_click(self, x: int, y: int) -> None:
        """Handle clicks for sacrifice button setup."""
        # Hardcoded RGB for the Sacrifice Button (for reliability)
        sacrifice_button_rgb = (219, 124, 0)

        self.setup_state.click_coords["sacrifice_button"] = (x, y)
        # Hardcoded RGB for the Sacrifice Button
        self.setup_state.target_rgbs["sacrifice_button"] = sacrifice_button_rgb

        logger.info(
            "Sacrifice Button captured: (%d, %d) with hardcoded color %s",
            x,
            y,
            sacrifice_button_rgb,
        )

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
        logger.info("Setup completed successfully")

        if self.on_setup_complete:
            self.on_setup_complete()

    def _finish_zodiac_slots(self) -> None:
        """Finish adding zodiac slots and proceed to sacrifice box."""
        message = f"Finished adding zodiac slots. {self.setup_state.zodiac_slot_count} zodiac slots configured."
        next_instructions = f"Zodiac slots configuration complete!\n\n{self.setup_state.zodiac_slot_count} zodiac slots have been configured.\n\nNow left-click to set the Sacrifice Drag Box."

        logger.info(
            "Finished adding zodiac slots. %d slots configured",
            self.setup_state.zodiac_slot_count,
        )

        if self.gui_log_message:
            self.gui_log_message(message)
        else:
            show_message(message)

        if self.gui_update_instructions:
            self.gui_update_instructions(next_instructions)
        else:
            show_message("Now left-click to set the Sacrifice Drag Box.")

        self.setup_state.current_step = "sacrifice_box"
        logger.debug("Moving to sacrifice_box step")

    def _is_click_on_revolution_idle(self, x: int, y: int) -> bool:
        """
        Check if the click coordinates are within the Revolution Idle game window.
        This helps prevent accidental clicks on other windows during setup.
        """
        try:
            if not self.window_filtering_enabled:
                logger.debug("Window filtering disabled, accepting all clicks")
                return True

            # Try to find the Revolution Idle window using strict criteria
            revolution_idle_windows = []

            try:
                # Get all windows and check each one strictly
                all_windows = gw.getAllWindows()

                for window in all_windows:
                    window_title = window.title.strip()

                    # Only accept windows with EXACTLY "Revolution Idle" as the title
                    if window_title == "Revolution Idle":
                        # Additional validation: check if window has reasonable game dimensions
                        try:
                            width = window.width
                            height = window.height

                            if width >= 400 and height >= 300:
                                revolution_idle_windows.append(window)
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
                            logger.debug(
                                "Skipping window '%s' - cannot get dimensions",
                                window_title,
                            )
                            continue
                    elif window_title == "Discord":
                        # Also accept Discord windows for overlay support
                        revolution_idle_windows.append(window)
                        logger.debug(
                            "Found Discord window for overlay support: %s", window_title
                        )
                    else:
                        # Log any window that contains "Revolution Idle" but doesn't match exactly
                        if "revolution idle" in window_title.lower():
                            logger.debug(
                                "Skipping non-exact match: '%s' (not exactly 'Revolution Idle')",
                                window_title,
                            )

            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Error finding game windows: %s", e)
                # If we can't find the windows, disable filtering and accept all clicks
                self.window_filtering_enabled = False
                return True

            if not revolution_idle_windows:
                logger.warning("No Revolution Idle or Discord windows found")
                if self.debug_mode:
                    all_windows = gw.getAllTitles()
                    logger.debug("Available windows: %s", all_windows)
                return False

            # Check if the click is within any of the Revolution Idle windows
            for window in revolution_idle_windows:
                try:
                    if (
                        window.left <= x <= window.right
                        and window.top <= y <= window.bottom
                    ):
                        if self.debug_mode:
                            logger.debug(
                                "Click at (%d, %d) is within window '%s' at (%d, %d, %d, %d)",
                                x,
                                y,
                                window.title,
                                window.left,
                                window.top,
                                window.right,
                                window.bottom,
                            )
                        return True
                except Exception as e:  # pylint: disable=broad-except
                    logger.warning(
                        "Error checking window bounds for %s: %s", window.title, e
                    )
                    continue

            if self.debug_mode:
                logger.debug(
                    "Click at (%d, %d) is not within any Revolution Idle or Discord window",
                    x,
                    y,
                )
            return False

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error in window detection: %s", e, exc_info=True)
            # If there's an error, disable window filtering and accept all clicks
            self.window_filtering_enabled = False
            return True


class KeyboardHandler:
    """Handles keyboard events during automation mode."""

    def __init__(self, on_stop_automation: Optional[Callable] = None) -> None:
        self.on_stop_automation = on_stop_automation
        self.stop_automation = False
        logger.debug("KeyboardHandler initialized")

    def reset_stop_flag(self) -> None:
        """Reset the stop flag before starting a new automation session."""
        self.stop_automation = False
        logger.debug("Stop flag reset")

    def on_press(self, key: Any) -> None:
        """
        Callback function executed when a key is pressed.
        Checks for the stop key to halt automation.
        """
        try:
            # Convert key to string representation for comparison
            key_str = None

            # Handle special keys
            if hasattr(key, "char") and key.char:
                key_str = key.char
            elif hasattr(key, "name") and key.name:
                key_str = key.name
            elif hasattr(key, "_name_") and key._name_:  # pylint: disable=protected-access
                key_str = key._name_  # pylint: disable=protected-access
            elif isinstance(key, str):
                key_str = key

            # Check if this is the stop key
            if key_str and key_str.lower() == STOP_KEY.lower():
                logger.info("Stop key '%s' pressed, stopping automation", STOP_KEY)
                self.stop_automation = True
                if self.on_stop_automation:
                    self.on_stop_automation()

        except Exception:  # pylint: disable=broad-except
            logger.error("Error handling key press", exc_info=True)
