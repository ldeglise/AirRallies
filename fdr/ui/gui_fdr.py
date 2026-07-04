# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gui_fdr.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStatusBar, QTabWidget,
    QTextBrowser, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 700)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabMain = QWidget()
        self.tabMain.setObjectName(u"tabMain")
        self.verticalLayout_2 = QVBoxLayout(self.tabMain)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.groupBoxSimulator = QGroupBox(self.tabMain)
        self.groupBoxSimulator.setObjectName(u"groupBoxSimulator")
        self.formLayoutSimulator = QFormLayout(self.groupBoxSimulator)
        self.formLayoutSimulator.setObjectName(u"formLayoutSimulator")
        self.labelSimulatorType = QLabel(self.groupBoxSimulator)
        self.labelSimulatorType.setObjectName(u"labelSimulatorType")

        self.formLayoutSimulator.setWidget(0, QFormLayout.LabelRole, self.labelSimulatorType)

        self.comboSimulatorType = QComboBox(self.groupBoxSimulator)
        self.comboSimulatorType.addItem("")
        self.comboSimulatorType.addItem("")
        self.comboSimulatorType.setObjectName(u"comboSimulatorType")

        self.formLayoutSimulator.setWidget(0, QFormLayout.FieldRole, self.comboSimulatorType)

        self.labelHost = QLabel(self.groupBoxSimulator)
        self.labelHost.setObjectName(u"labelHost")

        self.formLayoutSimulator.setWidget(1, QFormLayout.LabelRole, self.labelHost)

        self.lineEditHost = QLineEdit(self.groupBoxSimulator)
        self.lineEditHost.setObjectName(u"lineEditHost")

        self.formLayoutSimulator.setWidget(1, QFormLayout.FieldRole, self.lineEditHost)

        self.labelPort = QLabel(self.groupBoxSimulator)
        self.labelPort.setObjectName(u"labelPort")

        self.formLayoutSimulator.setWidget(2, QFormLayout.LabelRole, self.labelPort)

        self.spinBoxPort = QSpinBox(self.groupBoxSimulator)
        self.spinBoxPort.setObjectName(u"spinBoxPort")
        self.spinBoxPort.setMinimum(1)
        self.spinBoxPort.setMaximum(65535)
        self.spinBoxPort.setValue(8086)

        self.formLayoutSimulator.setWidget(2, QFormLayout.FieldRole, self.spinBoxPort)

        self.labelPollInterval = QLabel(self.groupBoxSimulator)
        self.labelPollInterval.setObjectName(u"labelPollInterval")

        self.formLayoutSimulator.setWidget(3, QFormLayout.LabelRole, self.labelPollInterval)

        self.spinBoxPollInterval = QDoubleSpinBox(self.groupBoxSimulator)
        self.spinBoxPollInterval.setObjectName(u"spinBoxPollInterval")
        self.spinBoxPollInterval.setDecimals(1)
        self.spinBoxPollInterval.setMinimum(1.0)
        self.spinBoxPollInterval.setMaximum(10.0)
        self.spinBoxPollInterval.setSingleStep(0.5)
        self.spinBoxPollInterval.setValue(1.0)

        self.formLayoutSimulator.setWidget(3, QFormLayout.FieldRole, self.spinBoxPollInterval)


        self.horizontalLayout_4.addWidget(self.groupBoxSimulator)

        self.groupBoxOutput = QGroupBox(self.tabMain)
        self.groupBoxOutput.setObjectName(u"groupBoxOutput")
        self.formLayoutOutput = QFormLayout(self.groupBoxOutput)
        self.formLayoutOutput.setObjectName(u"formLayoutOutput")
        self.labelOutputFile = QLabel(self.groupBoxOutput)
        self.labelOutputFile.setObjectName(u"labelOutputFile")

        self.formLayoutOutput.setWidget(0, QFormLayout.SpanningRole, self.labelOutputFile)

        self.horizontalLayoutOutputFile = QHBoxLayout()
        self.horizontalLayoutOutputFile.setObjectName(u"horizontalLayoutOutputFile")
        self.lineEditOutputFile = QLineEdit(self.groupBoxOutput)
        self.lineEditOutputFile.setObjectName(u"lineEditOutputFile")

        self.horizontalLayoutOutputFile.addWidget(self.lineEditOutputFile)

        self.pushButtonBrowse = QPushButton(self.groupBoxOutput)
        self.pushButtonBrowse.setObjectName(u"pushButtonBrowse")
        self.pushButtonBrowse.setMaximumWidth(100)

        self.horizontalLayoutOutputFile.addWidget(self.pushButtonBrowse)


        self.formLayoutOutput.setLayout(1, QFormLayout.SpanningRole, self.horizontalLayoutOutputFile)

        self.checkBoxIncludeTrajectory = QCheckBox(self.groupBoxOutput)
        self.checkBoxIncludeTrajectory.setObjectName(u"checkBoxIncludeTrajectory")
        self.checkBoxIncludeTrajectory.setChecked(True)

        self.formLayoutOutput.setWidget(2, QFormLayout.LabelRole, self.checkBoxIncludeTrajectory)

        self.checkBoxAutoConnect = QCheckBox(self.groupBoxOutput)
        self.checkBoxAutoConnect.setObjectName(u"checkBoxAutoConnect")
        self.checkBoxAutoConnect.setChecked(True)

        self.formLayoutOutput.setWidget(3, QFormLayout.LabelRole, self.checkBoxAutoConnect)


        self.horizontalLayout_4.addWidget(self.groupBoxOutput)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.groupBoxControls = QGroupBox(self.tabMain)
        self.groupBoxControls.setObjectName(u"groupBoxControls")
        self.horizontalLayoutControls = QHBoxLayout(self.groupBoxControls)
        self.horizontalLayoutControls.setObjectName(u"horizontalLayoutControls")
        self.horizontalSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutControls.addItem(self.horizontalSpacerLeft)

        self.pushButtonConnect = QPushButton(self.groupBoxControls)
        self.pushButtonConnect.setObjectName(u"pushButtonConnect")
        self.pushButtonConnect.setMinimumWidth(120)

        self.horizontalLayoutControls.addWidget(self.pushButtonConnect)

        self.pushButtonDisconnect = QPushButton(self.groupBoxControls)
        self.pushButtonDisconnect.setObjectName(u"pushButtonDisconnect")
        self.pushButtonDisconnect.setMinimumWidth(120)

        self.horizontalLayoutControls.addWidget(self.pushButtonDisconnect)

        self.pushButtonStart = QPushButton(self.groupBoxControls)
        self.pushButtonStart.setObjectName(u"pushButtonStart")
        self.pushButtonStart.setMinimumWidth(150)

        self.horizontalLayoutControls.addWidget(self.pushButtonStart)

        self.pushButtonStop = QPushButton(self.groupBoxControls)
        self.pushButtonStop.setObjectName(u"pushButtonStop")
        self.pushButtonStop.setMinimumWidth(150)

        self.horizontalLayoutControls.addWidget(self.pushButtonStop)

        self.horizontalSpacerRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutControls.addItem(self.horizontalSpacerRight)


        self.verticalLayout_2.addWidget(self.groupBoxControls)

        self.groupBoxStatus = QGroupBox(self.tabMain)
        self.groupBoxStatus.setObjectName(u"groupBoxStatus")
        self.verticalLayoutStatus = QVBoxLayout(self.groupBoxStatus)
        self.verticalLayoutStatus.setObjectName(u"verticalLayoutStatus")
        self.horizontalLayoutStatus = QHBoxLayout()
        self.horizontalLayoutStatus.setObjectName(u"horizontalLayoutStatus")
        self.labelConnectionStatusTitle = QLabel(self.groupBoxStatus)
        self.labelConnectionStatusTitle.setObjectName(u"labelConnectionStatusTitle")
        self.labelConnectionStatusTitle.setMinimumWidth(100)

        self.horizontalLayoutStatus.addWidget(self.labelConnectionStatusTitle)

        self.labelConnectionStatus = QLabel(self.groupBoxStatus)
        self.labelConnectionStatus.setObjectName(u"labelConnectionStatus")
        self.labelConnectionStatus.setFrameShape(QFrame.Panel)
        self.labelConnectionStatus.setFrameShadow(QFrame.Sunken)
        self.labelConnectionStatus.setAlignment(Qt.AlignCenter)
        self.labelConnectionStatus.setMinimumWidth(150)

        self.horizontalLayoutStatus.addWidget(self.labelConnectionStatus)

        self.labelFlightStatusTitle = QLabel(self.groupBoxStatus)
        self.labelFlightStatusTitle.setObjectName(u"labelFlightStatusTitle")
        self.labelFlightStatusTitle.setMinimumWidth(100)

        self.horizontalLayoutStatus.addWidget(self.labelFlightStatusTitle)

        self.labelFlightStatus = QLabel(self.groupBoxStatus)
        self.labelFlightStatus.setObjectName(u"labelFlightStatus")
        self.labelFlightStatus.setFrameShape(QFrame.Panel)
        self.labelFlightStatus.setFrameShadow(QFrame.Sunken)
        self.labelFlightStatus.setAlignment(Qt.AlignCenter)
        self.labelFlightStatus.setMinimumWidth(150)

        self.horizontalLayoutStatus.addWidget(self.labelFlightStatus)

        self.labelMonitoringStatusTitle = QLabel(self.groupBoxStatus)
        self.labelMonitoringStatusTitle.setObjectName(u"labelMonitoringStatusTitle")
        self.labelMonitoringStatusTitle.setMinimumWidth(100)

        self.horizontalLayoutStatus.addWidget(self.labelMonitoringStatusTitle)

        self.labelMonitoringStatus = QLabel(self.groupBoxStatus)
        self.labelMonitoringStatus.setObjectName(u"labelMonitoringStatus")
        self.labelMonitoringStatus.setFrameShape(QFrame.Panel)
        self.labelMonitoringStatus.setFrameShadow(QFrame.Sunken)
        self.labelMonitoringStatus.setAlignment(Qt.AlignCenter)
        self.labelMonitoringStatus.setMinimumWidth(150)

        self.horizontalLayoutStatus.addWidget(self.labelMonitoringStatus)


        self.verticalLayoutStatus.addLayout(self.horizontalLayoutStatus)

        self.textBrowserLog = QTextBrowser(self.groupBoxStatus)
        self.textBrowserLog.setObjectName(u"textBrowserLog")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.textBrowserLog.sizePolicy().hasHeightForWidth())
        self.textBrowserLog.setSizePolicy(sizePolicy)
        self.textBrowserLog.setMinimumHeight(100)
        self.textBrowserLog.setMaximumHeight(200)
        self.textBrowserLog.setFrameShape(QFrame.StyledPanel)
        self.textBrowserLog.setFrameShadow(QFrame.Sunken)
        self.textBrowserLog.setReadOnly(True)

        self.verticalLayoutStatus.addWidget(self.textBrowserLog)


        self.verticalLayout_2.addWidget(self.groupBoxStatus)

        self.tabWidget.addTab(self.tabMain, "")
        self.tabAdvanced = QWidget()
        self.tabAdvanced.setObjectName(u"tabAdvanced")
        self.verticalLayout_3 = QVBoxLayout(self.tabAdvanced)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBoxAircraft = QGroupBox(self.tabAdvanced)
        self.groupBoxAircraft.setObjectName(u"groupBoxAircraft")
        self.formLayoutAircraft = QFormLayout(self.groupBoxAircraft)
        self.formLayoutAircraft.setObjectName(u"formLayoutAircraft")
        self.labelAircraftICAO = QLabel(self.groupBoxAircraft)
        self.labelAircraftICAO.setObjectName(u"labelAircraftICAO")

        self.formLayoutAircraft.setWidget(0, QFormLayout.LabelRole, self.labelAircraftICAO)

        self.labelAircraftICAOValue = QLabel(self.groupBoxAircraft)
        self.labelAircraftICAOValue.setObjectName(u"labelAircraftICAOValue")
        self.labelAircraftICAOValue.setFrameShape(QFrame.Panel)
        self.labelAircraftICAOValue.setFrameShadow(QFrame.Sunken)

        self.formLayoutAircraft.setWidget(0, QFormLayout.FieldRole, self.labelAircraftICAOValue)

        self.labelAircraftName = QLabel(self.groupBoxAircraft)
        self.labelAircraftName.setObjectName(u"labelAircraftName")

        self.formLayoutAircraft.setWidget(1, QFormLayout.LabelRole, self.labelAircraftName)

        self.labelAircraftNameValue = QLabel(self.groupBoxAircraft)
        self.labelAircraftNameValue.setObjectName(u"labelAircraftNameValue")
        self.labelAircraftNameValue.setFrameShape(QFrame.Panel)
        self.labelAircraftNameValue.setFrameShadow(QFrame.Sunken)

        self.formLayoutAircraft.setWidget(1, QFormLayout.FieldRole, self.labelAircraftNameValue)


        self.verticalLayout_3.addWidget(self.groupBoxAircraft)

        self.groupBoxData = QGroupBox(self.tabAdvanced)
        self.groupBoxData.setObjectName(u"groupBoxData")
        self.gridLayoutData = QGridLayout(self.groupBoxData)
        self.gridLayoutData.setObjectName(u"gridLayoutData")
        self.labelLatitude = QLabel(self.groupBoxData)
        self.labelLatitude.setObjectName(u"labelLatitude")

        self.gridLayoutData.addWidget(self.labelLatitude, 0, 0, 1, 1)

        self.labelLatitudeValue = QLabel(self.groupBoxData)
        self.labelLatitudeValue.setObjectName(u"labelLatitudeValue")
        self.labelLatitudeValue.setFrameShape(QFrame.Panel)
        self.labelLatitudeValue.setFrameShadow(QFrame.Sunken)
        self.labelLatitudeValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelLatitudeValue, 0, 1, 1, 1)

        self.labelLongitude = QLabel(self.groupBoxData)
        self.labelLongitude.setObjectName(u"labelLongitude")

        self.gridLayoutData.addWidget(self.labelLongitude, 0, 2, 1, 1)

        self.labelLongitudeValue = QLabel(self.groupBoxData)
        self.labelLongitudeValue.setObjectName(u"labelLongitudeValue")
        self.labelLongitudeValue.setFrameShape(QFrame.Panel)
        self.labelLongitudeValue.setFrameShadow(QFrame.Sunken)
        self.labelLongitudeValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelLongitudeValue, 0, 3, 1, 1)

        self.labelAltitude = QLabel(self.groupBoxData)
        self.labelAltitude.setObjectName(u"labelAltitude")

        self.gridLayoutData.addWidget(self.labelAltitude, 1, 0, 1, 1)

        self.labelAltitudeValue = QLabel(self.groupBoxData)
        self.labelAltitudeValue.setObjectName(u"labelAltitudeValue")
        self.labelAltitudeValue.setFrameShape(QFrame.Panel)
        self.labelAltitudeValue.setFrameShadow(QFrame.Sunken)
        self.labelAltitudeValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelAltitudeValue, 1, 1, 1, 1)

        self.labelAGL = QLabel(self.groupBoxData)
        self.labelAGL.setObjectName(u"labelAGL")

        self.gridLayoutData.addWidget(self.labelAGL, 1, 2, 1, 1)

        self.labelAGLValue = QLabel(self.groupBoxData)
        self.labelAGLValue.setObjectName(u"labelAGLValue")
        self.labelAGLValue.setFrameShape(QFrame.Panel)
        self.labelAGLValue.setFrameShadow(QFrame.Sunken)
        self.labelAGLValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelAGLValue, 1, 3, 1, 1)

        self.labelHeading = QLabel(self.groupBoxData)
        self.labelHeading.setObjectName(u"labelHeading")

        self.gridLayoutData.addWidget(self.labelHeading, 2, 0, 1, 1)

        self.labelHeadingValue = QLabel(self.groupBoxData)
        self.labelHeadingValue.setObjectName(u"labelHeadingValue")
        self.labelHeadingValue.setFrameShape(QFrame.Panel)
        self.labelHeadingValue.setFrameShadow(QFrame.Sunken)
        self.labelHeadingValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelHeadingValue, 2, 1, 1, 1)

        self.labelGroundSpeed = QLabel(self.groupBoxData)
        self.labelGroundSpeed.setObjectName(u"labelGroundSpeed")

        self.gridLayoutData.addWidget(self.labelGroundSpeed, 2, 2, 1, 1)

        self.labelGroundSpeedValue = QLabel(self.groupBoxData)
        self.labelGroundSpeedValue.setObjectName(u"labelGroundSpeedValue")
        self.labelGroundSpeedValue.setFrameShape(QFrame.Panel)
        self.labelGroundSpeedValue.setFrameShadow(QFrame.Sunken)
        self.labelGroundSpeedValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelGroundSpeedValue, 2, 3, 1, 1)

        self.labelIndicatedSpeed = QLabel(self.groupBoxData)
        self.labelIndicatedSpeed.setObjectName(u"labelIndicatedSpeed")

        self.gridLayoutData.addWidget(self.labelIndicatedSpeed, 3, 0, 1, 1)

        self.labelIndicatedSpeedValue = QLabel(self.groupBoxData)
        self.labelIndicatedSpeedValue.setObjectName(u"labelIndicatedSpeedValue")
        self.labelIndicatedSpeedValue.setFrameShape(QFrame.Panel)
        self.labelIndicatedSpeedValue.setFrameShadow(QFrame.Sunken)
        self.labelIndicatedSpeedValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelIndicatedSpeedValue, 3, 1, 1, 1)

        self.labelPower = QLabel(self.groupBoxData)
        self.labelPower.setObjectName(u"labelPower")

        self.gridLayoutData.addWidget(self.labelPower, 3, 2, 1, 1)

        self.labelPowerValue = QLabel(self.groupBoxData)
        self.labelPowerValue.setObjectName(u"labelPowerValue")
        self.labelPowerValue.setFrameShape(QFrame.Panel)
        self.labelPowerValue.setFrameShadow(QFrame.Sunken)
        self.labelPowerValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelPowerValue, 3, 3, 1, 1)

        self.labelSimTime = QLabel(self.groupBoxData)
        self.labelSimTime.setObjectName(u"labelSimTime")

        self.gridLayoutData.addWidget(self.labelSimTime, 4, 0, 1, 1)

        self.labelSimTimeValue = QLabel(self.groupBoxData)
        self.labelSimTimeValue.setObjectName(u"labelSimTimeValue")
        self.labelSimTimeValue.setFrameShape(QFrame.Panel)
        self.labelSimTimeValue.setFrameShadow(QFrame.Sunken)
        self.labelSimTimeValue.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayoutData.addWidget(self.labelSimTimeValue, 4, 1, 1, 3)


        self.verticalLayout_3.addWidget(self.groupBoxData)

        self.verticalSpacerAdvanced = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacerAdvanced)

        self.tabWidget.addTab(self.tabAdvanced, "")

        self.verticalLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 24))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setSizeGripEnabled(True)
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)
        self.actionExit.triggered.connect(MainWindow.close)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Flight Data Recorder", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.groupBoxSimulator.setTitle(QCoreApplication.translate("MainWindow", u"Simulator Settings", None))
        self.labelSimulatorType.setText(QCoreApplication.translate("MainWindow", u"Simulator Type:", None))
        self.comboSimulatorType.setItemText(0, QCoreApplication.translate("MainWindow", u"X-Plane 12", None))
        self.comboSimulatorType.setItemText(1, QCoreApplication.translate("MainWindow", u"MSFS 2020/2024 / P3D", None))

        self.labelHost.setText(QCoreApplication.translate("MainWindow", u"Host:", None))
        self.lineEditHost.setText(QCoreApplication.translate("MainWindow", u"127.0.0.1", None))
        self.lineEditHost.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter IP address", None))
        self.labelPort.setText(QCoreApplication.translate("MainWindow", u"Port:", None))
        self.spinBoxPort.setPrefix("")
        self.spinBoxPort.setSuffix("")
        self.labelPollInterval.setText(QCoreApplication.translate("MainWindow", u"Poll Interval (s):", None))
        self.groupBoxOutput.setTitle(QCoreApplication.translate("MainWindow", u"Output Settings", None))
        self.labelOutputFile.setText(QCoreApplication.translate("MainWindow", u"Output File:", None))
        self.lineEditOutputFile.setText("")
        self.lineEditOutputFile.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Select output file path...", None))
        self.pushButtonBrowse.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.checkBoxIncludeTrajectory.setText(QCoreApplication.translate("MainWindow", u"Include Trajectory Line", None))
