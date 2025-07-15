# Revolution Idle Sacrifice Automation Script

This script automates the zodiac sacrificing process in the game **Revolution Idle**. It streamlines repetitive tasks by automating mouse movements and clicks based on pixel color detection.

---

## Features

- **Two Modes:**
  - **Setup Mode:** Configure on-screen locations (coordinates) and colors for your specific computer and game resolution.
  - **Automation Mode:** Runs the automated sacrificing process using your saved configuration.
- **Configurable Settings:** Adjust delays, stop key, slot limits, and message verbosity directly in the script
- **Persistent Configuration:** Saves settings to `revolution_idle_zodiac_automation_config.json` for reuse
- **Flexible Stop Key:** Use a character or special key (e.g., `esc`, `space`, `ctrl`) to stop automation

---

## How it Works

The script follows this logic:

1. **Multiple Zodiac Slot Check:** Monitors the colors of all configured zodiac slots in each cycle
2. **Drag Action:** When any zodiac slot's color matches its target, drags that zodiac to the "Sacrifice Drag Box"
3. **Sacrifice Button Check:** Checks the color of the "Sacrifice Button"
4. **Conditional Click & Restart:**
   - If the button color matches `(219, 124, 0)`, clicks the button and restarts
   - If not, continues checking all zodiac slots for matches

> [!NOTE]
> For consistent automation, auto-sell other zodiac rarities or wait for a 100% chance for the desired zodiac type. The script relies on consistent colors at the zodiac slots.

---

## Setup and Installation

### Prerequisites

- Python 3.x
- `pynput` library (for mouse/keyboard control)
- `Pillow` library (for screen capture and pixel color detection)

### Installation

1. **Clone Repository:**

   ```bash
   git clone https://github.com/RLAlpha49/Revolution-Idle-Sacrifice-Automation.git
   ```

2. **Install Libraries:**  

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the Script:**  
   Navigate to the script directory and run:

   ```sh
   python main.py
   ```

2. **Select a Mode:**  
   The script presents a menu:

   ```text
   1. Setup Mode (Configure click points and colors)
   2. Automation Mode (Run the automation)
   3. Help (Learn more about the script and settings)
   4. Exit (Quit the script)
   ```

   - **1 or setup:** Guides you to set multiple click points:
     - **Multiple Zodiac Slots:** Left-click on each zodiac slot you want to monitor (unlimited by default)
     - **Right-click** when finished adding zodiac slots to proceed
     - **Sacrifice Drag Box:** Where zodiacs are dragged to sacrifice
     - **Sacrifice Button:** The sacrifice confirmation button
     - Saves configuration to `revolution_idle_zodiac_automation_config.json`
   - **2 or automation:** Starts automation using saved config  
     Stop with the configured STOP_KEY (default: `q`)
   - **3 or help:** Shows detailed info
   - **4 or exit:** Quits the script  
     (You can also press `Ctrl+C` to quit anytime)

---

## User Configurable Settings

All user-configurable settings are located in `config/settings.py`:

### Multiple Zodiac Slots Configuration

- `MAX_ZODIAC_SLOTS`: Maximum number of zodiac slots (default: `-1` for unlimited)
  - Set to `-1` for unlimited slots
  - Set to a positive number to limit the maximum

### Color Matching

- `COLOR_TOLERANCE`: How close colors need to match (default: `15`)
  - `0` = exact match, higher = more tolerant
  - Increase if zodiac automation only works on some slots
- `DEBUG_COLOR_MATCHING`: Show detailed color matching info (default: `False`)
  - Set to `True` for troubleshooting color tolerance issues
  - Requires `MESSAGE_LEVEL = "debug"` to see output

### Timing Controls

Adjust for your computer/game responsiveness. Smaller = faster, but less reliable.

- `DELAY_BEFORE_CHECK`: Delay before checking pixel colors (seconds)
- `DELAY_AFTER_PRESS`: Delay after mouse press (seconds)
- `DELAY_DRAG_DURATION`: Mouse drag duration (seconds)
- `DELAY_AFTER_DRAG`: Delay after drag (seconds)
- `DELAY_AFTER_CLICK`: Delay after click (seconds)

