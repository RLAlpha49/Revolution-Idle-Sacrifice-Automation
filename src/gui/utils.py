"""
Utility functions for the GUI components of the Revolution Idle Sacrifice Automation.

This module provides helper functions for GUI-related tasks.
"""

import logging
import time
import webbrowser
from typing import Optional

import customtkinter as ctk  # type: ignore

# Set up module logger
logger = logging.getLogger(__name__)


def open_url(url: str) -> None:
    """
    Open a URL in the default web browser.

    Args:
        url: The URL to open
    """
    try:
        logger.debug("Opening URL: %s", url)
        webbrowser.open(url)
    except Exception:  # pylint: disable=broad-except
        logger.error("Error opening URL", exc_info=True)


def log_message(textbox: Optional[ctk.CTkTextbox], message: str) -> None:
    """
    Add a message to the log textbox with timestamp.

    Args:
        textbox: The textbox to add the message to
        message: The message to add
    """
    if textbox is None:
        logger.warning("Attempted to log message but textbox is None")
        return

    try:
        # Enable editing
        textbox.configure(state="normal")

        # Add message with timestamp
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        # Add message with newline
        textbox.insert("end", formatted_message)

        # Scroll to the end
        textbox.see("end")

        # Disable editing
        textbox.configure(state="disabled")

        # Log to the logger as well
        logger.debug("GUI log: %s", message)
    except Exception:  # pylint: disable=broad-except
        logger.error("Error logging message to textbox", exc_info=True)


def create_scrollable_frame(
    parent: ctk.CTkFrame,
) -> tuple[ctk.CTkScrollableFrame, ctk.CTkFrame]:
    """
    Create a scrollable frame with an inner content frame.

    Args:
        parent: The parent frame

    Returns:
        A tuple containing the scrollable frame and the inner content frame
    """
    try:
        scrollable_frame = ctk.CTkScrollableFrame(parent)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        content_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)

        logger.debug("Created scrollable frame")
        return scrollable_frame, content_frame
    except Exception:  # pylint: disable=broad-except
        logger.error("Error creating scrollable frame", exc_info=True)
        # Create fallback frames in case of error
        fallback_frame = ctk.CTkScrollableFrame(parent)
        fallback_content = ctk.CTkFrame(fallback_frame, fg_color="transparent")
        fallback_content.pack(fill="both", expand=True)
        return fallback_frame, fallback_content


def create_section_header(parent: ctk.CTkFrame, text: str) -> ctk.CTkLabel:
    """
    Create a section header label.

    Args:
        parent: The parent frame
        text: The header text

    Returns:
        The created label
    """
    try:
        header = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        header.pack(anchor="w", pady=(15, 5), padx=10)

        logger.debug("Created section header: %s", text)
        return header
    except Exception:  # pylint: disable=broad-except
        logger.error("Error creating section header '%s'", text, exc_info=True)
        # Return a basic label in case of error
        return ctk.CTkLabel(parent, text=text)


def create_info_label(parent: ctk.CTkFrame, text: str) -> ctk.CTkLabel:
    """
    Create an informational label.

    Args:
        parent: The parent frame
        text: The label text

    Returns:
        The created label
    """
    try:
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=600,
        )
        label.pack(anchor="w", pady=(0, 10), padx=20)

        logger.debug("Created info label: %s...", text[:30] if len(text) > 30 else text)
        return label
    except Exception:  # pylint: disable=broad-except
        logger.error("Error creating info label", exc_info=True)
        # Return a basic label in case of error
        return ctk.CTkLabel(parent, text=text)
