"""
Reusable GUI components for Revolution Idle Sacrifice Automation.
"""

import logging
from typing import Any, Callable, Optional

import customtkinter as ctk  # type: ignore

# Set up module logger
logger = logging.getLogger(__name__)


class TabView:
    """Base class for tab content in the help window."""

    def __init__(self, parent: Any) -> None:
        """Initialize the tab view."""
        try:
            self.parent = parent
            self.frame = ctk.CTkFrame(parent)
            self.frame.pack(fill="both", expand=True)
            logger.debug("TabView initialized")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error initializing TabView", exc_info=True)


class SettingsSection:
    """A section of settings with a header and content."""

    def __init__(self, parent: Any, title: str, description: str = "") -> None:
        """Initialize a settings section."""
        try:
            self.parent = parent
            self.frame = ctk.CTkFrame(parent)
            self.frame.pack(fill="x", expand=False, padx=10, pady=5)

            self.title = ctk.CTkLabel(
                self.frame,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            self.title.pack(anchor="w", padx=10, pady=(10, 0))

            if description:
                self.description = ctk.CTkLabel(
                    self.frame,
                    text=description,
                    font=ctk.CTkFont(size=12),
                    justify="left",
                    wraplength=550,
                )
                self.description.pack(anchor="w", padx=10, pady=(0, 5))

            self.content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
            self.content_frame.pack(fill="x", expand=False, padx=20, pady=10)

            logger.debug("SettingsSection initialized with title: %s", title)
        except Exception:  # pylint: disable=broad-except
            logger.error(
                "Error initializing SettingsSection '%s'", title, exc_info=True
            )


class ControlButton(ctk.CTkButton):  # pylint: disable=too-many-ancestors
    """A button with standard styling for controls."""

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        parent: Any,
        text: str,
        command: Callable[[], None],
        width: int = 150,
        height: int = 40,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a control button.

        Args:
            parent: The parent widget
            text: Button text
            command: Callback function
            width: Button width
            height: Button height
            **kwargs: Additional keyword arguments for CTkButton
        """
        try:
            super().__init__(
                parent,
                text=text,
                command=command,
                width=width,
                height=height,
                **kwargs,
            )
            logger.debug("ControlButton initialized with text: %s", text)
        except Exception:  # pylint: disable=broad-except
            logger.error("Error initializing ControlButton '%s'", text, exc_info=True)
            # Try to create a basic button as fallback
            try:
                super().__init__(parent, text=text, command=command)
            except Exception:  # pylint: disable=broad-except
                logger.critical("Failed to create even basic button for '%s'", text)


class StatusDisplay:
    """A status display with a label and optional progress bar."""

    def __init__(self, parent: Any) -> None:
        """Initialize a status display."""
        try:
            self.parent = parent
            self.frame = ctk.CTkFrame(parent)
            self.frame.pack(fill="x", expand=False, padx=10, pady=5)

            self.status_label = ctk.CTkLabel(
                self.frame,
                text="Ready",
                font=ctk.CTkFont(size=14),
            )
            self.status_label.pack(anchor="center", pady=10)

            self.progress_bar: Optional[ctk.CTkProgressBar] = None
            logger.debug("StatusDisplay initialized")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error initializing StatusDisplay", exc_info=True)

    def update_status(self, message: str) -> None:
        """Update the status message."""
        try:
            self.status_label.configure(text=message)
            logger.debug("Status updated: %s", message)
        except Exception:  # pylint: disable=broad-except
            logger.error("Error updating status to '%s'", message, exc_info=True)

    def add_progress_bar(self) -> None:
        """Add a progress bar to the status display."""
        try:
            self.progress_bar = ctk.CTkProgressBar(self.frame)
            self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
            self.progress_bar.set(0)
            logger.debug("Progress bar added to StatusDisplay")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error adding progress bar", exc_info=True)

    def update_progress(self, value: float) -> None:
        """Update the progress bar value (0.0 to 1.0)."""
        try:
            if self.progress_bar:
                self.progress_bar.set(value)
                logger.debug("Progress updated to %.2f", value)
        except Exception:  # pylint: disable=broad-except
            logger.error("Error updating progress to %f", value, exc_info=True)
