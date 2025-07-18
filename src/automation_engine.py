"""
Automation engine for Revolution Idle Sacrifice Automation.

This module contains the core automation logic that performs the repetitive
mouse actions for zodiac sacrificing in Revolution Idle.
"""

import time
from typing import Callable, Dict, List, Optional, Tuple

import pynput.mouse

from config.settings import (
    COLOR_TOLERANCE,
    DEBUG_COLOR_MATCHING,
    DELAY_AFTER_CLICK,
    DELAY_AFTER_DRAG,
    DELAY_AFTER_PRESS,
    DELAY_BEFORE_CHECK,
    DELAY_DRAG_DURATION,
)
from utils.color_utils import colors_match, get_multiple_pixel_colors, get_pixel_color
from utils.display_utils import PerformanceTracker, show_message


class AutomationEngine:
    """Core automation engine for Revolution Idle zodiac sacrificing."""

    def __init__(self) -> None:
        self.mouse = pynput.mouse.Controller()
        self.performance_tracker = PerformanceTracker()
        self.is_running = False

    def run_automation(
        self,
        click_coords: Dict,
        target_rgbs: Dict,
        stop_callback: Optional[Callable[[], bool]] = None,
    ) -> None:
        """
        Main automation loop for Revolution Idle zodiac sacrificing.

        Args:
            click_coords: Dictionary containing coordinates for zodiac slots,
                sacrifice box, and button
            target_rgbs: Dictionary containing target RGB colors for matching
            stop_callback: Function to check if automation should stop
        """
        # Validate configuration
        if not self._validate_config(click_coords, target_rgbs):
            return

        # Initialize automation
        self.is_running = True
        self.performance_tracker.start_tracking()
        zodiac_count = len(click_coords["zodiac_slots"])

        show_message(
            f"Revolution Idle Sacrifice Automation started with {zodiac_count} "
            "zodiac slot(s). Press 'q' to stop.",
            level="info",
        )

        # Display initial sacrifice counter
        self.performance_tracker.update_sacrifice_counter_display()

        # Main automation loop
        while self.is_running and (stop_callback is None or not stop_callback()):
            time.sleep(DELAY_BEFORE_CHECK)

            try:
                # Check all zodiac slots and sacrifice button colors in one screenshot
                coordinates_to_check = click_coords["zodiac_slots"] + [
                    click_coords["sacrifice_button"]
                ]
                current_colors = get_multiple_pixel_colors(coordinates_to_check)

                if None in current_colors:
                    continue  # Skip this iteration if color detection failed

                # Separate zodiac slot colors from sacrifice button color
                zodiac_colors = current_colors[:-1]

                # Skip if any colors are None
                if any(color is None for color in zodiac_colors):
                    continue

                # Check each zodiac slot for a match
                if self._check_zodiac_slots(
                    zodiac_colors,
                    target_rgbs["zodiac_slots"],
                    click_coords,
                    target_rgbs,
                ):
                    # If we performed an action, continue to next iteration
                    continue
            except (OSError, IndexError, ValueError) as e:
                show_message(f"Error during color detection: {e}", level="debug")
                continue

        # Calculate and display total automation time
        total_time = self.performance_tracker.get_total_automation_time()
        show_message(
            f"Revolution Idle Sacrifice Automation completed. "
            f"Total time: {total_time:.2f} seconds.",
            level="info",
        )
        # Add a newline after the counter display when automation ends
        print()
        self.is_running = False

    def stop(self) -> None:
        """Stop the automation engine."""
        self.is_running = False

    def _validate_config(self, click_coords: Dict, target_rgbs: Dict) -> bool:
        """Validate that all necessary configuration data is present."""
        required_keys = ["zodiac_slots", "sacrifice_box", "sacrifice_button"]
        if not all(k in click_coords for k in required_keys) or not all(
            k in target_rgbs for k in ["zodiac_slots", "sacrifice_button"]
        ):
            show_message(
                "Revolution Idle Sacrifice Automation cannot start: Missing "
                "configuration data. Please run in 'setup' mode first.",
                level="info",
            )
            return False

        # Verify we have at least one zodiac slot configured
        if not click_coords["zodiac_slots"] or not target_rgbs["zodiac_slots"]:
            show_message(
                "Revolution Idle Sacrifice Automation cannot start: No zodiac "
                "slots configured. Please run in 'setup' mode first.",
                level="info",
            )
            return False

        return True

    def _check_zodiac_slots(
        self,
        zodiac_colors: List,
        target_colors: List,
        click_coords: Dict,
        target_rgbs: Dict,
    ) -> bool:
        """
        Check each zodiac slot for color matches and perform actions if needed.

        Returns:
            bool: True if an action was performed, False otherwise
        """
        for slot_index, (current_color, target_color) in enumerate(
            zip(zodiac_colors, target_colors)
        ):
            # Show color comparison for debugging
            if DEBUG_COLOR_MATCHING:
                self._show_color_debug(slot_index, current_color, target_color)

            if colors_match(current_color, target_color):
                if self._perform_sacrifice_action(
                    slot_index, click_coords, target_rgbs
                ):
                    return True  # Action performed, restart loop

        # No zodiac slot matched
        show_message(
            "No zodiac slots have matching colors. Waiting for a match...",
            level="debug",
        )
        return False

    def _show_color_debug(
        self,
        slot_index: int,
        current_color: Tuple[int, int, int],
        target_color: Tuple[int, int, int],
    ) -> None:
        """Show detailed color matching debug information."""
        color_diff = [abs(c1 - c2) for c1, c2 in zip(current_color, target_color)]
        max_diff = max(color_diff)
        show_message(
            f"Slot {slot_index + 1}: Current={current_color}, Target={target_color}, "
            f"Diff={color_diff}, MaxDiff={max_diff}, Tolerance={COLOR_TOLERANCE}, "
            f"Match={colors_match(current_color, target_color)}",
            level="debug",
        )

    def _perform_sacrifice_action(
        self, slot_index: int, click_coords: Dict, target_rgbs: Dict
    ) -> bool:
        """
        Perform the drag and sacrifice action for a matching zodiac slot.

        Returns:
            bool: True if sacrifice was completed, False otherwise
        """
        slot_coords = click_coords["zodiac_slots"][slot_index]
        show_message(
            f"✓ Zodiac Slot {slot_index + 1} matched! Performing drag...",
            level="debug",
        )

        # Perform drag action
        self._drag_zodiac_to_sacrifice_box(slot_coords, click_coords["sacrifice_box"])

        time.sleep(DELAY_AFTER_DRAG)

        # Check sacrifice button color after drag
        current_sacrifice_color = get_pixel_color(
            click_coords["sacrifice_button"][0],
            click_coords["sacrifice_button"][1],
        )

        if colors_match(current_sacrifice_color, target_rgbs["sacrifice_button"]):
            self._click_sacrifice_button(click_coords["sacrifice_button"])
            self.performance_tracker.increment_sacrifice_count()
            self.performance_tracker.update_sacrifice_counter_display()

            show_message(
                f"Zodiac from slot {slot_index + 1} sacrificed successfully! "
                f"Total sacrifices: {self.performance_tracker.sacrifice_count}",
                level="debug",
            )
            return True

        show_message(
            f"Color at Sacrifice Button ({current_sacrifice_color}) does NOT match "
            f"target ({target_rgbs['sacrifice_button']}). "
            "Continuing to check other zodiac slots.",
            level="debug",
        )
        return False

    def _drag_zodiac_to_sacrifice_box(
        self, from_coords: Tuple[int, int], to_coords: Tuple[int, int]
    ) -> None:
        """Perform drag action from zodiac slot to sacrifice box."""
        self.mouse.position = from_coords
        self.mouse.press(pynput.mouse.Button.left)
        time.sleep(DELAY_AFTER_PRESS)
        self.mouse.position = to_coords
        time.sleep(DELAY_DRAG_DURATION)
        self.mouse.release(pynput.mouse.Button.left)

        show_message(
            f"Dragged zodiac from {from_coords} to sacrifice box {to_coords}.",
            level="debug",
        )

    def _click_sacrifice_button(self, button_coords: Tuple[int, int]) -> None:
        """Click the sacrifice button."""
        self.mouse.position = button_coords
        self.mouse.click(pynput.mouse.Button.left)
        time.sleep(DELAY_AFTER_CLICK)

        show_message(
            f"Clicked sacrifice button at {button_coords}.",
            level="debug",
        )
