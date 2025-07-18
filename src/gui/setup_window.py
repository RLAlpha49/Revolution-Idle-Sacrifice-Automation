"""
Setup window implementation for Revolution Idle Sacrifice Automation.
"""

import logging
from typing import Any, Callable, Optional

import customtkinter as ctk  # type: ignore

# Set up module logger
logger = logging.getLogger(__name__)


class SetupInstructionsWindow:
    """Instructions window for setup mode."""

    def __init__(
        self,
        parent: Any,
        cancel_callback: Callable[[], None],
        disable_window_detection_callback: Callable[[], None],
    ) -> None:
        """Initialize the setup instructions window."""
        logger.debug("Initializing setup instructions window")
        self.parent = parent
        self.cancel_callback = cancel_callback
        self.disable_window_detection_callback = disable_window_detection_callback

        self.window: Optional[ctk.CTkToplevel] = None
        self.instructions_label: Optional[ctk.CTkLabel] = None
        self.disable_detection_button: Optional[ctk.CTkButton] = None
        self.window_detection_disabled = False

        self._create_window()

    def _create_window(self) -> None:
        """Create the setup instructions window."""
        try:
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Setup Instructions")
            self.window.geometry("600x400")
            self.window.minsize(500, 300)

            # Make window independent
            self._make_independent()

            # Instructions frame
            instructions_frame = ctk.CTkFrame(self.window)
            instructions_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Title
            title_label = ctk.CTkLabel(
                instructions_frame,
                text="Setup Mode",
                font=ctk.CTkFont(size=18, weight="bold"),
            )
            title_label.pack(pady=(20, 10))

            # Instructions label
            self.instructions_label = ctk.CTkLabel(
                instructions_frame,
                text="Follow the instructions to configure the automation...",
                font=ctk.CTkFont(size=14),
                wraplength=500,
                justify="center",
            )
            self.instructions_label.pack(
                pady=(0, 20), padx=20, fill="both", expand=True
            )

            # Buttons frame
            buttons_frame = ctk.CTkFrame(instructions_frame, fg_color="transparent")
            buttons_frame.pack(fill="x", pady=(0, 10))

            # Disable window detection button
            self.disable_detection_button = ctk.CTkButton(
                buttons_frame,
                text="Disable Window Detection",
                command=self._on_disable_detection,
            )
            self.disable_detection_button.pack(side="left", padx=20, pady=10)

            # Cancel button
            cancel_button = ctk.CTkButton(
                buttons_frame,
                text="Cancel Setup",
                command=self._on_cancel,
                fg_color="red",
            )
            cancel_button.pack(side="right", padx=20, pady=10)

            logger.debug("Setup instructions window created successfully")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error creating setup instructions window", exc_info=True)
            print("Error creating setup window. Check the logs for details.")
            # Try to create a minimal window if the full one fails
            self._create_minimal_window()

    def _create_minimal_window(self) -> None:
        """Create a minimal window if the full one fails."""
        try:
            logger.debug("Creating minimal setup window")
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("Setup Instructions")
            self.window.geometry("400x200")

            # Simple label
            self.instructions_label = ctk.CTkLabel(
                self.window,
                text="Follow the instructions to configure the automation...",
                wraplength=350,
            )
            self.instructions_label.pack(pady=20, padx=20, expand=True)

            # Cancel button
            cancel_button = ctk.CTkButton(
                self.window,
                text="Cancel Setup",
                command=self._on_cancel,
                fg_color="red",
            )
            cancel_button.pack(pady=10)

            # Make the window appear in the taskbar
            self.window.transient(self.parent)
            self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)
        except Exception:  # pylint: disable=broad-except
            logger.error("Failed to create even minimal setup window", exc_info=True)

    def _make_independent(self) -> None:
        """Make the window independent from the parent."""
        if self.window:
            try:
                # Make the window stay on top
                self.window.attributes("-topmost", True)

                # Make the window appear in the taskbar
                self.window.transient(self.parent)

                # Prevent closing the window with the X button
                self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

                # Center the window on screen
                self.window.update_idletasks()
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                x = (self.window.winfo_screenwidth() // 2) - (width // 2)
                y = (self.window.winfo_screenheight() // 2) - (height // 2)
                self.window.geometry(f"{width}x{height}+{x}+{y}")

                logger.debug("Setup window positioned and configured")
            except Exception:  # pylint: disable=broad-except
                logger.error("Error making window independent", exc_info=True)

    def update_instructions(self, message: str) -> None:
        """Update the instructions text."""
        try:
            if self.instructions_label:
                self.instructions_label.configure(text=message)
                logger.debug("Updated setup instructions")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error updating instructions", exc_info=True)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        logger.info("Setup cancelled by user from setup window")
        if self.cancel_callback:
            self.cancel_callback()
        self.close()

    def _on_disable_detection(self) -> None:
        """Handle disable window detection button click."""
        logger.info("Window detection disabled by user")
        if self.disable_window_detection_callback:
            self.disable_window_detection_callback()

        self.window_detection_disabled = True
        try:
            if self.disable_detection_button:
                self.disable_detection_button.configure(
                    text="Window Detection Disabled",
                    state="disabled",
                    fg_color="gray",
                )
                logger.debug("Disabled window detection button updated")
        except Exception:  # pylint: disable=broad-except
            logger.error("Error updating disable detection button", exc_info=True)

    def close(self) -> None:
        """Close the setup instructions window."""
        logger.debug("Closing setup instructions window")
        if self.window:
            try:
                self.window.destroy()
                self.window = None
                logger.debug("Setup window destroyed")
            except Exception:  # pylint: disable=broad-except
                logger.error("Error closing setup window", exc_info=True)
                # Set to None anyway to avoid further errors
                self.window = None
