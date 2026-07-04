# Flight Data Recorder (FDR)

A GUI application for recording flight data from flight simulators to GeoJSON format.

## Features

- **Simulator Support**: 
  - X-Plane 12 (via REST API on port 8086)
  - Microsoft Flight Simulator 2020/2024 (via SimConnect)
  - Prepar3D (via SimConnect)

- **Automatic Detection**:
  - Takeoff detection (GS > 30kt AND AGL > 0 for > 5 seconds)
  - Landing detection (GS <= 30kt AND AGL = 0 for > 5 seconds)
  - Recording automatically starts on takeoff and stops on landing

- **Output Options**:
  - GeoJSON format (RFC 7946 compliant)
  - Optional trajectory LineString for QGIS visualization
  - Point features for each data sample with all flight parameters

- **Connection Modes**:
  - Automatic connection on monitoring start
  - Manual connection via Connect button
  - Support for manual IP/port configuration (for X-Plane)

## Requirements

- Python 3.8+
- PySide6 6.8.2+
- For X-Plane: `requests` library
- For MSFS/P3D: `SimConnect` library (Windows only)

### Installation

```bash
pip install PySide6 requests
# For MSFS/P3D on Windows:
pip install SimConnect
```

## Usage

### Starting the Application

```bash
cd /path/to/fdr
python fdr.py
```

### Using the GUI

1. **Simulator Settings** (Main Tab):
   - Select your simulator type (X-Plane 12 or MSFS/P3D)
   - For X-Plane: Enter the host IP and port (default: 127.0.0.1:8086)
   - For MSFS/P3D: Host and port are disabled (uses SimConnect directly)
   - Set the poll interval (seconds) for data collection

2. **Output Settings** (Main Tab):
   - Click "Browse..." to select an output file path
   - Choose whether to include a trajectory LineString (for QGIS)
   - Enable/disable auto-connect on monitoring start

3. **Controls** (Main Tab):
   - **Connect**: Establish connection to the simulator
   - **Disconnect**: Close the connection
   - **Start Monitoring**: Begin recording flight data
   - **Stop Monitoring**: Stop recording and close connection

4. **Status** (Main Tab):
   - Connection status (Connected/Disconnected)
   - Flight state (Waiting/In Flight/Landed)
   - Monitoring state (Running/Stopped)
   - Log messages with timestamps

5. **Advanced Tab**:
   - Live aircraft information (ICAO code, name)
   - Real-time flight data (latitude, longitude, altitudes, heading, speeds, power, time)

### Notes

- For X-Plane 12, ensure the REST API plugin is installed and running
- The default X-Plane REST API port is 8086
- For MSFS/P3D, SimConnect must be properly installed and the simulator must be running
- Recording starts automatically when takeoff is detected
- Recording stops automatically when landing is detected
- You can manually stop monitoring at any time

## Output Format

The application generates GeoJSON files (RFC 7946 compliant) containing:

- **Without trajectory option**: FeatureCollection with Point features only
- **With trajectory option**: FeatureCollection with:
  - One LineString feature (trajectory) as the first feature
  - Individual Point features for each data sample

### Point Feature Properties

All values are numeric (RFC 7946 compliant):

- `sim_time`: Simulation timestamp (ISO 8601)
- `alt_msl_m`: Altitude above mean sea level (meters)
- `alt_agl_m`: Altitude above ground level (meters)
- `heading_true_deg`: True heading (degrees)
- `heading_mag_deg`: Magnetic heading (degrees)
- `ias_kt`: Indicated airspeed (knots)
- `gs_kt`: Ground speed (knots)
- `power_hp`: Engine power (horsepower)
- `acf_icao`: Aircraft ICAO code (string)
- `acf_name`: Aircraft name (string)

## Project Structure

```
fdr/
├── fdr.py                 # Main application entry point
├── regenerate_ui.sh       # Script to regenerate UI from .ui file
├── README.md              # This file
├── ui/
│   ├── __init__.py
│   ├── gui_fdr.ui         # Qt Designer UI file
│   └── gui_fdr.py         # Generated Python UI file
└── sims_monitor/
    ├── __init__.py
    ├── sim_monitor.py      # Simulator monitoring logic
    └── translations.py     # Internationalization support
```

## Regenerating UI Files

If you modify `gui_fdr.ui` using Qt Designer, regenerate the Python file:

```bash
./regenerate_ui.sh
```

This script:
1. Runs `pyside6-uic` to generate `gui_fdr.py` from `gui_fdr.ui`
2. Fixes a known issue with QDoubleSpinBox decimal properties

## Development

### Adding New Features

1. Modify the UI in Qt Designer and save to `gui_fdr.ui`
2. Run `./regenerate_ui.sh` to update `gui_fdr.py`
3. Update `fdr.py` with new signal/slot connections
4. Test the changes

### Translations

UI strings can be translated by modifying the strings in `gui_fdr.ui` or by adding translation support in `fdr.py`. The `sims_monitor` module has its own translation system in `translations.py`.

## Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"

Install PySide6:
```bash
pip install PySide6
```

### "Connection failed" for X-Plane

- Ensure X-Plane is running
- Ensure the REST API plugin is installed and enabled
- Check the IP address and port in Settings
- Verify the plugin port matches the configured port

### "SimConnect not installed" for MSFS/P3D

- Ensure you're running on Windows
- Install SimConnect: `pip install SimConnect`
- Ensure MSFS or P3D is running

### UI Not Updating

- Ensure the poll interval is not too high
- Check the log messages for errors
- The minimum UI update interval is 500ms to prevent UI freezing

## License

This software is provided as-is for use with AirRallies applications.

## Version History

- **1.0.0**: Initial release with X-Plane and MSFS/P3D support
