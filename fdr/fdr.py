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
from PySide6.QtCore import QTimer, Qt, QThread, Signal, Slot, QObject, QDir
from PySide6.QtGui import QColor, QPalette, QIcon

# Import the generated UI
from ui.gui_fdr import Ui_MainWindow

# Import the resources (generated from resources.qrc)
# This import is optional - if resources_rc.py doesn't exist, we'll fall back to file-based icons
try:
    from ui import resources_rc
except ImportError:
    # resources_rc.py not found - this is expected during local development
    # without running generate_resources.py first
    resources_rc = None

# Import the GUI translations
from ui.translations import (
    gettext as gui_trans,
    set_language as set_gui_language,
    get_language as get_gui_language,
    on_language_change,
    set_language_both,
    TranslationManager
)

# Import the simulator monitor
from sims_monitor.sim_monitor import (
    create_monitor,
    SimulatorType,
    FlightState,
    check_simulator_available
)

# Convenience alias for GUI translations
_ = gui_trans


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
            # Use translated strings for status
            from ui.translations import gettext as gui_trans_poller
            status = gui_trans_poller("CONNECTION_CONNECTED") if is_connected else gui_trans_poller("CONNECTION_DISCONNECTED")
            self.connection_changed.emit(is_connected, status)
            
            # Check flight state
            state = self.monitor.flight_state
            # Translate flight state
            state_mapping = {
                FlightState.WAITING: gui_trans_poller("FLIGHT_STATE_WAITING"),
                FlightState.IN_FLIGHT: gui_trans_poller("FLIGHT_STATE_IN_FLIGHT"),
                FlightState.LANDED: gui_trans_poller("FLIGHT_STATE_LANDED"),
            }
            state_str = state_mapping.get(state, state.value.replace("_", " ").title())
            self.flight_state_changed.emit(state_str)
            
            # Check monitoring state
            if self.monitor._running:
                self.monitoring_state_changed.emit(gui_trans_poller("MONITORING_RUNNING"))
            else:
                self.monitoring_state_changed.emit(gui_trans_poller("MONITORING_STOPPED"))
                
        except Exception as e:
            self.log_message.emit(gui_trans_poller("ERROR_POLLING_DATA", error=str(e)))


