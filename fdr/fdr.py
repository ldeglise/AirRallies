#!/usr/bin/env python3
"""
Flight Data Recorder - Main Application

This is the main entry point for the Flight Data Recorder GUI application.
It provides a user interface to monitor flight simulators (X-Plane 12, MSFS 2020/2024, P3D)
and record flight data to GeoJSON files.

Usage:
    python fdr.py

Features:
    - Monitor X-Plane 12 or MSFS/P3D simulators
    - Auto-detection of takeoff and landing
    - Real-time data display
    - GeoJSON output with optional trajectory LineString
    - Manual or automatic connection modes
"""

import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QFileDialog, 
    QMessageBox,
    QInputDialog
)
from PySide6.QtCore import QTimer, Qt, QThread, Signal, Slot, QObject
from PySide6.QtGui import QColor, QPalette

# Import the generated UI
from ui.gui_fdr import Ui_MainWindow

# Import the simulator monitor
from sims_monitor.sim_monitor import (
    create_monitor,
    SimulatorType,
    FlightState,
    check_simulator_available
)


# ---------------------------------------------------------------------------
# Thread for live data polling (to avoid blocking the UI)
# ---------------------------------------------------------------------------

class DataPoller(QObject):
    """
    Thread that periodically polls live data from the simulator
    and emits signals to update the UI.
    """
    
    data_updated = Signal(dict)
    connection_changed = Signal(bool, str)
    flight_state_changed = Signal(str)
    monitoring_state_changed = Signal(str)
    log_message = Signal(str)
    
    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self._running = False
        self._timer = None
    
    def start(self, interval_ms=1000):
        """Start polling at the given interval (milliseconds)."""
        self._running = True
        self._timer = QTimer()
        self._timer.timeout.connect(self.poll_data)
        self._timer.start(interval_ms)
    
    def stop(self):
        """Stop polling."""
        self._running = False
        if self._timer:
            self._timer.stop()
    
    def poll_data(self):
        """Poll data from monitor and emit update signals."""
        if not self._running or not self.monitor:
            return
        
        try:
            # Get current data
            if self.monitor.is_connected:
                data = self.monitor.get_data()
                if data:
                    self.data_updated.emit(data)
            
            # Check connection status
            is_connected = self.monitor.is_connected
            if is_connected:
                status = "Connected"
            else:
                status = "Disconnected"
            self.connection_changed.emit(is_connected, status)
            
            # Check flight state
            state = self.monitor.flight_state
            state_str = state.value.replace("_", " ").title()
            self.flight_state_changed.emit(state_str)
            
            # Check monitoring state
            if self.monitor._running:
                self.monitoring_state_changed.emit("Running")
            else:
                self.monitoring_state_changed.emit("Stopped")
                
        except Exception as e:
            self.log_message.emit(f"Error polling data: {e}")


