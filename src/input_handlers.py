"""
Input handlers for mouse and keyboard events.

This module handles mouse clicks during setup mode and keyboard presses
during automation mode for the Revolution Idle automation script.
"""

from typing import Callable, Optional
import pynput.mouse
import pynput.keyboard
from config.settings import STOP_KEY, MAX_ZODIAC_SLOTS
from utils.color_utils import get_pixel_color
from utils.display_utils import show_message


class SetupState:
    """Manages the state during setup mode."""

    def __init__(self):
        self.current_step = "zodiac_slots"  # "zodiac_slots", "sacrifice_box", "sacrifice_button", "complete"
        self.zodiac_slot_count = 0
        self.click_coords = {}
        self.target_rgbs = {}

    def reset(self):
        """Reset setup state for a new setup session."""
        self.current_step = "zodiac_slots"
        self.zodiac_slot_count = 0
        self.click_coords = {}
        self.target_rgbs = {}


class MouseHandler:
    """Handles mouse click events during setup mode."""

    def __init__(
        self, setup_state: SetupState, on_setup_complete: Optional[Callable] = None
    ):
        self.setup_state = setup_state
        self.on_setup_complete = on_setup_complete
        self.current_mode = None

    def set_mode(self, mode: str):
        """Set the current operation mode."""
        self.current_mode = mode

    def on_click(self, x: int, y: int, button: pynput.mouse.Button, pressed: bool):
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
                f"Click detected at: X={x}, Y={y}. In automation mode, clicks are performed by the script, not used for setup.",
                level="debug",
            )

    def _handle_setup_click(self, x: int, y: int, button: pynput.mouse.Button):
        """Handle mouse clicks during setup mode."""
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
                show_message(
                    "Right-click detected. In setup mode, right-click is only used to finish adding zodiac slots.",
                    level="info",
                )

    def _handle_zodiac_slot_click(self, x: int, y: int):
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

        show_message(
            f"Zodiac Slot {self.setup_state.zodiac_slot_count} captured: ({x}, {y}) with color {slot_color}."
        )

        if MAX_ZODIAC_SLOTS == -1:
            # Unlimited slots - show option to continue or finish
            show_message(
                f"Left-click to add Zodiac Slot {self.setup_state.zodiac_slot_count + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
            )
        elif self.setup_state.zodiac_slot_count < MAX_ZODIAC_SLOTS:
            # Limited slots - show current count and option to continue
            show_message(
                f"Left-click to add Zodiac Slot {self.setup_state.zodiac_slot_count + 1} (or right-click to finish adding zodiac slots and proceed to Sacrifice Drag Box)."
            )
        else:
            # Reached maximum limit
            show_message(
                f"Maximum zodiac slots ({MAX_ZODIAC_SLOTS}) reached. Now left-click to set the Sacrifice Drag Box."
            )
            self.setup_state.current_step = "sacrifice_box"

    def _handle_sacrifice_box_click(self, x: int, y: int):
        """Handle clicks for sacrifice box setup."""
        self.setup_state.click_coords["sacrifice_box"] = (x, y)
        show_message(
            f"Sacrifice Drag Box captured: ({x}, {y}). Now left-click to set the Sacrifice Button."
        )
        self.setup_state.current_step = "sacrifice_button"

    def _handle_sacrifice_button_click(self, x: int, y: int):
        """Handle clicks for sacrifice button setup."""
        # Hardcoded RGB for the Sacrifice Button (for reliability)
        sacrifice_button_rgb = (219, 124, 0)

        self.setup_state.click_coords["sacrifice_button"] = (x, y)
        # Hardcoded RGB for the Sacrifice Button
        self.setup_state.target_rgbs["sacrifice_button"] = sacrifice_button_rgb
        show_message(
            f"Sacrifice Button captured: ({x}, {y}). Its target color is hardcoded to {sacrifice_button_rgb}."
        )
        show_message(
            f"Setup complete! Configured {len(self.setup_state.click_coords['zodiac_slots'])} zodiac slots. Saving Revolution Idle configuration."
        )
        self.setup_state.current_step = "complete"

        if self.on_setup_complete:
            self.on_setup_complete()

    def _finish_zodiac_slots(self):
        """Finish adding zodiac slots and proceed to sacrifice box."""
        show_message(
            f"Finished adding zodiac slots. {self.setup_state.zodiac_slot_count} zodiac slots configured. Now left-click to set the Sacrifice Drag Box."
        )
        self.setup_state.current_step = "sacrifice_box"


class KeyboardHandler:
    """Handles keyboard events during automation mode."""

    def __init__(self, on_stop_automation: Optional[Callable] = None):
        self.on_stop_automation = on_stop_automation
        self.stop_automation = False

    def reset_stop_flag(self):
        """Reset the stop automation flag."""
        self.stop_automation = False

    def on_press(self, key):
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
