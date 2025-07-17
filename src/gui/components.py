"""
Reusable GUI components for Revolution Idle Sacrifice Automation.
"""

from typing import Any, Callable, Optional

import customtkinter as ctk  # type: ignore



class TabView:
    """Base class for tab content in the help window."""

    def __init__(self, parent: Any) -> None:
        """Initialize the tab view."""
        self.parent = parent
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True)


class SettingsSection:
    """A section of settings with a header and content."""

    def __init__(self, parent: Any, title: str, description: str = "") -> None:
        """Initialize a settings section."""
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


class ControlButton(ctk.CTkButton):
    """A button with standard styling for controls."""

    def __init__(
        self,
        parent: Any,
        text: str,
        command: Callable[[], None],
        width: int = 150,
        height: int = 40,
        **kwargs: Any,
    ) -> None:
        """Initialize a control button."""
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            **kwargs,
        )


class StatusDisplay:
    """A status display with a label and optional progress bar."""

    def __init__(self, parent: Any) -> None:
        """Initialize a status display."""
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

    def update_status(self, message: str) -> None:
        """Update the status message."""
        self.status_label.configure(text=message)

    def add_progress_bar(self) -> None:
        """Add a progress bar to the status display."""
        self.progress_bar = ctk.CTkProgressBar(self.frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)

    def update_progress(self, value: float) -> None:
        """Update the progress bar value (0.0 to 1.0)."""
        if self.progress_bar:
            self.progress_bar.set(value)
