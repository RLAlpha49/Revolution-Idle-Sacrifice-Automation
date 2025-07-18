"""
Utility functions for displaying messages and performance tracking.

This module provides functions for console output with verbosity control
and performance monitoring for the automation script.
"""

import logging
import time

from config.settings import MESSAGE_LEVEL

# Set up module logger
logger = logging.getLogger(__name__)


def show_message(message: str, level: str = "info") -> None:
    """
    Display a message with verbosity control using the logging module.
    Messages are only displayed if their level matches or is lower than MESSAGE_LEVEL.

    Args:
        message: The message to display
        level: Message level ('info' or 'debug')
    """
    if level == "debug":
        logger.debug(message)
        if MESSAGE_LEVEL == "debug":
            print(f"\n--- DEBUG MESSAGE ---\n{message}\n----------------------\n")
    elif level == "info":
        logger.info(message)
        if MESSAGE_LEVEL in ["info", "debug"]:
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
        logger.info("Performance tracking started")

    def increment_sacrifice_count(self) -> None:
        """Increment sacrifice counter and update last sacrifice time."""
        self.sacrifice_count += 1
        self.last_sacrifice_time = time.time()
        if self.sacrifice_count % 10 == 0:  # Log every 10 sacrifices to avoid spam
            logger.debug("Sacrifice count: %d", self.sacrifice_count)

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
                # Log performance stats periodically
                if self.sacrifice_count % 50 == 0:
                    logger.info(
                        "Performance stats - Sacrifices: %d, Rate: %.1f/min, Time: %.1f s",
                        self.sacrifice_count,
                        sacrifices_per_minute,
                        elapsed_time,
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
            total_time = time.time() - self.automation_start_time
            logger.info("Total automation time: %.2f seconds", total_time)
            return total_time
        return 0.0
