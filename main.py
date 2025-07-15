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
- You can configure multiple zodiac slots (unlimited by default, or limited by MAX_ZODIAC_SLOTS) during setup.
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

import sys
import os

# Add the project root to Python path to enable imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from src.app import RevolutionIdleApp
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print(
        "Please ensure all required dependencies are installed: pip install -r requirements.txt"
    )
    sys.exit(1)


def main():
    """Main entry point for the Revolution Idle Sacrifice Automation Script."""
    try:
        app = RevolutionIdleApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user (Ctrl+C). Exiting...")
        sys.exit(0)
    except ImportError as e:
        print(f"\nMissing required dependencies: {e}")
        print("Please install required packages: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