#if QT_CONFIG(tooltip)
        self.checkBoxIncludeTrajectory.setToolTip(QCoreApplication.translate("MainWindow", u"Add a LineString feature for trajectory visualization in QGIS", None))
#endif // QT_CONFIG(tooltip)
        self.checkBoxAutoConnect.setText(QCoreApplication.translate("MainWindow", u"Auto-connect on Start", None))
#if QT_CONFIG(tooltip)
        self.checkBoxAutoConnect.setToolTip(QCoreApplication.translate("MainWindow", u"Automatically connect to simulator when monitoring starts", None))
#endif // QT_CONFIG(tooltip)
        self.groupBoxControls.setTitle(QCoreApplication.translate("MainWindow", u"Controls", None))
        self.pushButtonConnect.setText(QCoreApplication.translate("MainWindow", u"Connect", None))
        self.pushButtonDisconnect.setText(QCoreApplication.translate("MainWindow", u"Disconnect", None))
        self.pushButtonStart.setText(QCoreApplication.translate("MainWindow", u"Start Monitoring", None))
        self.pushButtonStop.setText(QCoreApplication.translate("MainWindow", u"Stop Monitoring", None))
        self.groupBoxStatus.setTitle(QCoreApplication.translate("MainWindow", u"Status", None))
        self.labelConnectionStatusTitle.setText(QCoreApplication.translate("MainWindow", u"Connection:", None))
        self.labelConnectionStatus.setText(QCoreApplication.translate("MainWindow", u"Disconnected", None))
        self.labelFlightStatusTitle.setText(QCoreApplication.translate("MainWindow", u"Flight State:", None))
        self.labelFlightStatus.setText(QCoreApplication.translate("MainWindow", u"Waiting", None))
        self.labelMonitoringStatusTitle.setText(QCoreApplication.translate("MainWindow", u"Monitoring:", None))
        self.labelMonitoringStatus.setText(QCoreApplication.translate("MainWindow", u"Stopped", None))
        self.textBrowserLog.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Application started. Ready for monitoring.</p>\n"
