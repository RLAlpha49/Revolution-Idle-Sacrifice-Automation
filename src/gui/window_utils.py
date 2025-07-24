"""
Window positioning utilities for multi-monitor support.

This module provides utilities for positioning windows relative to a parent window
or main application window, with proper multi-monitor support.
"""

import logging
from typing import Optional, Tuple, Union, Dict
import customtkinter as ctk
import tkinter as tk

logger = logging.getLogger(__name__)


class WindowPositioner:
    """Utility class for positioning windows with multi-monitor support."""

    @staticmethod
    def get_monitor_info(window: Union[ctk.CTk, ctk.CTkToplevel]) -> Dict[str, int]:
        """Get information about the monitor containing the window.

        Args:
            window: Window to get monitor info for

        Returns:
            dict: Dictionary containing monitor bounds and window position
        """
        try:
            window.update_idletasks()

            # Get window position
            win_x = window.winfo_x()
            win_y = window.winfo_y()
            win_width = window.winfo_width()
            win_height = window.winfo_height()

            # Get all monitor information using tkinter's built-in methods
            # This works better for multi-monitor setups than winfo_screenwidth/height
            root = window if isinstance(window, ctk.CTk) else window.master
            if root is None:
                root = tk._default_root or window

            # Try to get monitor bounds using tkinter geometry methods
            try:
                # Get the geometry of the root window to determine monitor bounds
                geometry = root.wm_maxsize()
                max_width, max_height = geometry

                # For multi-monitor, we need to detect which monitor the window is on
                # Use the window's current position to determine monitor bounds

                # Get virtual screen dimensions (all monitors combined)
                virtual_width = root.winfo_vrootwidth()
                virtual_height = root.winfo_vrootheight()
                virtual_x = root.winfo_vrootx()
                virtual_y = root.winfo_vrooty()

                # Calculate monitor bounds based on window position
                # This is a simplified approach - for more complex setups,
                # we'd need platform-specific APIs

                # Estimate monitor bounds by finding which "screen" the window center is in
                window_center_x = win_x + win_width // 2
                window_center_y = win_y + win_height // 2

                # Try to determine monitor bounds
                # If window is in negative coordinates, it's likely on a secondary monitor
                if window_center_x < 0:
                    # Likely on a monitor to the left of primary
                    monitor_x = virtual_x
                    monitor_width = abs(virtual_x)
                elif window_center_x > max_width:
                    # Likely on a monitor to the right of primary
                    monitor_x = max_width
                    monitor_width = virtual_width - max_width
                else:
                    # On primary monitor
                    monitor_x = 0
                    monitor_width = max_width

                if window_center_y < 0:
                    # Likely on a monitor above primary
                    monitor_y = virtual_y
                    monitor_height = abs(virtual_y)
                elif window_center_y > max_height:
                    # Likely on a monitor below primary
                    monitor_y = max_height
                    monitor_height = virtual_height - max_height
                else:
                    # On primary monitor
                    monitor_y = 0
                    monitor_height = max_height

                return {
                    "window_x": win_x,
                    "window_y": win_y,
                    "window_width": win_width,
                    "window_height": win_height,
                    "monitor_x": monitor_x,
                    "monitor_y": monitor_y,
                    "monitor_width": monitor_width,
                    "monitor_height": monitor_height,
                    "virtual_x": virtual_x,
                    "virtual_y": virtual_y,
                    "virtual_width": virtual_width,
                    "virtual_height": virtual_height,
                }

            except (AttributeError, ValueError, TypeError):
                # Fallback to basic screen dimensions
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()

                return {
                    "window_x": win_x,
                    "window_y": win_y,
                    "window_width": win_width,
                    "window_height": win_height,
                    "monitor_x": 0,
                    "monitor_y": 0,
                    "monitor_width": screen_width,
                    "monitor_height": screen_height,
                    "virtual_x": 0,
                    "virtual_y": 0,
                    "virtual_width": screen_width,
                    "virtual_height": screen_height,
                }

        except (AttributeError, ValueError, TypeError) as e:
            logger.warning("Error getting monitor info: %s", e)
            # Ultimate fallback
            return {
                "window_x": 100,
                "window_y": 100,
                "window_width": 800,
                "window_height": 600,
                "monitor_x": 0,
                "monitor_y": 0,
                "monitor_width": 1920,
                "monitor_height": 1080,
                "virtual_x": 0,
                "virtual_y": 0,
                "virtual_width": 1920,
                "virtual_height": 1080,
            }

    @staticmethod
    def get_parent_window_info(parent: Union[ctk.CTk, ctk.CTkToplevel]) -> dict:
        """Get information about the parent window and its monitor.

        Args:
            parent: Parent window (main window or toplevel)

        Returns:
            dict: Dictionary containing parent window position and monitor info
        """
        monitor_info = WindowPositioner.get_monitor_info(parent)

        # Convert to the expected format for backward compatibility
        return {
            "x": monitor_info["window_x"],
            "y": monitor_info["window_y"],
            "width": monitor_info["window_width"],
            "height": monitor_info["window_height"],
            "screen_width": monitor_info["monitor_width"],
            "screen_height": monitor_info["monitor_height"],
            "monitor_x": monitor_info["monitor_x"],
            "monitor_y": monitor_info["monitor_y"],
            "virtual_x": monitor_info["virtual_x"],
            "virtual_y": monitor_info["virtual_y"],
            "virtual_width": monitor_info["virtual_width"],
            "virtual_height": monitor_info["virtual_height"],
        }

    @staticmethod
    def calculate_relative_position(
        window_width: int,
        window_height: int,
        parent_info: dict,
        offset_x: int = 50,
        offset_y: int = 50,
        position: str = "center_offset",
    ) -> Tuple[int, int]:
        """Calculate window position relative to parent.

        Args:
            window_width: Width of the window to position
            window_height: Height of the window to position
            parent_info: Parent window information from get_parent_window_info
            offset_x: Horizontal offset from parent (default: 50)
            offset_y: Vertical offset from parent (default: 50)
            position: Position strategy - "center_offset", "center", "top_right", "cascade"

        Returns:
            Tuple[int, int]: (x, y) coordinates for the window
        """
        parent_x = parent_info["x"]
        parent_y = parent_info["y"]
        parent_width = parent_info["width"]
        parent_height = parent_info["height"]
        screen_width = parent_info["screen_width"]
        screen_height = parent_info["screen_height"]

        # Get monitor bounds for proper multi-monitor support
        monitor_x = parent_info.get("monitor_x", 0)
        monitor_y = parent_info.get("monitor_y", 0)

        if position == "center":
            # Center on parent window
            x = parent_x + (parent_width - window_width) // 2
            y = parent_y + (parent_height - window_height) // 2
        elif position == "center_offset":
            # Center on parent with slight offset
            x = parent_x + (parent_width - window_width) // 2 + offset_x
            y = parent_y + (parent_height - window_height) // 2 + offset_y
        elif position == "top_right":
            # Position to the right of parent window
            x = parent_x + parent_width + offset_x
            y = parent_y + offset_y
        elif position == "cascade":
            # Cascade style positioning (offset from parent)
            x = parent_x + offset_x
            y = parent_y + offset_y
        else:
            # Default to center_offset
            x = parent_x + (parent_width - window_width) // 2 + offset_x
            y = parent_y + (parent_height - window_height) // 2 + offset_y

        # Ensure window stays within monitor bounds (not just screen bounds)
        monitor_right = monitor_x + screen_width
        monitor_bottom = monitor_y + screen_height

        x = max(monitor_x, min(x, monitor_right - window_width))
        y = max(monitor_y, min(y, monitor_bottom - window_height))

        # If window would be too far off monitor, fall back to monitor center
        if x < monitor_x - window_width // 2 or y < monitor_y - window_height // 2:
            x = monitor_x + (screen_width - window_width) // 2
            y = monitor_y + (screen_height - window_height) // 2

        logger.debug(
            "Calculated position for %dx%d window: (%d, %d) using strategy '%s'",
            window_width,
            window_height,
            x,
            y,
            position,
        )

        return x, y

    @staticmethod
    def position_window_relative(
        window: ctk.CTkToplevel,
        parent: Optional[Union[ctk.CTk, ctk.CTkToplevel]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        offset_x: int = 50,
        offset_y: int = 50,
        position: str = "center_offset",
    ) -> None:
        """Position a window relative to its parent with multi-monitor support.

        Args:
            window: Window to position
            parent: Parent window (if None, will try to get from window.master)
            width: Desired window width (if None, uses current width)
            height: Desired window height (if None, uses current height)
            offset_x: Horizontal offset from parent
            offset_y: Vertical offset from parent
            position: Position strategy - "center_offset", "center", "top_right", "cascade"
        """
        try:
            # Get parent window
            if parent is None:
                parent = getattr(window, "master", None) or getattr(
                    window, "_parent", None
                )

            if parent is None:
                logger.warning("No parent window found, centering on screen")
                WindowPositioner.center_on_screen(window, width, height)
                return

            # Update window to get current dimensions
            window.update_idletasks()

            # Get window dimensions
            if width is None:
                width = window.winfo_width()
            if height is None:
                height = window.winfo_height()

            # Get parent window info
            parent_info = WindowPositioner.get_parent_window_info(parent)

            # Calculate position
            x, y = WindowPositioner.calculate_relative_position(
                width, height, parent_info, offset_x, offset_y, position
            )

            # Set window geometry
            window.geometry(f"{width}x{height}+{x}+{y}")

            logger.debug("Positioned window at (%d, %d) relative to parent", x, y)

        except (AttributeError, ValueError, TypeError) as e:
            logger.error(
                "Error positioning window relative to parent: %s", e, exc_info=True
            )
            # Fallback to screen center
            WindowPositioner.center_on_screen(window, width, height)

    @staticmethod
    def center_on_screen(
        window: Union[ctk.CTk, ctk.CTkToplevel],
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> None:
        """Center a window on the screen (monitor-aware for multi-monitor setups).

        Args:
            window: Window to center
            width: Desired window width (if None, uses current width)
            height: Desired window height (if None, uses current height)
        """
        try:
            window.update_idletasks()

            # Get window dimensions
            if width is None:
                width = window.winfo_width()
            if height is None:
                height = window.winfo_height()

            # Get monitor information for proper multi-monitor support
            monitor_info = WindowPositioner.get_monitor_info(window)

            monitor_x = monitor_info["monitor_x"]
            monitor_y = monitor_info["monitor_y"]
            monitor_width = monitor_info["monitor_width"]
            monitor_height = monitor_info["monitor_height"]

            # Calculate center position on the current monitor
            x = monitor_x + (monitor_width - width) // 2
            y = monitor_y + (monitor_height - height) // 2

            # Set window geometry
            window.geometry(f"{width}x{height}+{x}+{y}")

            logger.debug(
                "Centered window on monitor at (%d, %d) [monitor bounds: %d,%d %dx%d]",
                x,
                y,
                monitor_x,
                monitor_y,
                monitor_width,
                monitor_height,
            )

        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error centering window on screen: %s", e, exc_info=True)
            # Ultimate fallback
            try:
                if width and height:
                    window.geometry(f"{width}x{height}")
            except (AttributeError, ValueError, TypeError):
                pass

    @staticmethod
    def ensure_window_visible(window: Union[ctk.CTk, ctk.CTkToplevel]) -> None:
        """Ensure a window is visible on screen (move if off-screen).

        Args:
            window: Window to check and adjust
        """
        try:
            window.update_idletasks()

            x = window.winfo_x()
            y = window.winfo_y()
            width = window.winfo_width()
            height = window.winfo_height()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()

            # Check if window is off-screen
            needs_adjustment = False
            new_x, new_y = x, y

            if x < 0:
                new_x = 0
                needs_adjustment = True
            elif x + width > screen_width:
                new_x = screen_width - width
                needs_adjustment = True

            if y < 0:
                new_y = 0
                needs_adjustment = True
            elif y + height > screen_height:
                new_y = screen_height - height
                needs_adjustment = True

            if needs_adjustment:
                window.geometry(f"{width}x{height}+{new_x}+{new_y}")
                logger.debug(
                    "Adjusted window position from (%d, %d) to (%d, %d)",
                    x,
                    y,
                    new_x,
                    new_y,
                )

        except (AttributeError, ValueError, TypeError) as e:
            logger.error("Error ensuring window visibility: %s", e, exc_info=True)
