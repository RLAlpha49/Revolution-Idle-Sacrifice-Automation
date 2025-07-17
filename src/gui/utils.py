"""
Utility functions for the GUI components of Revolution Idle Sacrifice Automation.
"""

import time
import webbrowser
from typing import Any, Optional

import customtkinter as ctk  # type: ignore


def open_url(url: str) -> None:
    """Open a URL in the default web browser."""
    webbrowser.open(url)


def log_message(textbox: Optional[ctk.CTkTextbox], message: str) -> None:
    """Add a timestamped message to a textbox."""
    if textbox:
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        textbox.insert("end", formatted_message)
        textbox.see("end")


def create_scrollable_frame(parent: Any) -> tuple[ctk.CTkScrollableFrame, ctk.CTkFrame]:
    """Create a scrollable frame with an inner content frame."""
    scrollable_frame = ctk.CTkScrollableFrame(parent)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

    content_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    content_frame.pack(fill="both", expand=True)

    return scrollable_frame, content_frame


def create_section_header(parent: Any, text: str) -> ctk.CTkLabel:
    """Create a section header label."""
    header = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    header.pack(anchor="w", pady=(15, 5), padx=10)
    return header


def create_info_label(parent: Any, text: str) -> ctk.CTkLabel:
    """Create an informational label."""
    label = ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=12),
        justify="left",
        wraplength=600,
    )
    label.pack(anchor="w", pady=(0, 10), padx=20)
    return label