# ---------------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """
    Main application window for Flight Data Recorder.
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Setup additional UI properties
        self._setup_ui_extras()
        
        # Initialize monitor
        self.monitor = None
        self.poller = None
        self.poll_thread = None
        self.last_output_file = None
        
        # Connect signals
        self._connect_signals()
        
        # Set initial state
        self._update_ui_state()
        
        # Log startup message
        self.log_message("Application started. Ready for monitoring.")
        
        # Set default output file path
        default_path = os.path.expanduser(f"~/flight_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.ui.lineEditOutputFile.setText(default_path)
    
    def _setup_ui_extras(self):
        """Setup additional UI properties that can't be set in Qt Designer."""
        # Set combo box items properly
        self.ui.comboSimulatorType.clear()
        self.ui.comboSimulatorType.addItem("X-Plane 12", SimulatorType.XPLANE.value)
        self.ui.comboSimulatorType.addItem("MSFS 2020/2024 / P3D", SimulatorType.MSFS.value)
        
        # Set default simulator type
        self.ui.comboSimulatorType.setCurrentIndex(0)
        
        # Configure text browser for logging
        self.ui.textBrowserLog.setOpenExternalLinks(True)
        
        # Set initial status message using native status bar
        self.statusBar().showMessage("Ready")
    
    def _connect_signals(self):
        """Connect all UI signals to their slots."""
        # File menu
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.show_about)
        
        # Browse button
        self.ui.pushButtonBrowse.clicked.connect(self.browse_output_file)
        
        # Control buttons
        self.ui.pushButtonConnect.clicked.connect(self.on_connect)
        self.ui.pushButtonDisconnect.clicked.connect(self.on_disconnect)
        self.ui.pushButtonStart.clicked.connect(self.on_start_monitoring)
        self.ui.pushButtonStop.clicked.connect(self.on_stop_monitoring)
        
        # Simulator type change
        self.ui.comboSimulatorType.currentIndexChanged.connect(self._update_ui_state)
        
        # Host and port changes
        self.ui.lineEditHost.textChanged.connect(self._validate_settings)
        self.ui.spinBoxPort.valueChanged.connect(self._validate_settings)
        self.ui.spinBoxPollInterval.valueChanged.connect(self._validate_settings)
        
        # Checkbox changes
        self.ui.checkBoxAutoConnect.stateChanged.connect(self._validate_settings)
        self.ui.checkBoxIncludeTrajectory.stateChanged.connect(self._validate_settings)
    
    def _validate_settings(self):
        """Validate that all settings are valid."""
        # For now, just ensure output file is set
        has_output = bool(self.ui.lineEditOutputFile.text().strip())
        has_host = bool(self.ui.lineEditHost.text().strip())
        has_port = self.ui.spinBoxPort.value() > 0
        
        # Enable/disable buttons based on settings
        self.ui.pushButtonStart.setEnabled(has_output and has_host and has_port)
    
    def _update_ui_state(self):
        """Update UI state based on current monitor and settings."""
        # Determine if we're in MSFS mode (host/port disabled)
        is_msfs = self._get_selected_simulator_type() == SimulatorType.MSFS.value
        
        # Enable/disable host and port for MSFS (not used)
        self.ui.lineEditHost.setEnabled(not is_msfs)
        self.ui.labelHost.setEnabled(not is_msfs)
        self.ui.spinBoxPort.setEnabled(not is_msfs)
        self.ui.labelPort.setEnabled(not is_msfs)
        
        # Validate settings
        self._validate_settings()
        
        # Update button states
        if self.monitor:
            self.ui.pushButtonConnect.setEnabled(not self.monitor.is_connected)
            self.ui.pushButtonDisconnect.setEnabled(self.monitor.is_connected)
            self.ui.pushButtonStart.setEnabled(
                not self.monitor._running and 
                bool(self.ui.lineEditOutputFile.text().strip())
            )
            self.ui.pushButtonStop.setEnabled(self.monitor._running)
        else:
            self.ui.pushButtonConnect.setEnabled(True)
            self.ui.pushButtonDisconnect.setEnabled(False)
            self.ui.pushButtonStart.setEnabled(
                bool(self.ui.lineEditOutputFile.text().strip())
            )
            self.ui.pushButtonStop.setEnabled(False)
    
    def _get_selected_simulator_type(self):
        """Get the currently selected simulator type."""
        return self.ui.comboSimulatorType.currentData()
    
    def _get_host(self):
        """Get the current host setting."""
        return self.ui.lineEditHost.text().strip()
    
    def _get_port(self):
        """Get the current port setting."""
        return self.ui.spinBoxPort.value()
    
    def _get_poll_interval(self):
        """Get the current poll interval in seconds."""
        return self.ui.spinBoxPollInterval.value()
    
    def _get_output_file(self):
        """Get the current output file path."""
        return self.ui.lineEditOutputFile.text().strip()
    
    def _get_include_trajectory(self):
        """Get whether to include trajectory."""
        return self.ui.checkBoxIncludeTrajectory.isChecked()
    
    def _get_auto_connect(self):
        """Get whether to auto-connect."""
        return self.ui.checkBoxAutoConnect.isChecked()
    
    def log_message(self, message):
        """Add a message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        
        # Add to text browser
        self.ui.textBrowserLog.append(formatted)
        
        # Show message in native status bar (temporary, auto-clears after timeout)
        self.statusBar().showMessage(message, timeout=5000)
        
        # Auto-scroll to bottom
        from PySide6.QtGui import QTextCursor
        self.ui.textBrowserLog.moveCursor(QTextCursor.MoveOperation.End)
    
    def browse_output_file(self):
        """Open file dialog to select output file."""
        options = QFileDialog.Option.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            self._get_output_file() or os.path.expanduser("~"),
            "GeoJSON Files (*.json *.geojson);;All Files (*)"
        )
        
        if file_path:
            # Ensure the file has a valid extension
            if not file_path.lower().endswith((".json", ".geojson")):
                file_path += ".json"
            
            self.ui.lineEditOutputFile.setText(file_path)
            self.last_output_file = file_path
            self._validate_settings()
    
    def create_monitor_instance(self):
        """Create a new monitor instance based on current settings."""
        # Clean up existing monitor
        self.cleanup_monitor()
        
        sim_type = self._get_selected_simulator_type()
        host = self._get_host()
        port = self._get_port()
        poll_interval = self._get_poll_interval()
        output_file = self._get_output_file()
        include_trajectory = self._get_include_trajectory()
        auto_connect = self._get_auto_connect()
        
        if not output_file:
            self.log_message("Error: No output file specified")
            QMessageBox.warning(self, "Error", "Please specify an output file path.")
            return None
        
        try:
            monitor = create_monitor(
                simulator_type=sim_type,
                geojson_path=output_file,
                host=host,
                port=port,
                poll_interval=poll_interval,
                include_trajectory=include_trajectory,
                auto_connect=False  # We'll handle connection manually
            )
            
            # Set up connection callback
            monitor.set_connection_callback(self.on_connection_status_changed)
            
            self.monitor = monitor
            self.log_message(f"Monitor created for {sim_type} simulator")
            
            return monitor
            
        except Exception as e:
            self.log_message(f"Error creating monitor: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create monitor: {e}")
            return None
    
    def cleanup_monitor(self):
        """Clean up existing monitor and poller."""
        # Stop poller
        if self.poller:
            self.poller.stop()
            self.poller = None
        
        # Stop monitor
        if self.monitor:
            if self.monitor._running:
                self.monitor.stop_monitoring()
            self.monitor.disconnect()
            self.monitor = None
        
        # Clean up thread
        if self.poll_thread:
            self.poll_thread.quit()
            self.poll_thread.wait()
            self.poll_thread = None
    
    def on_connection_status_changed(self, connected, message):
        """Callback for monitor connection status changes."""
        # Update connection status label
        self.ui.labelConnectionStatus.setText("Connected" if connected else "Disconnected")
        
        # Set color
        palette = self.ui.labelConnectionStatus.palette()
        if connected:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
        else:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
        self.ui.labelConnectionStatus.setPalette(palette)
        
        # Log message
        self.log_message(message)
        
        # Update button states
        self._update_ui_state()
    
    def on_connect(self):
        """Handle Connect button click."""
        # Ensure we have a monitor
        if not self.monitor:
            self.create_monitor_instance()
        
        if not self.monitor:
            return
        
        try:
            success = self.monitor.connect()
            if success:
                self.log_message("Successfully connected to simulator")
                self._update_ui_state()
                
                # Start polling live data
                self.start_polling()
            else:
                self.log_message("Failed to connect to simulator")
        except Exception as e:
            self.log_message(f"Connection error: {e}")
            QMessageBox.critical(self, "Connection Error", str(e))
    
    def on_disconnect(self):
        """Handle Disconnect button click."""
        if self.monitor:
            try:
                self.monitor.disconnect()
                self.log_message("Disconnected from simulator")
            except Exception as e:
                self.log_message(f"Error disconnecting: {e}")
        
        # Stop polling
        if self.poller:
            self.poller.stop()
        
        self._update_ui_state()
    
    def on_start_monitoring(self):
        """Handle Start Monitoring button click."""
        # Ensure we have a monitor
        if not self.monitor:
            self.create_monitor_instance()
        
        if not self.monitor:
            return
        
        # Get fresh settings
        output_file = self._get_output_file()
        if not output_file:
            QMessageBox.warning(self, "Error", "Please specify an output file.")
            return
        
        # Check if we need to recreate monitor with new settings
        if (self.monitor.geojson_writer.filepath != output_file or
            self._get_include_trajectory() != self.monitor.geojson_writer._include_trajectory):
            self.log_message("Output settings changed, recreating monitor...")
            self.create_monitor_instance()
        
        if not self.monitor:
            return
        
        try:
            # Set auto-connect based on preference
            if self._get_auto_connect() and not self.monitor.is_connected:
                self.monitor.connect()
            
            # Start monitoring
            self.monitor.start_monitoring()
            self.log_message("Monitoring started")
            
            # Start polling
            self.start_polling()
            
            self._update_ui_state()
            
        except Exception as e:
            self.log_message(f"Error starting monitoring: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start monitoring: {e}")
    
    def on_stop_monitoring(self):
        """Handle Stop Monitoring button click."""
        if self.monitor and self.monitor._running:
            try:
                self.monitor.stop_monitoring()
                self.log_message("Monitoring stopped")
            except Exception as e:
                self.log_message(f"Error stopping monitoring: {e}")
        
        # Stop polling
        if self.poller:
            self.poller.stop()
        
        self._update_ui_state()
    
    def start_polling(self):
        """Start the data poller thread."""
        # Stop existing poller
        if self.poller:
            self.poller.stop()
        
        # Create new poller
        if self.monitor:
            self.poller = DataPoller(self.monitor)
            self.poller.data_updated.connect(self.on_data_updated)
            self.poller.connection_changed.connect(self.on_poller_connection_changed)
            self.poller.flight_state_changed.connect(self.on_poller_flight_state_changed)
            self.poller.monitoring_state_changed.connect(self.on_poller_monitoring_state_changed)
            self.poller.log_message.connect(self.log_message)
            
            # Start polling at a reasonable interval
            poll_interval_ms = int(self._get_poll_interval() * 1000)
            self.poller.start(max(poll_interval_ms, 500))  # Minimum 500ms for UI updates
    
    def on_data_updated(self, data):
        """Handle new data from the simulator."""
        try:
            # Update aircraft info
            if 'acf_icao' in data:
                self.ui.labelAircraftICAOValue.setText(str(data.get('acf_icao', 'N/A')))
            if 'acf_name' in data:
                self.ui.labelAircraftNameValue.setText(str(data.get('acf_name', 'N/A')))
            
            # Update flight data
            if 'latitude' in data:
                self.ui.labelLatitudeValue.setText(str(data.get('latitude', 'N/A')))
            if 'longitude' in data:
                self.ui.labelLongitudeValue.setText(str(data.get('longitude', 'N/A')))
            if 'alt_msl' in data:
                self.ui.labelAltitudeValue.setText(str(data.get('alt_msl', 'N/A')))
            if 'alt_agl' in data:
                self.ui.labelAGLValue.setText(str(data.get('alt_agl', 'N/A')))
            if 'heading_true' in data:
                self.ui.labelHeadingValue.setText(str(data.get('heading_true', 'N/A')))
            if 'gs' in data:
                self.ui.labelGroundSpeedValue.setText(str(data.get('gs', 'N/A')))
            if 'ias' in data:
                self.ui.labelIndicatedSpeedValue.setText(str(data.get('ias', 'N/A')))
            if 'power' in data:
                self.ui.labelPowerValue.setText(str(data.get('power', 'N/A')))
            if 'sim_time' in data:
                self.ui.labelSimTimeValue.setText(str(data.get('sim_time', 'N/A')))
                
        except Exception as e:
            self.log_message(f"Error updating data display: {e}")
    
    def on_poller_connection_changed(self, connected, status):
        """Handle poller connection status updates."""
        self.ui.labelConnectionStatus.setText(status)
        palette = self.ui.labelConnectionStatus.palette()
        if connected:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
        else:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
        self.ui.labelConnectionStatus.setPalette(palette)
        self._update_ui_state()
    
    def on_poller_flight_state_changed(self, state_str):
        """Handle flight state updates from poller."""
        self.ui.labelFlightStatus.setText(state_str)
        
        # Set color based on state
        palette = self.ui.labelFlightStatus.palette()
        if state_str == "In Flight":
            palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
        elif state_str == "Landed":
            palette.setColor(QPalette.ColorRole.WindowText, QColor("orange"))
        else:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("blue"))
        self.ui.labelFlightStatus.setPalette(palette)
    
    def on_poller_monitoring_state_changed(self, state_str):
        """Handle monitoring state updates from poller."""
        self.ui.labelMonitoringStatus.setText(state_str)
        palette = self.ui.labelMonitoringStatus.palette()
        if state_str == "Running":
            palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
        else:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
        self.ui.labelMonitoringStatus.setPalette(palette)
        self._update_ui_state()
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Flight Data Recorder</h2>
        <p>Version 1.0.0</p>
        <p>A tool for recording flight data from flight simulators to GeoJSON format.</p>
        <p><b>Supported Simulators:</b></p>
        <ul>
            <li>X-Plane 12 (via REST API on port 8086)</li>
            <li>Microsoft Flight Simulator 2020/2024 (via SimConnect)</li>
            <li>Prepar3D (via SimConnect)</li>
        </ul>
        <p><b>Features:</b></p>
        <ul>
            <li>Real-time flight data recording</li>
            <li>Auto-detection of takeoff and landing</li>
            <li>GeoJSON output (RFC 7946 compliant)</li>
            <li>Optional trajectory LineString for QGIS visualization</li>
            <li>Manual or automatic connection modes</li>
        </ul>
        <p><b>Output:</b> GeoJSON files with Point features for each data sample, 
        optionally including a LineString feature for trajectory visualization.</p>
        <p><b>Author:</b> AirRallies Development Team</p>
        """
        QMessageBox.about(self, "About Flight Data Recorder", about_text)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up resources
        self.cleanup_monitor()
        
        # Accept the close event
        event.accept()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    
    # Set application details
    app.setApplicationName("Flight Data Recorder")
    app.setOrganizationName("AirRallies")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