"</body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMain), QCoreApplication.translate("MainWindow", u"Main", None))
        self.groupBoxAircraft.setTitle(QCoreApplication.translate("MainWindow", u"Aircraft Information", None))
        self.labelAircraftICAO.setText(QCoreApplication.translate("MainWindow", u"ICAO Code:", None))
        self.labelAircraftICAOValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelAircraftName.setText(QCoreApplication.translate("MainWindow", u"Aircraft Name:", None))
        self.labelAircraftNameValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.groupBoxData.setTitle(QCoreApplication.translate("MainWindow", u"Live Data", None))
        self.labelLatitude.setText(QCoreApplication.translate("MainWindow", u"Latitude:", None))
        self.labelLatitudeValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelLongitude.setText(QCoreApplication.translate("MainWindow", u"Longitude:", None))
        self.labelLongitudeValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelAltitude.setText(QCoreApplication.translate("MainWindow", u"Altitude (MSL):", None))
        self.labelAltitudeValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelAGL.setText(QCoreApplication.translate("MainWindow", u"Altitude (AGL):", None))
        self.labelAGLValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelHeading.setText(QCoreApplication.translate("MainWindow", u"Heading:", None))
        self.labelHeadingValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelGroundSpeed.setText(QCoreApplication.translate("MainWindow", u"Ground Speed:", None))
        self.labelGroundSpeedValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelIndicatedSpeed.setText(QCoreApplication.translate("MainWindow", u"Indicated Speed:", None))
        self.labelIndicatedSpeedValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelPower.setText(QCoreApplication.translate("MainWindow", u"Power:", None))
        self.labelPowerValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.labelSimTime.setText(QCoreApplication.translate("MainWindow", u"Simulation Time:", None))
        self.labelSimTimeValue.setText(QCoreApplication.translate("MainWindow", u"N/A", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAdvanced), QCoreApplication.translate("MainWindow", u"Advanced", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

