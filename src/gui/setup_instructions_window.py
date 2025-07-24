"""
Setup instructions window for Revolution Idle Sacrifice Automation.
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
        enable_debug_mode_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the setup instructions window."""
        logger.debug("Initializing setup instructions window")
        self.parent = parent
        self.cancel_callback = cancel_callback
        self.disable_window_detection_callback = disable_window_detection_callback
        self.enable_debug_mode_callback = enable_debug_mode_callback

        self.window: Optional[ctk.CTkToplevel] = None
        self.instructions_label: Optional[ctk.CTkLabel] = None
        self.debug_mode_button: Optional[ctk.CTkButton] = None
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

            # Main frame
            main_frame = ctk.CTkFrame(self.window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Title
            title_label = ctk.CTkLabel(
                main_frame,
                text="Revolution Idle Automation Setup",
                font=ctk.CTkFont(size=18, weight="bold"),
            )
            title_label.pack(pady=(10, 20))

            # Instructions
            self.instructions_label = ctk.CTkLabel(
                main_frame,
                text="Follow the on-screen instructions to set up automation.",
                wraplength=550,
                justify="left",
                font=ctk.CTkFont(size=12),
            )
            self.instructions_label.pack(pady=(0, 20), fill="both", expand=True)

            # Buttons frame
            button_frame = ctk.CTkFrame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))

            # Cancel button
            cancel_button = ctk.CTkButton(
                button_frame,
                text="Cancel Setup",
                command=self._on_cancel,
                fg_color="red",
                hover_color="dark red",
            )
            cancel_button.pack(side="left", padx=5)

            # Debug mode button (if callback provided)
            if self.enable_debug_mode_callback:
                self.debug_mode_button = ctk.CTkButton(
                    button_frame,
                    text="Enable Debug Mode",
                    command=self._on_enable_debug_mode,
                )
                self.debug_mode_button.pack(side="left", padx=5)

            # Disable window detection button
            self.disable_detection_button = ctk.CTkButton(
                button_frame,
                text="Disable Window Detection",
                command=self._on_disable_detection,
            )
            self.disable_detection_button.pack(side="right", padx=5)

            # Make window independent
            self._make_independent()

            logger.debug("Setup instructions window created successfully")

        except (AttributeError, ValueError, RuntimeError) as e:
            logger.error(
                "Error creating setup instructions window: %s", e, exc_info=True
            )
            # Try to create a minimal window as fallback
            self._create_minimal_window()

    def _create_minimal_window(self) -> None:
        """Create a minimal window if the full one fails."""
        try:
            if self.window:
                self.window.destroy()

            self.window = ctk.CTkToplevel()
            self.window.title("Setup Instructions")
            self.window.geometry("400x200")

            # Simple label
            label = ctk.CTkLabel(
                self.window,
                text="Setup in progress...\nCheck the console for instructions.",
                font=ctk.CTkFont(size=12),
            )
            label.pack(expand=True, pady=20)

            # Cancel button
            cancel_button = ctk.CTkButton(
                self.window,
                text="Cancel",
                command=self._on_cancel,
            )
            cancel_button.pack(pady=10)

            logger.debug("Created minimal setup instructions window")

        except (AttributeError, ValueError, RuntimeError) as e:
            logger.error(
                "Failed to create even minimal setup window: %s", e, exc_info=True
            )

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
            except (AttributeError, ValueError, RuntimeError) as e:
                logger.error("Error making window independent: %s", e, exc_info=True)

    def update_instructions(self, message: str) -> None:
        """Update the instructions text."""
        try:
            if self.instructions_label:
                self.instructions_label.configure(text=message)
                logger.debug("Updated setup instructions")
        except (AttributeError, ValueError) as e:
            logger.error("Error updating instructions: %s", e, exc_info=True)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        logger.info("Setup cancelled by user from setup window")
        if self.cancel_callback is not None:
            self.cancel_callback()
        self.close()

    def _on_enable_debug_mode(self) -> None:
        """Handle enable debug mode button click."""
        logger.info("Debug mode enabled by user")
        if self.enable_debug_mode_callback:
            self.enable_debug_mode_callback()

        try:
            if self.debug_mode_button:
                self.debug_mode_button.configure(
                    text="Debug Mode Enabled",
                    state="disabled",
                    fg_color="gray",
                )
                logger.debug("Debug mode button updated")
        except (AttributeError, ValueError) as e:
            logger.error("Error updating debug mode button: %s", e, exc_info=True)

    def _on_disable_detection(self) -> None:
        """Handle disable window detection button click."""
        logger.info("Window detection disabled by user")
        if self.disable_window_detection_callback is not None:
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
        except (AttributeError, ValueError) as e:
            logger.error(
                "Error updating disable detection button: %s", e, exc_info=True
            )

    def close(self) -> None:
        """Close the setup instructions window."""
        logger.debug("Closing setup instructions window")
        if self.window:
            try:
                self.window.destroy()
                self.window = None
                logger.debug("Setup window destroyed")
            except (AttributeError, RuntimeError) as e:
                logger.error("Error closing setup window: %s", e, exc_info=True)
                # Set to None anyway to avoid further errors
                self.window = None
