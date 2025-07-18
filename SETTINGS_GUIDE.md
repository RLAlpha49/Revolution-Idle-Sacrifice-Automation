# Revolution Idle Sacrifice Automation - Settings Guide

## Settings File Location

When you run the script for the first time, it will automatically create a `user_settings.json` file in the same directory as the script/executable. This file contains all configurable settings with helpful comments explaining each option.

### Available Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `color_tolerance` | Number | 15 | How close colors need to be to match (0 = exact match, higher = more tolerant) |
| `delay_before_check` | Number | 0.02 | Delay before checking pixel colors in the automation loop (seconds) |
| `delay_after_press` | Number | 0.02 | Delay immediately after a mouse press (seconds) |
| `delay_drag_duration` | Number | 0.02 | Duration of the mouse drag action (seconds) |
| `delay_after_drag` | Number | 0.11 | Delay after completing a drag action (seconds) |
| `delay_after_click` | Number | 0.01 | Delay after performing a click action (seconds) |
| `stop_key` | String | "q" | Keyboard key to stop automation (e.g., "q", "p", "esc", "f1", "space") |
| `max_zodiac_slots` | Number | -1 | Maximum zodiac slots to configure (-1 = unlimited, positive number = limit) |
| `debug_color_matching` | Boolean | false | Show detailed color matching info during automation |
| `message_level` | String | "info" | Message verbosity level ("info" or "debug") |

### How to Modify Settings

#### Using the Settings Editor (GUI Mode)

The easiest way to modify settings is through the built-in settings editor in GUI mode:

1. **Launch the application in GUI mode**: `python main.py --gui`
2. **Click the "Settings" button** in the main interface
3. **Adjust settings** using the intuitive controls:
   - Sliders for numeric values
   - Switches for boolean values
   - Dropdown menus for options
   - Text fields for strings
4. **Click "Save Settings"** to apply your changes
5. The settings will be automatically saved and reloaded

#### Manually Editing the Settings File

You can also edit the settings file directly:

1. **Locate the settings file**: Look for `user_settings.json` in the same directory as your script/executable
2. **Edit the file**: Open it with any text editor (Notepad, VS Code, etc.)
3. **Modify values**: Change the values for the settings you want to customize
4. **Save the file**: Save your changes
5. **Reload or restart**: Either use the "Reload Settings" option in the main menu (option 4) or restart the script

### Example Settings File

```json
{
    "color_tolerance": 15,
    "delay_before_check": 0.02,
    "delay_after_press": 0.02,
    "delay_drag_duration": 0.02,
    "delay_after_drag": 0.11,
    "delay_after_click": 0.01,
    "stop_key": "q",
    "max_zodiac_slots": -1,
    "debug_color_matching": false,
    "message_level": "info"
}
```

### Performance Tuning

- **Faster automation**: Decrease delay values (but be careful not to make them too small as it may cause instability)
- **More stable automation**: Increase delay values, especially `delay_after_drag`
- **Color matching issues**: Increase `color_tolerance` if colors aren't being detected properly
- **Debugging**: Set `debug_color_matching` to `true` and `message_level` to `"debug"` for detailed output

### Important Notes

- Boolean values should be `true` or `false` (lowercase, no quotes)
- String values should be in quotes: `"value"`
- Number values should not be in quotes: `15` or `0.02`
- Save the file as UTF-8 encoding
- Invalid JSON will cause the script to fall back to default settings
- Some settings changes may require restarting the script to take full effect

### Troubleshooting

**Settings not loading**:

- Check that the JSON syntax is valid
- Ensure the file is saved as UTF-8
- Try using the "Reload Settings" option in the main menu

**Performance issues**:

- Try increasing delay values if the automation is too fast for your system
- Decrease delay values carefully if you want faster performance

**Color detection problems**:

- Increase `color_tolerance` value
- Enable `debug_color_matching` to see detailed color information
