#!/usr/bin/env python3
"""
Revolution Idle Sacrifice Automation Script

This script automates the zodiac sacrificing process in the game "Revolution Idle".
It operates in two modes: 'setup' to configure the necessary click points and colors,
and 'automation' to perform the repetitive actions.

How it works:
1. Checks the colors of all configured zodiac slots in each cycle.
2. When any zodiac slot's color matches its target, drags that zodiac to the sacrifice box.
3. After the drag, it checks the color of the sacrifice button.
4. If the sacrifice button's color matches, it clicks the button and restarts the sequence.
   If the sacrifice button's color does NOT match, it continues checking zodiac slots.

Important Notes for Revolution Idle:
- You can configure multiple zodiac slots (unlimited by default, or limited by
  MAX_ZODIAC_SLOTS) during setup.
  Each slot will have its color remembered for matching during automation.
- For consistent automation, it is highly recommended to auto-sell other zodiac rarities or
  wait until you have a 100% chance for the desired zodiac type, as the script relies on
  consistent colors at the zodiac slots.
- The sacrifice drag box should be the area where you drag zodiacs to sacrifice them.
- The sacrifice button's target color is hardcoded to (219, 124, 0) to ensure reliability,
  as this button's color is expected to be consistent.

Performance Information:
- Based on testing, the script can achieve approximately 230 sacrifices per minute with 1 slot
  configured and the fastest possible timing settings.
- I can generate around 6 unities per second, while the script reaches a soft limit
  of about 3.8 sacrifices per second due to timing constraints and game responsiveness.
- Your performance may vary depending on your timing settings, computer performance, game
  progression, and the number of zodiac slots configured. More slots may reduce per-slot efficiency.

Author: RLAlpha49
Repository: https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation
"""

import argparse
import logging
import os
import sys
from typing import Any

# Add the project root to Python path to enable imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Configure logging
    log_file = os.path.join(logs_dir, "revolution_idle_automation.log")

    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )

    # Set specific loggers to different levels if needed
    # logging.getLogger("some_module").setLevel(logging.DEBUG)

    logging.info("Logging initialized")
    if debug:
        logging.debug("Debug logging enabled")


def parse_arguments() -> Any:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Revolution Idle Sacrifice Automation Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py               # Run in CLI mode (default)
  python main.py --cli         # Run in CLI mode (explicit)
  python main.py --gui         # Run in GUI mode
  python main.py --gui --debug # Run in GUI mode with debug logging
        """,
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--cli", action="store_true", help="Run in CLI mode (default)"
    )
    mode_group.add_argument(
        "--gui", action="store_true", help="Run in GUI mode using CustomTkinter"
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def main() -> None:
    """Main entry point for the Revolution Idle Sacrifice Automation Script."""
    # Parse arguments
    args = parse_arguments()

    # Set up logging with debug flag
    setup_logging(args.debug)

    # Default to CLI mode if no mode specified
    use_gui = args.gui

    try:
        if use_gui:
            # Try to import GUI dependencies
            try:
                from src.gui.app import RevolutionIdleGUI  # pylint: disable=import-outside-toplevel

                logging.info("Starting Revolution Idle Automation in GUI mode...")
                print("Starting Revolution Idle Automation in GUI mode...")
                gui_app = RevolutionIdleGUI()
                gui_app.run()

            except ImportError as e:
                logging.error("GUI dependencies missing: %s", e)
                print(f"Error: GUI mode requires additional dependencies: {e}")
                print(
                    "Please install the GUI dependencies: pip install customtkinter>=5.2.0"
                )
                print("Alternatively, run in CLI mode: python main.py --cli")
                sys.exit(1)
        else:
            # CLI mode
            from src.app import (  # pylint: disable=import-outside-toplevel
                RevolutionIdleApp,
            )

            logging.info("Starting Revolution Idle Automation in CLI mode...")
            print("Starting Revolution Idle Automation in CLI mode...")
            cli_app = RevolutionIdleApp()
            cli_app.run()

    except KeyboardInterrupt:
        logging.info("Script interrupted by user (Ctrl+C)")
        print("\n\nScript interrupted by user (Ctrl+C). Exiting...")
        sys.exit(0)
    except ImportError as e:
        logging.error("Missing required dependencies: %s", e)
        print(f"\nMissing required dependencies: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        logging.exception("Unhandled exception")
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