# ---------------------------------------------------------------------------
# Main Application Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """
    Main application window for Flight Data Recorder.
    """
    
    def __init__(self):
        super().__init__()
        
        # Set window icon first thing
        icon = QIcon(":/icons/icon.png")
        if icon.isNull():
            icon_file = os.path.join(os.path.dirname(__file__), "ui", "icons", "icon.png")
            if os.path.exists(icon_file):
                icon = QIcon(icon_file)
        if not icon.isNull():
            self.setWindowIcon(icon)
        
        # Initialize language detection and translations
        # This must be done BEFORE creating the UI
        self._init_translations()
        
        # Initialize UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Setup additional UI properties
        self._setup_ui_extras()
        
        # Apply translations to UI
        self._retranslate_ui()
        
        # Initialize monitor
        self.monitor = None
        self.poller = None
        self.poll_thread = None
        self.last_output_file = None
        
        # Connect signals
        self._connect_signals()
        
        # Setup status message timer (to process messages from monitor queue)
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._process_status_messages)
        self.status_timer.start(100)  # Check for status messages 10 times per second
        
        # Set initial state
        self._update_ui_state()
        
        # Set default output file path
        default_path = os.path.expanduser(f"~/flight_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.ui.lineEditOutputFile.setText(default_path)
    
    def _init_translations(self):
        """Initialize language detection and setup language menu."""
        # Detect system language and set it (will fall back to English if not available)
        set_gui_language(None)  # None = auto-detect
        
        # Synchronize with sim_monitor translations
        set_language_both(get_gui_language())
        
        # Register callback for language changes
        on_language_change(self._retranslate_ui)
    
    def _setup_ui_extras(self):
        """Setup additional UI properties that can't be set in Qt Designer."""
        # Set combo box items properly
        self.ui.comboSimulatorType.clear()
        self.ui.comboSimulatorType.addItem(_("SIMULATOR_XPLANE_12"), SimulatorType.XPLANE.value)
        self.ui.comboSimulatorType.addItem(_("SIMULATOR_MSFS_P3D"), SimulatorType.MSFS.value)
        
        # Set default simulator type
        self.ui.comboSimulatorType.setCurrentIndex(0)
        
        # Configure text browser for logging
        self.ui.textBrowserLog.setOpenExternalLinks(True)
        
        # Set initial status message using native status bar
        self.statusBar().showMessage(_("READY"))
        
        # Setup language menu
        self._setup_language_menu()
    
    def _setup_language_menu(self):
        """Setup the Language menu in the menu bar."""
        # Create Language menu - insert before Help menu to keep Help as last
        from PySide6.QtWidgets import QMenu
        self.menuLanguage = QMenu(_("LANGUAGE_MENU"), self)
        
        # Add language actions
        self.actionEnglish = self.menuLanguage.addAction(_("LANGUAGE_ENGLISH"))
        self.actionFrench = self.menuLanguage.addAction(_("LANGUAGE_FRENCH"))
        
        # Connect language actions
        self.actionEnglish.triggered.connect(lambda: set_language_both("en"))
        self.actionFrench.triggered.connect(lambda: set_language_both("fr"))
        
        # Insert Language menu before Help menu (so Help stays last on the right)
        self.ui.menubar.insertMenu(self.ui.menuHelp.menuAction(), self.menuLanguage)
        
        # Mark current language
        current_lang = get_gui_language()
        if current_lang == "fr":
            self.actionFrench.setChecked(True)
        else:
            self.actionEnglish.setChecked(True)
    
    def _retranslate_ui(self, lang: str = None):
        """Retranslate the entire UI based on current language."""
        # Update window title
        self.setWindowTitle(_("FLIGHT_DATA_RECORDER_TITLE"))
        
        # Update menu bar
        self.ui.menuFile.setTitle(_("FILE_MENU"))
        self.ui.menuHelp.setTitle(_("HELP_MENU"))
        self.ui.actionExit.setText(_("EXIT_ACTION"))
        self.ui.actionAbout.setText(_("ABOUT_ACTION"))
        
        # Update language menu if it exists
        if hasattr(self, 'menuLanguage'):
            self.menuLanguage.setTitle(_("LANGUAGE_MENU"))
            self.actionEnglish.setText(_("LANGUAGE_ENGLISH"))
            self.actionFrench.setText(_("LANGUAGE_FRENCH"))
            # Update checked state - utiliser lang passé en paramètre (évite appel à get_gui_language())
            current_lang = lang or get_gui_language() or "en"
            if current_lang == "fr":
                self.actionFrench.setChecked(True)
                self.actionEnglish.setChecked(False)
            else:
                self.actionEnglish.setChecked(True)
                self.actionFrench.setChecked(False)
        
        # Update tab widget
        self.ui.tabWidget.setTabText(0, _("MAIN_TAB"))  # Need to add MAIN_TAB to translations
        self.ui.tabWidget.setTabText(1, _("ADVANCED_TAB"))
        
        # Update Simulator Settings group
        self.ui.groupBoxSimulator.setTitle(_("SIMULATOR_SETTINGS"))
        self.ui.labelSimulatorType.setText(_("SIMULATOR_TYPE"))
        self.ui.labelHost.setText(_("HOST"))
        self.ui.lineEditHost.setPlaceholderText(_("HOST_PLACEHOLDER"))
        self.ui.labelPort.setText(_("PORT"))
        self.ui.labelPollInterval.setText(_("POLL_INTERVAL"))
        
        # Update Output Settings group
        self.ui.groupBoxOutput.setTitle(_("OUTPUT_SETTINGS"))
        self.ui.labelOutputFile.setText(_("OUTPUT_FILE"))
        self.ui.lineEditOutputFile.setPlaceholderText(_("OUTPUT_FILE_PLACEHOLDER"))
        self.ui.pushButtonBrowse.setText(_("BROWSE_BUTTON"))
        
        # Update Controls group
        self.ui.groupBoxControls.setTitle(_("CONTROLS"))
        self.ui.pushButtonConnect.setText(_("CONNECT_BUTTON"))
        self.ui.pushButtonDisconnect.setText(_("DISCONNECT_BUTTON"))
        self.ui.pushButtonStart.setText(_("START_MONITORING"))
        self.ui.pushButtonStop.setText(_("STOP_MONITORING"))
        
        # Update Status group
        self.ui.groupBoxStatus.setTitle(_("STATUS"))
        self.ui.labelConnectionStatusTitle.setText(_("CONNECTION"))
        self.ui.labelFlightStatusTitle.setText(_("FLIGHT_STATE"))
        self.ui.labelMonitoringStatusTitle.setText(_("MONITORING"))
        
        # Update Advanced tab
        self.ui.groupBoxAircraft.setTitle(_("AIRCRAFT_INFORMATION"))
        self.ui.labelAircraftICAO.setText(_("ICAO_CODE"))
        self.ui.labelAircraftName.setText(_("AIRCRAFT_NAME"))
        
        self.ui.groupBoxData.setTitle(_("LIVE_DATA"))
        self.ui.labelLatitude.setText(_("LATITUDE"))
        self.ui.labelLongitude.setText(_("LONGITUDE"))
        self.ui.labelAltitude.setText(_("ALTITUDE_MSL"))
        self.ui.labelAGL.setText(_("ALTITUDE_AGL"))
        self.ui.labelHeading.setText(_("HEADING_TRUE"))
        self.ui.labelHeadingMag.setText(_("HEADING_MAG"))
        self.ui.labelGroundSpeed.setText(_("GROUND_SPEED"))
        self.ui.labelIndicatedSpeed.setText(_("INDICATED_SPEED"))
        self.ui.labelPower.setText(_("POWER"))
        self.ui.labelSimTime.setText(_("SIMULATION_TIME"))
        
        # Update static text values
        self._update_static_text()
        
        # Update status bar
        self.statusBar().showMessage(_("LOG_STARTUP"))
    
    def _update_static_text(self):
        """Update static text elements that need translation."""
        # Update N/A values in data display
        na_text = _("N_A")
        for widget_name in ['labelAircraftICAOValue', 'labelAircraftNameValue',
                            'labelLatitudeValue', 'labelLongitudeValue',
                            'labelAltitudeValue', 'labelAGLValue',
                            'labelHeadingValue', 'labelHeadingMagValue',
                            'labelGroundSpeedValue',
                            'labelIndicatedSpeedValue', 'labelPowerValue',
                            'labelSimTimeValue']:
            widget = getattr(self.ui, widget_name, None)
            if widget and widget.text() == "N/A":
                widget.setText(na_text)
        
        # Update initial log message
        self.ui.textBrowserLog.clear()
        self.log_message(_("LOG_STARTUP"))
    
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
            # Start Monitoring button enabled only if connected and not already running
            self.ui.pushButtonStart.setEnabled(
                not self.monitor._running and 
                self.monitor.is_connected and
                bool(self.ui.lineEditOutputFile.text().strip())
            )
            self.ui.pushButtonStop.setEnabled(self.monitor._running)
        else:
            self.ui.pushButtonConnect.setEnabled(True)
            self.ui.pushButtonDisconnect.setEnabled(False)
            # No monitor = cannot start monitoring (need connection first)
            self.ui.pushButtonStart.setEnabled(False)
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
            _("SELECT_OUTPUT_FILE"),
            self._get_output_file() or os.path.expanduser("~"),
            _("FILE_FILTER_GEOJSON")
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
        include_trajectory = True  # Always include trajectory line
        
        if not output_file:
            self.log_message(_("ERROR_NO_OUTPUT_FILE"))
            QMessageBox.warning(self, _("ERROR_NO_OUTPUT_FILE"), _("ERROR_SPECIFY_OUTPUT_FILE"))
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
            
            # NOTE: We no longer use set_connection_callback to avoid Qt thread issues.
            # The monitor now uses a thread-safe queue for status messages, and we
            # process them in the UI thread via _process_status_messages() method called
            # by the status_timer. This prevents "QObject: Cannot create children for a
            # parent that is in a different thread" errors.
            
            self.monitor = monitor
            self.log_message(_("MONITOR_CREATED", sim_type=sim_type))
            
            return monitor
            
        except Exception as e:
            self.log_message(_("ERROR_CREATING_MONITOR", error=str(e)))
            QMessageBox.critical(self, _("ERROR_NO_OUTPUT_FILE"), _("FAILED_CREATE_MONITOR", error=str(e)))
            return None
    
    def _process_status_messages(self):
        """Process status messages from monitor queue in UI thread."""
        if not self.monitor:
            return
        
        # Get all pending status messages from the monitor's thread-safe queue
        messages = self.monitor.get_status_messages()
        
        for is_connected, message in messages:
            # Update connection status label
            if is_connected:
                self.ui.labelConnectionStatus.setText(_("CONNECTION_CONNECTED"))
                palette = self.ui.labelConnectionStatus.palette()
                palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
            else:
                self.ui.labelConnectionStatus.setText(_("CONNECTION_DISCONNECTED"))
                palette = self.ui.labelConnectionStatus.palette()
                palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
            self.ui.labelConnectionStatus.setPalette(palette)
            
            # Log message
            self.log_message(message)
            
            # Update button states
            self._update_ui_state()
    
    def cleanup_monitor(self):
        """Clean up existing monitor and poller."""
        # Stop status timer
        if hasattr(self, 'status_timer') and self.status_timer:
            self.status_timer.stop()
            self.status_timer = None
        
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
    
    # NOTE: This method is no longer used. Connection status is now handled via
    # _process_status_messages() which processes messages from the thread-safe queue.
    # Keeping it here for reference but it's not connected to anything.
    # def on_connection_status_changed(self, connected, message):
    #     """Callback for monitor connection status changes."""
    #     # Update connection status label
    #     self.ui.labelConnectionStatus.setText(_("CONNECTION_CONNECTED") if connected else _("CONNECTION_DISCONNECTED"))
    #     
    #     # Set color
    #     palette = self.ui.labelConnectionStatus.palette()
    #     if connected:
    #         palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
    #     else:
    #         palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
    #     self.ui.labelConnectionStatus.setPalette(palette)
    #     
    #     # Log message
    #     self.log_message(message)
    #     
    #     # Update button states
    #     self._update_ui_state()
    
    def on_connect(self):
        """Handle Connect button click."""
        # Always recreate monitor with current settings to pick up any changes
        # (host, port, output file, etc.)
        self.create_monitor_instance()
        
        if not self.monitor:
            return
        
        try:
            success = self.monitor.connect()
            if success:
                self.log_message(_("CONNECTED_SUCCESS"))
                self._update_ui_state()
                
                # Start polling live data
                self.start_polling()
            else:
                # Get error ID and args, then format using GUI translations
                error_id = self.monitor.get_last_error_id()
                error_args = self.monitor.get_last_error_args() or {}
                if error_id:
                    # Use GUI translation
                    error_msg = _(error_id, **error_args)
                else:
                    error_msg = _("CONNECT_FAILED")
                self.log_message(error_msg)
                QMessageBox.warning(self, _("CONNECTION_FAILED"), error_msg)
        except Exception as e:
            self.log_message(_("CONNECTION_ERROR", error=str(e)))
            QMessageBox.critical(self, _("CONNECTION_ERROR"), str(e))
    
    def on_disconnect(self):
        """Handle Disconnect button click."""
        if self.monitor:
            try:
                self.monitor.disconnect()
                self.log_message(_("DISCONNECTED_SUCCESS"))
            except Exception as e:
                self.log_message(_("DISCONNECT_ERROR", error=str(e)))
        
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
            QMessageBox.warning(self, _("ERROR_NO_OUTPUT_FILE"), _("ERROR_SPECIFY_OUTPUT_FILE"))
            return
        
        # Check if we need to recreate monitor with new settings
        if self.monitor.geojson_writer.filepath != output_file:
            self.log_message(_("OUTPUT_CHANGED"))
            self.create_monitor_instance()
        
        if not self.monitor:
            return
        
        try:
            # Auto-connect has been removed - manual connection is now required
            # Check if we are connected
            if not self.monitor.is_connected:
                QMessageBox.warning(self, _("NOT_CONNECTED"), _("CONNECT_FIRST"))
                return
            
            # Start monitoring
            self.monitor.start_monitoring()
            self.log_message(_("MONITORING_STARTED"))
            
            # Start polling
            self.start_polling()
            
            self._update_ui_state()
            
        except Exception as e:
            self.log_message(_("ERROR_STARTING_MONITORING", error=str(e)))
            QMessageBox.critical(self, _("ERROR_STARTING_MONITORING"), _("FAILED_START_MONITORING", error=str(e)))
    
    def on_stop_monitoring(self):
        """Handle Stop Monitoring button click."""
        if self.monitor and self.monitor._running:
            try:
                self.monitor.stop_monitoring()
                self.log_message(_("MONITORING_STOPPED"))
            except Exception as e:
                self.log_message(_("ERROR_STOPPING_MONITORING", error=str(e)))
        
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
            
            # Start polling at a reasonable interval (minimum 1 second)
            poll_interval_ms = int(self._get_poll_interval() * 1000)
            self.poller.start(max(poll_interval_ms, 1000))  # Minimum 1000ms (1 second)
    
    def on_data_updated(self, data):
        """Handle new data from the simulator."""
        try:
            na_text = _("N_A")
            
            # Update aircraft info
            if 'acf_icao' in data:
                self.ui.labelAircraftICAOValue.setText(str(data.get('acf_icao', na_text)))
            if 'acf_name' in data:
                self.ui.labelAircraftNameValue.setText(str(data.get('acf_name', na_text)))
            
            # Update flight data
            if 'latitude' in data:
                self.ui.labelLatitudeValue.setText(str(data.get('latitude', na_text)))
            if 'longitude' in data:
                self.ui.labelLongitudeValue.setText(str(data.get('longitude', na_text)))
            if 'alt_msl' in data:
                self.ui.labelAltitudeValue.setText(str(data.get('alt_msl', na_text)))
            if 'alt_agl' in data:
                self.ui.labelAGLValue.setText(str(data.get('alt_agl', na_text)))
            if 'heading_true' in data:
                self.ui.labelHeadingValue.setText(str(data.get('heading_true', na_text)))
            if 'heading_mag' in data:
                self.ui.labelHeadingMagValue.setText(str(data.get('heading_mag', na_text)))
            if 'gs' in data:
                self.ui.labelGroundSpeedValue.setText(str(data.get('gs', na_text)))
            if 'ias' in data:
                self.ui.labelIndicatedSpeedValue.setText(str(data.get('ias', na_text)))
            if 'power' in data:
                self.ui.labelPowerValue.setText(str(data.get('power', na_text)))
            if 'sim_time' in data:
                self.ui.labelSimTimeValue.setText(str(data.get('sim_time', na_text)))
                
        except Exception as e:
            self.log_message(_("ERROR_UPDATING_DATA", error=str(e)))
    
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
        
        # Set color based on state (using translated strings)
        palette = self.ui.labelFlightStatus.palette()
        if state_str == _("FLIGHT_STATE_IN_FLIGHT"):
            palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
        elif state_str == _("FLIGHT_STATE_LANDED"):
            palette.setColor(QPalette.ColorRole.WindowText, QColor("orange"))
        else:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("blue"))
        self.ui.labelFlightStatus.setPalette(palette)
    
    def on_poller_monitoring_state_changed(self, state_str):
        """Handle monitoring state updates from poller."""
        self.ui.labelMonitoringStatus.setText(state_str)
        palette = self.ui.labelMonitoringStatus.palette()
        if state_str == _("MONITORING_RUNNING"):
            palette.setColor(QPalette.ColorRole.WindowText, QColor("green"))
        else:
            palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
        self.ui.labelMonitoringStatus.setPalette(palette)
        self._update_ui_state()
    
    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        <h2>{_("FLIGHT_DATA_RECORDER_TITLE")}</h2>
        <p>{_("ABOUT_VERSION")}</p>
        <p>{_("ABOUT_DESCRIPTION")}</p>
        <p>{_("ABOUT_SUPPORTED_SIMULATORS")}</p>
        <ul>
            <li>{_("ABOUT_SIMULATOR_XPLANE")}</li>
            <li>{_("ABOUT_SIMULATOR_MSFS")}</li>
            <li>{_("ABOUT_SIMULATOR_P3D")}</li>
        </ul>
        <p>{_("ABOUT_LICENSE")}</p>
        <p>{_("ABOUT_AUTHOR")}</p>
        """
        QMessageBox.about(self, _("ABOUT_TITLE"), about_text)
    
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
    app.setApplicationName(_("FLIGHT_DATA_RECORDER_TITLE"))
    app.setOrganizationName("AirRallies")
    app.setApplicationVersion(_("ABOUT_VERSION"))
    
    # Load icon
    icon = QIcon(":/icons/icon.png")
    if icon.isNull():
        icon_file = os.path.join(os.path.dirname(__file__), "ui", "icons", "icon.png")
        if os.path.exists(icon_file):
            icon = QIcon(icon_file)
    
    # Create and show main window
    window = MainWindow()
    
    # Set icon on both app and window
    if not icon.isNull():
        app.setWindowIcon(icon)
        window.setWindowIcon(icon)
    
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