### User Interface

- `STOP_KEY`: Key to stop automation (default: `'q'`)
  - Can be a character or special key (e.g., `'esc'`, `'space'`, `'ctrl'`, etc.)
- `MESSAGE_LEVEL`: Console output verbosity
  - `'info'`: Standard messages (default)
  - `'debug'`: Detailed messages for troubleshooting

## Troubleshooting

### Color Tolerance Issues

If the automation only works on some zodiac slots:

1. **Increase Color Tolerance:** Set `COLOR_TOLERANCE` to a higher value (try 20-25)
2. **Enable Debug Mode:**

   ```python
   DEBUG_COLOR_MATCHING = True
   MESSAGE_LEVEL = "debug"
   ```

3. **Analyze Output:** Look for `MaxDiff` values that exceed your tolerance
4. **Adjust Accordingly:** Set tolerance higher than the maximum difference you see

### Setup Guidance

If you need help identifying the correct click points, check the visual guide below.

---

## Performance Information

Based on testing with Revolution Idle:

- **Script Performance:** Approximately **230 sacrifices per minute** with 1 slot configured and optimal timing settings
- **Manual vs Automation:** I can achieve ~6 unities per second, while the script reaches a soft limit of ~3.8 sacrifices per second
- **Performance Factors:** Your results may vary depending on:
  - Timing settings (faster settings = higher risk of inconsistency)
  - Computer performance and responsiveness
  - Current game progression and zodiac generation rate
  - Number of zodiac slots configured (more slots may reduce per-slot efficiency)
- **Optimization Tips:** For maximum performance, use a single slot with the fastest timing settings that still maintain reliability

> [!NOTE]
> The 230 sacrifices/minute rate represents a practical soft limit due to game timing constraints and automation overhead. Individual results may vary based on system performance and game state.

---

## Visual Guide for Click Points

![Click Points](https://github.com/user-attachments/assets/6697f003-f5f4-4d7e-8d4c-7d353f0278da)

### Setup Instructions

1. **Zodiac Slots:** Click on each zodiac slot you want to monitor (the colored areas where zodiacs appear)
2. **Sacrifice Drag Box:** Click on the area where you drag zodiacs to sacrifice them
3. **Sacrifice Button:** Click on the sacrifice confirmation button

> [!TIP]
> For best results, click on a consistent part of each zodiac slot (e.g., always a corner) to ensure reliable color detection.

---

## Modules Overview

### Project Structure

```text
Revolution Idle/
├── main.py                  # Main entry point
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── LICENSE                  # License file
├── config/                  # Configuration management
│   ├── __init__.py
│   ├── settings.py          # User-configurable settings
│   └── config_manager.py    # Configuration loading/saving
├── src/                     # Main source code
│   ├── __init__.py
│   ├── app.py               # Main application controller
│   ├── automation_engine.py # Core automation logic
│   ├── setup_manager.py     # Setup mode handler
│   ├── input_handlers.py    # Mouse and keyboard event handlers
│   └── help.py              # Help and documentation
└── utils/                   # Utility functions
    ├── __init__.py
    ├── color_utils.py       # Color detection and matching
    └── display_utils.py     # Console output and performance tracking
```

### Core Modules

- **`src/app.py`**: Main application controller that orchestrates all components
- **`src/automation_engine.py`**: Contains the core automation logic for zodiac sacrificing
- **`src/setup_manager.py`**: Handles the interactive setup process
- **`src/input_handlers.py`**: Manages mouse and keyboard event handling

### Configuration

- **`config/settings.py`**: All user-configurable settings
- **`config/config_manager.py`**: Handles loading/saving configuration data

### Utilities

- **`utils/color_utils.py`**: Color detection and matching functions
- **`utils/display_utils.py`**: Console output and performance tracking

### Documentation

- **`src/help.py`**: Comprehensive help and usage information

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script!
