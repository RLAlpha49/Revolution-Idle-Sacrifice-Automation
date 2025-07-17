"""
Utility functions for displaying messages and performance tracking.

This module provides functions for console output with verbosity control
and performance monitoring for the automation script.
"""

import time

from config.settings import MESSAGE_LEVEL


def show_message(message: str, level: str = "info") -> None:
    """
    A simple console-based message display function with verbosity control.
    Messages are only printed if their level matches or is lower than MESSAGE_LEVEL.

    Args:
        message: The message to display
        level: Message level ('info' or 'debug')
    """
    if MESSAGE_LEVEL == "debug":
        # If debug mode, show all messages with their level prefix
        if level == "debug":
            print(f"\n--- DEBUG MESSAGE ---\n{message}\n----------------------\n")
        elif level == "info":
            print(f"\n--- INFO MESSAGE ---\n{message}\n----------------------\n")
    elif MESSAGE_LEVEL == "info" and level == "info":
        # If info mode, only show info messages without a prefix
        print(f"\n{message}\n")


class PerformanceTracker:
    """Tracks performance statistics for the automation script."""

    def __init__(self) -> None:
        self.sacrifice_count: int = 0
        self.automation_start_time: float = 0
        self.last_sacrifice_time: float = 0

    def start_tracking(self) -> None:
        """Start tracking automation performance."""
        self.sacrifice_count = 0
        self.automation_start_time = time.time()

    def increment_sacrifice_count(self) -> None:
        """Increment sacrifice counter and update last sacrifice time."""
        self.sacrifice_count += 1
        self.last_sacrifice_time = time.time()

    def update_sacrifice_counter_display(self) -> None:
        """
        Updates the sacrifice counter display on the same line without creating new lines.
        """
        current_time = time.time()
        if self.automation_start_time > 0:
            elapsed_time = current_time - self.automation_start_time
            if self.sacrifice_count > 0:
                avg_time_per_sacrifice = elapsed_time / self.sacrifice_count
                sacrifices_per_minute = (
                    60 / avg_time_per_sacrifice if avg_time_per_sacrifice > 0 else 0
                )
                print(
                    f"\rSacrifices: {self.sacrifice_count} | "
                    f"Rate: {sacrifices_per_minute:.1f}/min | "
                    f"Time: {elapsed_time:.1f}s",
                    end="",
                    flush=True,
                )
            else:
                print(
                    f"\rSacrifices: {self.sacrifice_count} | Time: {elapsed_time:.1f}s",
                    end="",
                    flush=True,
                )
        else:
            print(
                f"\rTotal Zodiac Sacrifices: {self.sacrifice_count}", end="", flush=True
            )

    def get_total_automation_time(self) -> float:
        """Get total automation time elapsed."""
        if self.automation_start_time > 0:
            return time.time() - self.automation_start_time
        return 0.0
