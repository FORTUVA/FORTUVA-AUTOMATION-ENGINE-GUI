# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
import os

import icons_rc  # pylint: disable=unused-import
from bot.worker import BotWorker, BotConfig

# Import for system notifications
try:
    from plyer import notification as system_notification
    SYSTEM_NOTIFICATIONS_AVAILABLE = True
except ImportError:
    SYSTEM_NOTIFICATIONS_AVAILABLE = False
    print("Warning: plyer not installed. System notifications disabled.")



# TODO: Improve readability


class FortuvaForm(QtWidgets.QWidget):
    """Basic login form.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._drag_active = False
        self._drag_pos = QtCore.QPoint()
        self.setup_ui()

    def setup_ui(self):
        """Setup the login form.
        """
        self.resize(1380, 825)  # Main panel (500px) + Round card (380px) + Log panel (500px)
        # remove the title bar
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "icons", "fortuva.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        self.setStyleSheet(
            """
            QWidget#Form {
                background-color: rgb(12, 12, 24);
            }
            QPushButton {
                border-style: outset;
                border-radius: 0px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #cf7500;
                border-style: inset;
            }
            QPushButton:pressed {
                background-color: #ffa126;
                border-style: inset;
            }
            """
        )
        self.setObjectName("Form")

        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # Notification area at the top
        self.notificationWidget = QtWidgets.QWidget(self)
        self.notificationWidget.setMaximumHeight(0)  # Initially hidden
        self.notificationWidget.setStyleSheet(
            "QWidget {"
            "background-color: #4caf50;"
            "border-radius: 0px;"
            "}"
        )
        self.notificationLayout = QtWidgets.QHBoxLayout(self.notificationWidget)
        self.notificationLayout.setContentsMargins(20, 10, 20, 10)
        
        self.notificationIcon = QtWidgets.QLabel("✓", self.notificationWidget)
        self.notificationIcon.setStyleSheet("color: white; font: 16pt 'Verdana' bold;")
        self.notificationLayout.addWidget(self.notificationIcon)
        
        self.notificationLabel = QtWidgets.QLabel("", self.notificationWidget)
        self.notificationLabel.setStyleSheet("color: white; font: 11pt 'Verdana';")
        self.notificationLayout.addWidget(self.notificationLabel)
        self.notificationLayout.addStretch()
        
        self.verticalLayout.addWidget(self.notificationWidget)
        
        # Timer for auto-hiding notifications
        self.notificationTimer = QtCore.QTimer(self)
        self.notificationTimer.setSingleShot(True)
        self.notificationTimer.timeout.connect(self._hide_notification)

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)

        self.widget = QtWidgets.QWidget(self)
        self.widget.setMinimumWidth(500)  # Fixed width for main panel
        self.widget.setMaximumWidth(500)
        self.widget.setStyleSheet(".QWidget{background-color: rgb(12, 12, 24);}")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(9, 0, 0, 0)
        self.verticalLayout_2.setAlignment(QtCore.Qt.AlignTop)  # Keep content at top

        # Top bar with close and settings toggle buttons
        self.topBarLayout = QtWidgets.QHBoxLayout()
        self.topBarLayout.setContentsMargins(0, 5, 0, 5)
        
        # Close button at top-left
        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        self.pushButton_3.setMinimumSize(QtCore.QSize(35, 25))
        self.pushButton_3.setMaximumSize(QtCore.QSize(35, 25))
        self.pushButton_3.setStyleSheet("color: white;\n"
                                        "font: 13pt \"Verdana\";\n"
                                        "border-radius: 1px;\n"
                                        "opacity: 200;\n")
        self.pushButton_3.clicked.connect(self.close)
        self.topBarLayout.addWidget(self.pushButton_3)
        
        self.topBarLayout.addStretch()
        
        # Settings panel toggle button at top-right
        self.settingsToggleButton = QtWidgets.QPushButton(self.widget)
        self.settingsToggleButton.setText("◀")
        self.settingsToggleButton.setMinimumSize(QtCore.QSize(40, 25))
        self.settingsToggleButton.setMaximumSize(QtCore.QSize(40, 25))
        self.settingsToggleButton.setStyleSheet(
            "QPushButton {"
            "color: white;"
            "font: 16pt \"Verdana\";"
            "border: 1px solid #444;"
            "border-radius: 3px;"
            "background: rgb(30, 30, 50);"
            "padding: 2px 2px 0px 2px;"
            "text-align: center;"
            "}"
            "QPushButton:hover {"
            "background: rgb(40, 40, 60);"
            "}"
        )
        self.settingsToggleButton.setToolTip("Collapse/Expand settings panel")
        self.settingsToggleButton.clicked.connect(self._toggle_settings_panel)
        self.topBarLayout.addWidget(self.settingsToggleButton)
        
        self.verticalLayout_2.addLayout(self.topBarLayout, 0)  # Add with stretch factor 0 to prevent expansion

        # Create a container widget for the collapsible settings content
        self.settingsContentWidget = QtWidgets.QWidget(self.widget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.settingsContentWidget)
        self.verticalLayout_3.setContentsMargins(-1, 15, -1, -1)

        # Wallet Import section
        self.walletGroup = QtWidgets.QGroupBox(self.settingsContentWidget)
        self.walletGroup.setStyleSheet("color: rgb(231, 231, 231);\nfont: 13pt \"Verdana\";")
        self.formLayout_wallet = QtWidgets.QFormLayout(self.walletGroup)
        self.formLayout_wallet.setContentsMargins(20, 10, 20, 10)

        # Keypair JSON file selector
        self.keypairPathLayout = QtWidgets.QHBoxLayout()
        self.keypairPathEdit = QtWidgets.QLineEdit(self.walletGroup)
        self.keypairPathEdit.setMinimumSize(QtCore.QSize(0, 32))
        self.keypairPathEdit.setPlaceholderText("Select keypair JSON file...")
        self.keypairPathEdit.setStyleSheet("QLineEdit {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 4px 8px;}")
        self.keypairBrowseBtn = QtWidgets.QPushButton(self.walletGroup)
        self.keypairBrowseBtn.setText("Browse")
        self.keypairBrowseBtn.setStyleSheet("QPushButton {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; border: 1px solid #444; border-radius: 6px; padding: 4px 10px;}")
        self.keypairBrowseBtn.clicked.connect(self._browse_keypair_file)
        self.keypairPathLayout.addWidget(self.keypairPathEdit)
        self.keypairPathLayout.addWidget(self.keypairBrowseBtn)
        self.formLayout_wallet.addRow("Keypair File", self.keypairPathLayout)

        # Seed phrase or private key text
        self.seedOrPrivateEdit = QtWidgets.QLineEdit(self.walletGroup)
        self.seedOrPrivateEdit.setMinimumSize(QtCore.QSize(0, 32))
        self.seedOrPrivateEdit.setPlaceholderText("Enter seed phrase (space-separated) or private key (base58/hex)")
        self.seedOrPrivateEdit.setEchoMode(QtWidgets.QLineEdit.Password)  # Hide text for security
        self.seedOrPrivateEdit.setStyleSheet("QLineEdit {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 4px 8px;}")
        self.formLayout_wallet.addRow("Seed/Private", self.seedOrPrivateEdit)

        # Wallet import section
        self.verticalLayout_3.addWidget(self.walletGroup)

        # removed legacy login/register form

        # Bot configuration section
        self.groupBox = QtWidgets.QGroupBox(self.settingsContentWidget)
        self.groupBox.setStyleSheet("color: rgb(231, 231, 231);\nfont: 13pt \"Verdana\";")
        self.formLayout_cfg = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_cfg.setContentsMargins(20, 20, 20, 20)

        # Network Configuration
        self.rpcUrlEdit = QtWidgets.QLineEdit(self.groupBox)
        self.rpcUrlEdit.setMinimumSize(QtCore.QSize(0, 32))
        self.rpcUrlEdit.setStyleSheet("QLineEdit {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 4px 8px;}")
        self.rpcUrlEdit.setText("https://api.mainnet-beta.solana.com")
        self.formLayout_cfg.addRow("RPC URL", self.rpcUrlEdit)

        # removed API URL field

        # Timing Configuration
        self.betTimeSpin = QtWidgets.QSpinBox(self.groupBox)
        self.betTimeSpin.setRange(0, 3600)
        self.betTimeSpin.setValue(20)
        self.betTimeSpin.setSuffix(" s")
        self.betTimeSpin.setStyleSheet("QSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Bet Time", self.betTimeSpin)

        self.intervalTimeSpin = QtWidgets.QSpinBox(self.groupBox)
        self.intervalTimeSpin.setRange(1, 3600)
        self.intervalTimeSpin.setValue(3)
        self.intervalTimeSpin.setSuffix(" s")
        self.intervalTimeSpin.setStyleSheet("QSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Interval Time", self.intervalTimeSpin)

        self.minWalletBalanceSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.minWalletBalanceSpin.setDecimals(6)
        self.minWalletBalanceSpin.setRange(0.0, 1000000.0)
        self.minWalletBalanceSpin.setSingleStep(0.0001)
        self.minWalletBalanceSpin.setValue(0.0015)
        self.minWalletBalanceSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Min Wallet Balance", self.minWalletBalanceSpin)

        # Even Strategy
        self.evenMinBetSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.evenMinBetSpin.setDecimals(6)
        self.evenMinBetSpin.setRange(0.0, 1000000.0)
        self.evenMinBetSpin.setValue(0.01)
        self.evenMinBetSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Even Min Bet", self.evenMinBetSpin)

        self.evenMaxBetSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.evenMaxBetSpin.setDecimals(6)
        self.evenMaxBetSpin.setRange(0.0, 1000000.0)
        self.evenMaxBetSpin.setValue(1.0)
        self.evenMaxBetSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Even Max Bet", self.evenMaxBetSpin)

        self.evenMultiplierSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.evenMultiplierSpin.setDecimals(3)
        self.evenMultiplierSpin.setRange(1.0, 1000.0)
        self.evenMultiplierSpin.setSingleStep(0.1)
        self.evenMultiplierSpin.setValue(2.1)
        self.evenMultiplierSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Even Multiplier", self.evenMultiplierSpin)

        self.evenModeCombo = QtWidgets.QComboBox(self.groupBox)
        self.evenModeCombo.addItems(["GENERAL", "PAYOUT"])
        self.evenModeCombo.setCurrentText("GENERAL")
        self.evenModeCombo.setStyleSheet("""
            QComboBox {
                color: rgb(231, 231, 231); 
                font: 11pt "Verdana"; 
                background: rgb(20, 20, 40); 
                border: 1px solid #444; 
                border-radius: 6px; 
                padding: 2px 8px;
            }
            QComboBox QAbstractItemView {
                color: rgb(231, 231, 231);
                background-color: rgb(20, 20, 40);
                selection-background-color: rgb(40, 40, 80);
                selection-color: rgb(255, 255, 255);
                border: 1px solid #444;
            }
        """)
        self.formLayout_cfg.addRow("Even Mode", self.evenModeCombo)

        self.evenDirectionCombo = QtWidgets.QComboBox(self.groupBox)
        self.evenDirectionCombo.addItems(["UP", "DOWN"])
        self.evenDirectionCombo.setCurrentText("DOWN")
        self.evenDirectionCombo.setStyleSheet("""
            QComboBox {
                color: rgb(231, 231, 231); 
                font: 11pt "Verdana"; 
                background: rgb(20, 20, 40); 
                border: 1px solid #444; 
                border-radius: 6px; 
                padding: 2px 8px;
            }
            QComboBox QAbstractItemView {
                color: rgb(231, 231, 231);
                background-color: rgb(20, 20, 40);
                selection-background-color: rgb(40, 40, 80);
                selection-color: rgb(255, 255, 255);
                border: 1px solid #444;
            }
        """)
        self.formLayout_cfg.addRow("Even Direction", self.evenDirectionCombo)

        # Odd Strategy
        self.oddMinBetSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.oddMinBetSpin.setDecimals(6)
        self.oddMinBetSpin.setRange(0.0, 1000000.0)
        self.oddMinBetSpin.setValue(0.01)
        self.oddMinBetSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Odd Min Bet", self.oddMinBetSpin)

        self.oddMaxBetSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.oddMaxBetSpin.setDecimals(6)
        self.oddMaxBetSpin.setRange(0.0, 1000000.0)
        self.oddMaxBetSpin.setValue(1.0)
        self.oddMaxBetSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Odd Max Bet", self.oddMaxBetSpin)

        self.oddMultiplierSpin = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.oddMultiplierSpin.setDecimals(3)
        self.oddMultiplierSpin.setRange(1.0, 1000.0)
        self.oddMultiplierSpin.setSingleStep(0.1)
        self.oddMultiplierSpin.setValue(2.1)
        self.oddMultiplierSpin.setStyleSheet("QDoubleSpinBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\"; background: rgb(20, 20, 40); border: 1px solid #444; border-radius: 6px; padding: 2px 8px;}")
        self.formLayout_cfg.addRow("Odd Multiplier", self.oddMultiplierSpin)

        self.oddModeCombo = QtWidgets.QComboBox(self.groupBox)
        self.oddModeCombo.addItems(["GENERAL", "PAYOUT"])
        self.oddModeCombo.setCurrentText("PAYOUT")
        self.oddModeCombo.setStyleSheet("""
            QComboBox {
                color: rgb(231, 231, 231); 
                font: 11pt "Verdana"; 
                background: rgb(20, 20, 40); 
                border: 1px solid #444; 
                border-radius: 6px; 
                padding: 2px 8px;
            }
            QComboBox QAbstractItemView {
                color: rgb(231, 231, 231);
                background-color: rgb(20, 20, 40);
                selection-background-color: rgb(40, 40, 80);
                selection-color: rgb(255, 255, 255);
                border: 1px solid #444;
            }
        """)
        self.formLayout_cfg.addRow("Odd Mode", self.oddModeCombo)

        self.oddDirectionCombo = QtWidgets.QComboBox(self.groupBox)
        self.oddDirectionCombo.addItems(["UP", "DOWN"])
        self.oddDirectionCombo.setCurrentText("UP")
        self.oddDirectionCombo.setStyleSheet("""
            QComboBox {
                color: rgb(231, 231, 231); 
                font: 11pt "Verdana"; 
                background: rgb(20, 20, 40); 
                border: 1px solid #444; 
                border-radius: 6px; 
                padding: 2px 8px;
            }
            QComboBox QAbstractItemView {
                color: rgb(231, 231, 231);
                background-color: rgb(20, 20, 40);
                selection-background-color: rgb(40, 40, 80);
                selection-color: rgb(255, 255, 255);
                border: 1px solid #444;
            }
        """)
        self.formLayout_cfg.addRow("Odd Direction", self.oddDirectionCombo)

        # Toggle
        self.considerOldBetsCheck = QtWidgets.QCheckBox(self.groupBox)
        self.considerOldBetsCheck.setChecked(True)
        self.considerOldBetsCheck.setStyleSheet("QCheckBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\";}")
        self.formLayout_cfg.addRow("Considering Old Bets", self.considerOldBetsCheck)
        
        # Auto Bet Toggle
        self.autoBetCheck = QtWidgets.QCheckBox(self.groupBox)
        self.autoBetCheck.setChecked(True)
        self.autoBetCheck.setStyleSheet("QCheckBox {color: rgb(231, 231, 231); font: 11pt \"Verdana\";}")
        self.autoBetCheck.stateChanged.connect(self._on_auto_bet_changed)
        self.formLayout_cfg.addRow("Auto Bet", self.autoBetCheck)

        self.verticalLayout_3.addWidget(self.groupBox)

        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)

        # Bottom action button
        self.setButton = QtWidgets.QPushButton(self.settingsContentWidget)
        self.setButton.setText("Set")
        self.setButton.setMinimumSize(QtCore.QSize(0, 48))
        self.setButton.setStyleSheet("color: rgb(231, 231, 231);\n"
                                     "font: 15pt \"Verdana\";\n"
                                     "border: 2px solid orange;\n"
                                     "padding: 6px;\n"
                                     "border-radius: 4px;\n")
        self.verticalLayout_3.addWidget(self.setButton)
        self.setButton.clicked.connect(self.save_settings)

        # Start/Stop button below Set
        self.startStopButton = QtWidgets.QPushButton(self.settingsContentWidget)
        self.startStopButton.setText("Start")
        self.startStopButton.setMinimumSize(QtCore.QSize(0, 48))
        self.startStopButton.setCheckable(True)
        self.startStopButton.toggled.connect(self._on_start_stop)
        self.startStopButton.setStyleSheet("color: rgb(231, 231, 231);\n"
                                           "font: 15pt \"Verdana\";\n"
                                           "border: 2px solid #4caf50;\n"
                                           "padding: 6px;\n"
                                           "border-radius: 4px;\n")
        self.verticalLayout_3.addWidget(self.startStopButton)
        
        # Add the settings content widget to the main widget layout
        self.verticalLayout_2.addWidget(self.settingsContentWidget)

        self.horizontalLayout_3.addWidget(self.widget)

        # Middle - Round Card Panel
        self.roundCardPanel = QtWidgets.QWidget(self)
        self.roundCardPanel.setMinimumWidth(380)
        self.roundCardPanel.setMaximumWidth(380)
        self.roundCardPanel.setStyleSheet(
            "QWidget {"
            "background-color: rgb(20, 20, 40);"
            "}"
        )
        self.roundCardLayout = QtWidgets.QVBoxLayout(self.roundCardPanel)
        self.roundCardLayout.setContentsMargins(15, 15, 15, 15)
        self.roundCardLayout.setSpacing(10)
        
        # Round info container (narrower, centered)
        self.roundInfoContainer = QtWidgets.QWidget(self.roundCardPanel)
        self.roundInfoContainer.setMaximumWidth(340)
        self.roundInfoContainer.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        self.roundInfoLayout = QtWidgets.QVBoxLayout(self.roundInfoContainer)
        self.roundInfoLayout.setContentsMargins(0, 0, 0, 0)
        self.roundInfoLayout.setSpacing(8)
        self.roundInfoLayout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Round header
        self.roundHeaderLayout = QtWidgets.QHBoxLayout()
        self.roundHeaderLabel = QtWidgets.QLabel("Next", self.roundInfoContainer)
        self.roundHeaderLabel.setStyleSheet("color: rgba(255, 255, 255, 0.7); font: 10pt 'Verdana';")
        self.roundNumberLabel = QtWidgets.QLabel("#0", self.roundInfoContainer)
        self.roundNumberLabel.setStyleSheet("color: white; font: 10pt 'Verdana' bold;")
        self.roundHeaderLayout.addWidget(self.roundHeaderLabel)
        self.roundHeaderLayout.addStretch()
        self.roundHeaderLayout.addWidget(self.roundNumberLabel)
        self.roundInfoLayout.addLayout(self.roundHeaderLayout)
        
        # Remaining time display
        self.remainingTimeLabel = QtWidgets.QLabel("Waiting...", self.roundInfoContainer)
        self.remainingTimeLabel.setStyleSheet("color: #ffa726; font: 12pt 'Verdana' bold;")
        self.remainingTimeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.roundInfoLayout.addWidget(self.remainingTimeLabel)
        
        # UP section
        self.upSection = QtWidgets.QWidget(self.roundInfoContainer)
        self.upSection.setStyleSheet(
            "QWidget {"
            "background-color: rgba(100, 50, 150, 0.3);"
            "border-radius: 8px;"
            "padding: 8px;"
            "}"
        )
        self.upSectionLayout = QtWidgets.QVBoxLayout(self.upSection)
        self.upSectionLayout.setContentsMargins(8, 6, 8, 6)
        
        # Combined label for direction and bet amount
        self.upLabel = QtWidgets.QLabel("UP", self.upSection)
        self.upLabel.setStyleSheet("color: white; font: 12pt 'Verdana' bold;")
        self.upLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.upSectionLayout.addWidget(self.upLabel)
        
        self.upPayoutLabel = QtWidgets.QLabel("0.00x Payout", self.upSection)
        self.upPayoutLabel.setStyleSheet("color: rgba(255, 255, 255, 0.7); font: 9pt 'Verdana';")
        self.upPayoutLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.upSectionLayout.addWidget(self.upPayoutLabel)
        self.roundInfoLayout.addWidget(self.upSection)
        
        # Solana logo with background image
        self.logoLabel = QtWidgets.QLabel(self.roundInfoContainer)
        self.logoLabel.setMinimumSize(QtCore.QSize(360, 160))  # Reduced from 180 to fit layout better
        self.logoLabel.setMaximumSize(QtCore.QSize(360, 160))
        
        # Load the solana background image
        solana_bg_path = os.path.join(os.path.dirname(__file__), "img", "solana_bg.webp")
        if os.path.exists(solana_bg_path):
            pixmap = QtGui.QPixmap(solana_bg_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(360, 160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.logoLabel.setPixmap(scaled_pixmap)
                self.logoLabel.setScaledContents(False)
                self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        else:
            # Fallback to text if image not found
            self.logoLabel.setStyleSheet(
                "QLabel {"
                "background-color: rgba(30, 30, 60, 0.5);"
                "border-radius: 10px;"
                "color: rgba(255, 255, 255, 0.5);"
                "font: 16pt 'Verdana';"
                "}"
            )
            self.logoLabel.setText("SOLANA")
            self.logoLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        self.logoLabel.setStyleSheet(
            "QLabel {"
            "border-radius: 10px;"
            "}"
        )
        self.roundInfoLayout.addWidget(self.logoLabel)
        
        # Prize pool
        self.prizePoolLayout = QtWidgets.QHBoxLayout()
        self.prizePoolTextLabel = QtWidgets.QLabel("Prize Pool", self.roundInfoContainer)
        self.prizePoolTextLabel.setStyleSheet("color: rgba(255, 255, 255, 0.8); font: 9pt 'Verdana';")
        self.prizePoolValueLabel = QtWidgets.QLabel("0.0000 SOL", self.roundInfoContainer)
        self.prizePoolValueLabel.setStyleSheet("color: white; font: 9pt 'Verdana' bold;")
        self.prizePoolLayout.addWidget(self.prizePoolTextLabel)
        self.prizePoolLayout.addStretch()
        self.prizePoolLayout.addWidget(self.prizePoolValueLabel)
        self.roundInfoLayout.addLayout(self.prizePoolLayout)
        
        # Wallet balance
        self.walletBalanceLayout = QtWidgets.QHBoxLayout()
        self.walletBalanceTextLabel = QtWidgets.QLabel("Balance", self.roundInfoContainer)
        self.walletBalanceTextLabel.setStyleSheet("color: rgba(255, 255, 255, 0.8); font: 9pt 'Verdana';")
        self.walletBalanceValueLabel = QtWidgets.QLabel("0.0000 SOL", self.roundInfoContainer)
        self.walletBalanceValueLabel.setStyleSheet("color: #4caf50; font: 9pt 'Verdana' bold;")  # Green for balance
        self.walletBalanceLayout.addWidget(self.walletBalanceTextLabel)
        self.walletBalanceLayout.addStretch()
        self.walletBalanceLayout.addWidget(self.walletBalanceValueLabel)
        self.roundInfoLayout.addLayout(self.walletBalanceLayout)
        
        # Enter UP button
        self.enterUpButton = QtWidgets.QPushButton("Enter UP", self.roundInfoContainer)
        self.enterUpButton.setMinimumSize(QtCore.QSize(0, 38))
        self.enterUpButton.setStyleSheet(
            "QPushButton {"
            "background-color: #4caf50;"
            "color: white;"
            "font: 11pt 'Verdana' bold;"
            "border: none;"
            "border-radius: 8px;"
            "}"
            "QPushButton:hover:enabled {"
            "background-color: #45a049;"
            "}"
            "QPushButton:pressed:enabled {"
            "background-color: #3d8b40;"
            "}"
            "QPushButton:disabled {"
            "background-color: rgba(76, 175, 80, 0.3);"
            "color: rgba(255, 255, 255, 0.4);"
            "}"
        )
        self.enterUpButton.setEnabled(False)  # Disabled until bot places a bet
        self.enterUpButton.clicked.connect(lambda: self._show_place_order("UP"))
        self.roundInfoLayout.addWidget(self.enterUpButton)
        
        # Enter DOWN button
        self.enterDownButton = QtWidgets.QPushButton("Enter DOWN", self.roundInfoContainer)
        self.enterDownButton.setMinimumSize(QtCore.QSize(0, 38))
        self.enterDownButton.setStyleSheet(
            "QPushButton {"
            "background-color: #f44336;"
            "color: white;"
            "font: 11pt 'Verdana' bold;"
            "border: none;"
            "border-radius: 8px;"
            "}"
            "QPushButton:hover:enabled {"
            "background-color: #da190b;"
            "}"
            "QPushButton:pressed:enabled {"
            "background-color: #ba0c0c;"
            "}"
            "QPushButton:disabled {"
            "background-color: rgba(244, 67, 54, 0.3);"
            "color: rgba(255, 255, 255, 0.4);"
            "}"
        )
        self.enterDownButton.setEnabled(False)  # Disabled until bot places a bet
        self.enterDownButton.clicked.connect(lambda: self._show_place_order("DOWN"))
        self.roundInfoLayout.addWidget(self.enterDownButton)
        
        # DOWN section
        self.downSection = QtWidgets.QWidget(self.roundInfoContainer)
        self.downSection.setStyleSheet(
            "QWidget {"
            "background-color: rgba(100, 50, 150, 0.3);"
            "border-radius: 8px;"
            "padding: 8px;"
            "}"
        )
        self.downSectionLayout = QtWidgets.QVBoxLayout(self.downSection)
        self.downSectionLayout.setContentsMargins(8, 6, 8, 6)
        
        self.downPayoutLabel = QtWidgets.QLabel("0.00x Payout", self.downSection)
        self.downPayoutLabel.setStyleSheet("color: rgba(255, 255, 255, 0.7); font: 9pt 'Verdana';")
        self.downPayoutLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.downSectionLayout.addWidget(self.downPayoutLabel)
        
        # Combined label for direction and bet amount
        self.downLabel = QtWidgets.QLabel("DOWN", self.downSection)
        self.downLabel.setStyleSheet("color: white; font: 12pt 'Verdana' bold;")
        self.downLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.downSectionLayout.addWidget(self.downLabel)
        self.roundInfoLayout.addWidget(self.downSection)
        
        # Add round info container to main layout (centered)
        containerLayout = QtWidgets.QHBoxLayout()
        containerLayout.addStretch()
        containerLayout.addWidget(self.roundInfoContainer)
        containerLayout.addStretch()
        self.roundCardLayout.addLayout(containerLayout)
        
        # Latest Bets Section
        self.latestBetsLabel = QtWidgets.QLabel("Latest Bets", self.roundCardPanel)
        self.latestBetsLabel.setStyleSheet("color: white; font: 12pt 'Verdana' bold; margin-top: 10px;")
        self.latestBetsLabel.setAlignment(QtCore.Qt.AlignLeft)
        self.roundCardLayout.addWidget(self.latestBetsLabel)
        
        # Table for bets
        self.betsTable = QtWidgets.QTableWidget(self.roundCardPanel)
        self.betsTable.setColumnCount(5)
        self.betsTable.setHorizontalHeaderLabels(["Round", "Dir", "Amount", "Status", "Payout"])
        self.betsTable.setMinimumHeight(150)  # Reduced from 200 to fit in layout
        self.betsTable.setMaximumHeight(300)
        
        # Set size policy to allow the table to shrink and use scrollbar
        self.betsTable.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        
        # Ensure scrollbars are shown when needed (important for Linux)
        self.betsTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.betsTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.betsTable.horizontalHeader().setStretchLastSection(False)
        self.betsTable.verticalHeader().setVisible(False)
        self.betsTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.betsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.betsTable.setShowGrid(False)
        
        # Set column widths (adjusted for 380px panel)
        self.betsTable.setColumnWidth(0, 65)   # Round
        self.betsTable.setColumnWidth(1, 50)   # Direction
        self.betsTable.setColumnWidth(2, 75)   # Amount
        self.betsTable.setColumnWidth(3, 75)   # Status
        self.betsTable.setColumnWidth(4, 80)   # Payout
        self.betsTable.horizontalHeader().setStretchLastSection(True)  # Stretch last column to fill
        
        self.betsTable.setStyleSheet(
            "QTableWidget {"
            "background-color: rgba(30, 30, 50, 0.5);"
            "border: 1px solid #444;"
            "border-radius: 8px;"
            "color: white;"
            "font: 9pt 'Verdana';"
            "gridline-color: rgba(100, 100, 120, 0.3);"
            "}"
            "QHeaderView::section {"
            "background-color: rgba(50, 50, 70, 0.8);"
            "color: rgba(255, 255, 255, 0.9);"
            "font: 9pt 'Verdana' bold;"
            "border: none;"
            "padding: 6px;"
            "}"
            "QTableWidget::item {"
            "padding: 6px;"
            "border-bottom: 1px solid rgba(100, 100, 120, 0.2);"
            "}"
            "QScrollBar:vertical {"
            "background: rgba(20, 20, 40, 0.8);"
            "width: 12px;"
            "margin: 0px;"
            "border: 1px solid rgba(60, 60, 80, 0.5);"
            "border-radius: 6px;"
            "}"
            "QScrollBar::handle:vertical {"
            "background: rgba(120, 120, 150, 0.9);"
            "border: 1px solid rgba(140, 140, 170, 0.5);"
            "border-radius: 5px;"
            "min-height: 30px;"
            "margin: 2px;"
            "}"
            "QScrollBar::handle:vertical:hover {"
            "background: rgba(140, 140, 170, 1.0);"
            "}"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {"
            "height: 0px;"
            "}"
            "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {"
            "background: none;"
            "}"
        )
        
        # Add bets table to fill parent width
        self.roundCardLayout.addWidget(self.betsTable)
        
        self.horizontalLayout_3.addWidget(self.roundCardPanel)
        
        # Create Place Order Panel (initially hidden)
        self.placeOrderPanel = QtWidgets.QWidget(self)
        self.placeOrderPanel.setMinimumWidth(380)
        self.placeOrderPanel.setMaximumWidth(380)
        self.placeOrderPanel.setStyleSheet(
            "QWidget {"
            "background-color: rgb(20, 20, 40);"
            "}"
        )
        self.placeOrderLayout = QtWidgets.QVBoxLayout(self.placeOrderPanel)
        self.placeOrderLayout.setContentsMargins(15, 15, 15, 15)
        self.placeOrderLayout.setSpacing(15)
        
        # Header with back button and direction
        self.orderHeaderLayout = QtWidgets.QHBoxLayout()
        self.backButton = QtWidgets.QPushButton("←", self.placeOrderPanel)
        self.backButton.setMinimumSize(QtCore.QSize(35, 35))
        self.backButton.setMaximumSize(QtCore.QSize(35, 35))
        self.backButton.setStyleSheet(
            "QPushButton {"
            "color: white;"
            "font: 18pt 'Verdana';"
            "border: 1px solid #444;"
            "border-radius: 5px;"
            "background: rgb(30, 30, 50);"
            "text-align: center;"
            "padding: 0px 0px 2px 0px;"
            "}"
            "QPushButton:hover {"
            "background: rgb(40, 40, 60);"
            "}"
        )
        self.backButton.clicked.connect(self._show_round_card)
        self.orderHeaderLayout.addWidget(self.backButton)
        
        self.orderHeaderLabel = QtWidgets.QLabel("Place Order", self.placeOrderPanel)
        self.orderHeaderLabel.setStyleSheet("color: white; font: 14pt 'Verdana';")
        self.orderHeaderLayout.addWidget(self.orderHeaderLabel)
        
        self.orderHeaderLayout.addStretch()
        
        self.directionBadge = QtWidgets.QPushButton("UP", self.placeOrderPanel)
        self.directionBadge.setMinimumSize(QtCore.QSize(80, 35))
        self.directionBadge.setMaximumSize(QtCore.QSize(80, 35))
        self.directionBadge.setStyleSheet(
            "QPushButton {"
            "background-color: #4caf50;"
            "color: white;"
            "font: 12pt 'Verdana' bold;"
            "border: none;"
            "border-radius: 8px;"
            "}"
            "QPushButton:hover {"
            "background-color: #45a049;"
            "}"
        )
        self.directionBadge.setToolTip("Click to switch direction")
        self.directionBadge.clicked.connect(self._toggle_order_direction)
        self.orderHeaderLayout.addWidget(self.directionBadge)
        self.placeOrderLayout.addLayout(self.orderHeaderLayout)
        
        # Enter Amount section
        self.amountLabel = QtWidgets.QLabel("Enter Amount", self.placeOrderPanel)
        self.amountLabel.setStyleSheet("color: rgba(255, 255, 255, 0.8); font: 11pt 'Verdana';")
        self.placeOrderLayout.addWidget(self.amountLabel)
        
        # Amount input with SOL indicator
        self.amountInputLayout = QtWidgets.QHBoxLayout()
        self.amountInput = QtWidgets.QLineEdit(self.placeOrderPanel)
        self.amountInput.setMinimumSize(QtCore.QSize(0, 50))
        self.amountInput.setText("0.010000000")
        self.amountInput.setAlignment(QtCore.Qt.AlignRight)
        self.amountInput.setStyleSheet(
            "QLineEdit {"
            "background-color: rgba(30, 30, 50, 0.8);"
            "color: white;"
            "font: 16pt 'Verdana';"
            "border: 1px solid #444;"
            "border-radius: 10px;"
            "padding: 8px 15px;"
            "}"
        )
        self.amountInput.textChanged.connect(self._validate_bet_amount)
        self.amountInputLayout.addWidget(self.amountInput)
        
        self.solLabel = QtWidgets.QLabel("SOL", self.placeOrderPanel)
        self.solLabel.setStyleSheet("color: white; font: 11pt 'Verdana' bold;")
        self.amountInputLayout.addWidget(self.solLabel)
        self.placeOrderLayout.addLayout(self.amountInputLayout)
        
        # Slider
        self.amountSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.placeOrderPanel)
        self.amountSlider.setMinimum(0)
        self.amountSlider.setMaximum(100)
        self.amountSlider.setValue(10)
        self.amountSlider.setStyleSheet(
            "QSlider::groove:horizontal {"
            "border: 1px solid #444;"
            "height: 4px;"
            "background: rgba(255, 255, 255, 0.2);"
            "border-radius: 2px;"
            "}"
            "QSlider::handle:horizontal {"
            "background: #4caf50;"
            "border: 2px solid #4caf50;"
            "width: 20px;"
            "height: 20px;"
            "margin: -8px 0;"
            "border-radius: 10px;"
            "}"
        )
        self.amountSlider.valueChanged.connect(self._update_amount_from_slider)
        self.placeOrderLayout.addWidget(self.amountSlider)
        
        # Percentage buttons
        self.percentageLayout = QtWidgets.QHBoxLayout()
        self.percentageLayout.setSpacing(8)
        
        for percent in ["10%", "25%", "50%", "75%", "Max"]:
            btn = QtWidgets.QPushButton(percent, self.placeOrderPanel)
            btn.setMinimumSize(QtCore.QSize(0, 35))
            btn.setStyleSheet(
                "QPushButton {"
                "background-color: rgba(60, 60, 80, 0.8);"
                "color: white;"
                "font: 10pt 'Verdana';"
                "border: 1px solid #444;"
                "border-radius: 8px;"
                "}"
                "QPushButton:hover {"
                "background-color: rgba(80, 80, 100, 0.8);"
                "}"
                "QPushButton:pressed {"
                "background-color: rgba(100, 100, 120, 0.8);"
                "}"
            )
            btn.clicked.connect(lambda checked, p=percent: self._set_percentage_amount(p))
            self.percentageLayout.addWidget(btn)
        
        self.placeOrderLayout.addLayout(self.percentageLayout)
        
        # Add some spacing
        self.placeOrderLayout.addSpacing(20)
        
        # Confirm button
        self.confirmOrderButton = QtWidgets.QPushButton("Confirm", self.placeOrderPanel)
        self.confirmOrderButton.setMinimumSize(QtCore.QSize(0, 50))
        self.confirmOrderButton.setStyleSheet(
            "QPushButton {"
            "background-color: rgba(80, 80, 100, 0.8);"
            "color: white;"
            "font: 14pt 'Verdana' bold;"
            "border: none;"
            "border-radius: 10px;"
            "}"
            "QPushButton:hover:enabled {"
            "background-color: rgba(100, 100, 120, 0.8);"
            "}"
            "QPushButton:pressed:enabled {"
            "background-color: rgba(120, 120, 140, 0.8);"
            "}"
            "QPushButton:disabled {"
            "background-color: rgba(60, 60, 70, 0.5);"
            "color: rgba(255, 255, 255, 0.3);"
            "}"
        )
        self.confirmOrderButton.clicked.connect(self._confirm_manual_bet)
        self.placeOrderLayout.addWidget(self.confirmOrderButton)
        
        # Add stretch at bottom
        self.placeOrderLayout.addStretch()
        
        # Add place order panel to layout (initially hidden)
        self.placeOrderPanel.hide()
        self.horizontalLayout_3.addWidget(self.placeOrderPanel)

        # Right-side log panel container
        self.logContainer = QtWidgets.QWidget(self)
        self.logContainer.setStyleSheet(
            "QWidget {"
            "background-color: rgb(12, 12, 24);"
            "}"
        )
        self.logContainerLayout = QtWidgets.QVBoxLayout(self.logContainer)
        self.logContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.logContainerLayout.setSpacing(0)
        self.logContainerLayout.setAlignment(QtCore.Qt.AlignTop)
        
        # Collapse/Expand button in log panel - stays at top
        self.logToggleButton = QtWidgets.QPushButton(self.logContainer)
        self.logToggleButton.setText("◀")
        self.logToggleButton.setMinimumSize(QtCore.QSize(40, 30))
        self.logToggleButton.setMaximumSize(QtCore.QSize(40, 30))
        self.logToggleButton.setStyleSheet(
            "QPushButton {"
            "color: white;"
            "font: 16pt \"Verdana\";"
            "border: 1px solid #444;"
            "border-radius: 0px;"
            "background: rgb(20, 20, 40);"
            "padding: 2px 2px 0px 2px;"
            "text-align: center;"
            "}"
            "QPushButton:hover {"
            "background: rgb(30, 30, 50);"
            "}"
        )
        self.logToggleButton.setToolTip("Collapse/Expand logs")
        self.logToggleButton.clicked.connect(self._toggle_log_panel)
        self.logContainerLayout.addWidget(self.logToggleButton, 0, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        
        # Log panel text area
        self.logPanel = QtWidgets.QPlainTextEdit(self.logContainer)
        self.logPanel.setReadOnly(True)
        self.logPanel.setStyleSheet(
            "QPlainTextEdit {"
            "background: rgb(12, 12, 24);"
            "color: rgb(210, 210, 210);"
            "font: 10pt \"Consolas\";"
            "}"
        )
        self.logContainerLayout.addWidget(self.logPanel, 1)  # Stretch factor 1
        
        # Set initial width for log container
        self.logContainer.setMinimumWidth(500)
        self.logContainer.setMaximumWidth(500)
        
        self.horizontalLayout_3.addWidget(self.logContainer)

        # Set size policies to prevent expansion
        self.widget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.roundCardPanel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.placeOrderPanel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        self.logContainer.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        
        # Track panel visibility states (all start expanded)
        self.log_panel_visible = True
        self.settings_panel_visible = True
        self.selected_direction = "UP"  # Default direction for manual betting
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        # Load previously saved settings (if any)
        self.load_settings()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.pushButton_3.setText(_translate("Form", "X"))

    def get_config(self):
        return {
            "RPC_URL": self.rpcUrlEdit.text().strip(),
            "BET_TIME": int(self.betTimeSpin.value()),
            "INTERVAL_TIME": int(self.intervalTimeSpin.value()),
            "MIN_WALLET_BALANCE": float(self.minWalletBalanceSpin.value()),
            "EVEN_MIN_BET_AMOUNT": float(self.evenMinBetSpin.value()),
            "EVEN_MAX_BET_AMOUNT": float(self.evenMaxBetSpin.value()),
            "EVEN_MULTIPLIER": float(self.evenMultiplierSpin.value()),
            "EVEN_MODE": self.evenModeCombo.currentText(),
            "EVEN_DIRECTION": self.evenDirectionCombo.currentText(),
            "ODD_MIN_BET_AMOUNT": float(self.oddMinBetSpin.value()),
            "ODD_MAX_BET_AMOUNT": float(self.oddMaxBetSpin.value()),
            "ODD_MULTIPLIER": float(self.oddMultiplierSpin.value()),
            "ODD_MODE": self.oddModeCombo.currentText(),
            "ODD_DIRECTION": self.oddDirectionCombo.currentText(),
            "CONSIDERING_OLD_BETS": bool(self.considerOldBetsCheck.isChecked()),
            "AUTO_BET": bool(self.autoBetCheck.isChecked()),
        }

    def _browse_keypair_file(self):
        dialog = QtWidgets.QFileDialog(self, "Select keypair JSON")
        dialog.setNameFilter("JSON Files (*.json);;All Files (*.*)")
        dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dialog.exec_():
            selected_files = dialog.selectedFiles()
            if selected_files:
                keypair_path = selected_files[0]
                self.keypairPathEdit.setText(keypair_path)
                
                # Automatically load and populate the private key
                try:
                    import json
                    with open(keypair_path, 'r') as f:
                        keypair_data = json.load(f)
                    
                    # Keypair file is an array of 64 bytes
                    if isinstance(keypair_data, list) and len(keypair_data) == 64:
                        # Convert to JSON string format for the seed/private field
                        private_key_str = json.dumps(keypair_data)
                        self.seedOrPrivateEdit.setText(private_key_str)
                        
                        # Show success message in log panel
                        self._append_log(f"✅ Keypair loaded from: {os.path.basename(keypair_path)}")
                        self._append_log(f"🔑 Private key automatically populated")
                    else:
                        self._append_log(f"⚠️  Invalid keypair format in {os.path.basename(keypair_path)}")
                        self._append_log(f"💡 Expected array of 64 bytes")
                
                except Exception as e:
                    self._append_log(f"❌ Failed to load keypair: {e}")
                    # Keep the path but don't populate the private key field

    def get_wallet_input(self):
        return {
            "keypair_file": self.keypairPathEdit.text().strip(),
            "seed_or_private": self.seedOrPrivateEdit.text().strip(),
        }

    # Settings persistence helpers
    def _settings(self):
        return QtCore.QSettings("fortuva", "bot-config")

    def save_settings(self):
        s = self._settings()
        # Wallet
        s.setValue("wallet/keypair_file", self.keypairPathEdit.text().strip())
        s.setValue("wallet/seed_or_private", self.seedOrPrivateEdit.text().strip())
        # Network & timing
        s.setValue("rpc_url", self.rpcUrlEdit.text().strip())
        s.setValue("bet_time", int(self.betTimeSpin.value()))
        s.setValue("interval_time", int(self.intervalTimeSpin.value()))
        s.setValue("min_wallet_balance", float(self.minWalletBalanceSpin.value()))
        # Even
        s.setValue("even/min_bet", float(self.evenMinBetSpin.value()))
        s.setValue("even/max_bet", float(self.evenMaxBetSpin.value()))
        s.setValue("even/multiplier", float(self.evenMultiplierSpin.value()))
        s.setValue("even/mode", self.evenModeCombo.currentText())
        s.setValue("even/direction", self.evenDirectionCombo.currentText())
        # Odd
        s.setValue("odd/min_bet", float(self.oddMinBetSpin.value()))
        s.setValue("odd/max_bet", float(self.oddMaxBetSpin.value()))
        s.setValue("odd/multiplier", float(self.oddMultiplierSpin.value()))
        s.setValue("odd/mode", self.oddModeCombo.currentText())
        s.setValue("odd/direction", self.oddDirectionCombo.currentText())
        # Toggles
        s.setValue("considering_old_bets", bool(self.considerOldBetsCheck.isChecked()))
        s.setValue("auto_bet", bool(self.autoBetCheck.isChecked()))
        s.sync()

    def load_settings(self):
        s = self._settings()
        # Wallet
        self.keypairPathEdit.setText(s.value("wallet/keypair_file", ""))
        self.seedOrPrivateEdit.setText(s.value("wallet/seed_or_private", ""))
        # Network & timing
        self.rpcUrlEdit.setText(s.value("rpc_url", self.rpcUrlEdit.text()))
        self.betTimeSpin.setValue(int(s.value("bet_time", self.betTimeSpin.value())))
        self.intervalTimeSpin.setValue(int(s.value("interval_time", self.intervalTimeSpin.value())))
        self.minWalletBalanceSpin.setValue(float(s.value("min_wallet_balance", self.minWalletBalanceSpin.value())))
        # Even
        self.evenMinBetSpin.setValue(float(s.value("even/min_bet", self.evenMinBetSpin.value())))
        self.evenMaxBetSpin.setValue(float(s.value("even/max_bet", self.evenMaxBetSpin.value())))
        self.evenMultiplierSpin.setValue(float(s.value("even/multiplier", self.evenMultiplierSpin.value())))
        self.evenModeCombo.setCurrentText(str(s.value("even/mode", self.evenModeCombo.currentText())))
        self.evenDirectionCombo.setCurrentText(str(s.value("even/direction", self.evenDirectionCombo.currentText())))
        # Odd
        self.oddMinBetSpin.setValue(float(s.value("odd/min_bet", self.oddMinBetSpin.value())))
        self.oddMaxBetSpin.setValue(float(s.value("odd/max_bet", self.oddMaxBetSpin.value())))
        self.oddMultiplierSpin.setValue(float(s.value("odd/multiplier", self.oddMultiplierSpin.value())))
        self.oddModeCombo.setCurrentText(str(s.value("odd/mode", self.oddModeCombo.currentText())))
        self.oddDirectionCombo.setCurrentText(str(s.value("odd/direction", self.oddDirectionCombo.currentText())))
        # Toggles
        self.considerOldBetsCheck.setChecked(str(s.value("considering_old_bets", "true")).lower() in ("1", "true", "yes"))
        self.autoBetCheck.setChecked(str(s.value("auto_bet", "true")).lower() in ("1", "true", "yes"))

    # enable window dragging on frameless window
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_active = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    # Bot start/stop handlers
    def _on_start_stop(self, checked: bool):
        self.startStopButton.setText("Stop" if checked else "Start")
        if checked:
            self.start_bot()
            # Enable manual betting buttons when bot starts
            self.enterUpButton.setEnabled(True)
            self.enterDownButton.setEnabled(True)
        else:
            self.stop_bot()
            # Disable manual betting buttons when bot stops
            self.enterUpButton.setEnabled(False)
            self.enterDownButton.setEnabled(False)

    def start_bot(self):
        # Persist current settings before starting
        self.save_settings()
        cfg = self.get_config()
        wallet = self.get_wallet_input()
        
        # Try to load initial bets if wallet is available
        if wallet.get("seed_or_private"):
            try:
                from bot.blockchain import create_keypair_from_private_key
                keypair = create_keypair_from_private_key(wallet["seed_or_private"])
                wallet_address = str(keypair.pubkey())
                # Load bets asynchronously
                QtCore.QTimer.singleShot(2000, lambda: self.update_latest_bets(wallet_address))
            except:
                pass

        bot_cfg = BotConfig(
            rpc_url=cfg["RPC_URL"],
            bet_time=cfg["BET_TIME"],
            interval_time=cfg["INTERVAL_TIME"],
            min_wallet_balance=cfg["MIN_WALLET_BALANCE"],
            even_min_bet=cfg["EVEN_MIN_BET_AMOUNT"],
            even_max_bet=cfg["EVEN_MAX_BET_AMOUNT"],
            even_multiplier=cfg["EVEN_MULTIPLIER"],
            even_mode=cfg["EVEN_MODE"],
            even_direction=cfg["EVEN_DIRECTION"],
            odd_min_bet=cfg["ODD_MIN_BET_AMOUNT"],
            odd_max_bet=cfg["ODD_MAX_BET_AMOUNT"],
            odd_multiplier=cfg["ODD_MULTIPLIER"],
            odd_mode=cfg["ODD_MODE"],
            odd_direction=cfg["ODD_DIRECTION"],
            considering_old_bets=cfg["CONSIDERING_OLD_BETS"],
            auto_bet=cfg["AUTO_BET"],
        )

        self._bot_worker = BotWorker(wallet=wallet, config=bot_cfg)
        # Connect worker signals to UI updates
        self._bot_worker.status.connect(self._append_log)
        self._bot_worker.round_update.connect(self.update_round_card)
        self._bot_worker.bet_placed.connect(self._on_bet_placed)
        self._bot_worker.bet_placing.connect(self._on_bet_placing)
        self._bot_worker.claim_success.connect(self._on_claim_success)
        self._bot_worker.finished.connect(self._on_bot_stopped)
        self._bot_worker.start()

    def stop_bot(self):
        worker = getattr(self, "_bot_worker", None)
        if worker is not None and worker.isRunning():
            worker.stop()
            worker.wait(3000)
    
    def _on_bet_placed(self, bet_data: dict):
        """Handle bet placed event - show notification for both manual and automatic bets."""
        try:
            direction = bet_data.get('direction', 'unknown').upper()
            amount = bet_data.get('amount', 0)
            round_num = bet_data.get('round_number', bet_data.get('round', 0))
            
            # Update bet amount display in direction buttons
            if direction == 'UP':
                # Combine direction and bet amount in a single label with colored bet amount
                self.upLabel.setText(
                    f'<span style="color: white;">{direction}</span> '
                    f'<span style="color: #4caf50;">- {amount:.4f} SOL</span>'
                )
            elif direction == 'DOWN':
                # Combine direction and bet amount in a single label with colored bet amount
                self.downLabel.setText(
                    f'<span style="color: white;">{direction}</span> '
                    f'<span style="color: #f44336;">- {amount:.4f} SOL</span>'
                )
            
            # Show success notification (works for both manual and automatic bets)
            self._show_notification(
                f"Bet placed: {amount:.4f} SOL on {direction} for round #{round_num}",
                "success"
            )
            print(f"[DEBUG] Bet notification triggered: {direction} {amount} SOL on round {round_num}")
        except Exception as e:
            print(f"Error showing bet notification: {e}")
    
    def _on_bet_placing(self, is_placing: bool):
        """Handle bet placing state change - disable buttons and show loading."""
        try:
            if is_placing:
                # Disable Enter UP/DOWN buttons during bet placement
                self.enterUpButton.setEnabled(False)
                self.enterDownButton.setEnabled(False)
                
                # Show loading indicator
                self.remainingTimeLabel.setText("Placing bet...")
                self.remainingTimeLabel.setStyleSheet("color: #ffa726; font: 12pt 'Verdana' bold;")
                
                print("[DEBUG] Bet placing started - buttons disabled")
            else:
                # Re-enable buttons when done (if bot is running and no bet exists)
                worker = getattr(self, "_bot_worker", None)
                bot_running = worker is not None and worker.isRunning()
                
                # We'll let the next round_update handle enabling buttons based on has_bet status
                # Just clear the loading indicator
                print("[DEBUG] Bet placing finished")
        except Exception as e:
            print(f"Error handling bet placing state: {e}")
    
    def _on_claim_success(self, claim_data: dict):
        """Handle claim success event - show notification."""
        try:
            reward_amount = claim_data.get('reward_amount', 0)
            round_num = claim_data.get('round_number', 0)
            
            # Show success notification
            self._show_notification(
                f"Claimed {reward_amount:.4f} SOL reward from round #{round_num}!",
                "success"
            )
            print(f"[DEBUG] Claim notification triggered: {reward_amount} SOL from round {round_num}")
        except Exception as e:
            print(f"Error showing claim notification: {e}")
    
    def _on_bot_stopped(self):
        """Handle bot stopped event - reset state."""
        self.startStopButton.setChecked(False)
        # Disable Enter UP/DOWN buttons when bot stops
        self.enterUpButton.setEnabled(False)
        self.enterDownButton.setEnabled(False)
    
    def _on_auto_bet_changed(self, state: int):
        """Handle Auto Bet checkbox state change - update running bot."""
        is_checked = (state == QtCore.Qt.Checked)
        
        # Update running bot's config if bot is running
        worker = getattr(self, "_bot_worker", None)
        if worker is not None and worker.isRunning():
            if hasattr(worker, 'betting_service') and worker.betting_service:
                worker.betting_service.config['auto_bet'] = is_checked
                
                if is_checked:
                    self._append_log("✅ Auto betting enabled")
                else:
                    self._append_log("⏸️  Auto betting paused (manual bets still available)")

    def _append_log(self, message: str):
        self.logPanel.appendPlainText(message)
        # Auto-scroll to bottom
        cursor = self.logPanel.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.logPanel.setTextCursor(cursor)

        # Show notifications for important events
        if "❌ Failed to place bet" in message and "transaction returned None" not in message:
            # Extract failure reason if possible
            self._show_notification("Bet placement failed", "error")
        elif "✅ Cancelled bet and refunded" in message:
            # Successful cancel - extract amount
            try:
                parts = message.split("refunded ")
                if len(parts) > 1:
                    amount_str = parts[1].split(" SOL")[0]
                    self._show_notification(f"Bet cancelled, refunded {amount_str} SOL", "info")
                else:
                    self._show_notification("Bet cancelled successfully", "info")
            except:
                self._show_notification("Bet cancelled successfully", "info")
        elif "✅ Closed bet for Round" in message:
            # Successful close
            self._show_notification("Bet closed, rent reclaimed", "info")

    def update_latest_bets(self, wallet_address: str):
        """Fetch and display latest bets from API."""
        import threading
        
        def fetch_and_update():
            try:
                from bot.api import FortuvaApi
                api = FortuvaApi()
                # Fetch bets from API
                bets = api.get_user_bets(wallet_address)
                
                # Update UI in main thread
                QtCore.QMetaObject.invokeMethod(
                    self,
                    "_update_bets_ui",
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(list, bets if bets else [])
                )
            
            except Exception as e:
                # Log error
                import traceback
                self._append_log(f"❌ Failed to fetch bets: {type(e).__name__}: {e}")
                self._append_log(f"📋 Traceback: {traceback.format_exc()}")
        
        # Run in background thread to avoid blocking UI
        thread = threading.Thread(target=fetch_and_update, daemon=True)
        thread.start()
    
    @QtCore.pyqtSlot(list)
    def _update_bets_ui(self, bets: list):
        """Update the bets table (must be called from main thread)."""
        try:
            # Clear table
            self.betsTable.setRowCount(0)
            
            if not bets or len(bets) == 0:
                # Show no bets row
                self.betsTable.setRowCount(1)
                no_bets_item = QtWidgets.QTableWidgetItem("No bets found")
                no_bets_item.setTextAlignment(QtCore.Qt.AlignCenter)
                no_bets_item.setForeground(QtGui.QColor(255, 255, 255, 128))
                self.betsTable.setItem(0, 0, no_bets_item)
                self.betsTable.setSpan(0, 0, 1, 5)  # Span across all columns
                return
            
            # Sort bets (most recent first)
            sorted_bets = sorted(bets, key=lambda x: x.get('epoch', 0), reverse=True)
            
            # Add bets to table
            for row, bet in enumerate(sorted_bets[:10]):  # Show last 10 bets
                self.betsTable.insertRow(row)
                
                # Round number
                round_item = QtWidgets.QTableWidgetItem(f"#{bet.get('epoch', 0)}")
                round_item.setForeground(QtGui.QColor(255, 255, 255))
                self.betsTable.setItem(row, 0, round_item)
                
                # Direction with color
                direction = bet.get('direction', 'up').upper()
                direction_item = QtWidgets.QTableWidgetItem(direction)
                direction_color = QtGui.QColor(76, 175, 80) if direction == 'UP' else QtGui.QColor(244, 67, 54)
                direction_item.setForeground(direction_color)
                self.betsTable.setItem(row, 1, direction_item)
                
                # Amount
                try:
                    amount_str = str(bet.get('amount', '0'))
                    amount = float(amount_str) / 1_000_000_000
                except:
                    amount = 0.0
                amount_item = QtWidgets.QTableWidgetItem(f"{amount:.3f}")
                amount_item.setForeground(QtGui.QColor(255, 255, 255, 200))
                amount_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.betsTable.setItem(row, 2, amount_item)
                
                # Status with color
                status = bet.get('status', 'pending').lower()
                status_colors = {
                    'won': QtGui.QColor(76, 175, 80),      # Green
                    'lost': QtGui.QColor(244, 67, 54),     # Red
                    'pending': QtGui.QColor(255, 167, 38), # Orange
                    'claimed': QtGui.QColor(33, 150, 243), # Blue
                    'cancelled': QtGui.QColor(158, 158, 158), # Gray
                    'closed': QtGui.QColor(158, 158, 158)     # Gray
                }
                status_item = QtWidgets.QTableWidgetItem(status.upper())
                status_item.setForeground(status_colors.get(status, QtGui.QColor(255, 167, 38)))
                self.betsTable.setItem(row, 3, status_item)
                
                # Payout
                try:
                    payout_str = str(bet.get('payout', '0'))
                    payout = float(payout_str) / 1_000_000_000
                except:
                    payout = 0.0
                
                if payout > 0:
                    payout_item = QtWidgets.QTableWidgetItem(f"+{payout:.3f}")
                    payout_item.setForeground(QtGui.QColor(76, 175, 80))  # Green
                else:
                    payout_item = QtWidgets.QTableWidgetItem("--")
                    payout_item.setForeground(QtGui.QColor(255, 255, 255, 100))
                payout_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.betsTable.setItem(row, 4, payout_item)
        
        except Exception as e:
            self._append_log(f"❌ Failed to display bets: {e}")
    
    def update_round_card(self, round_data: dict):
        """Update the round card with live data."""
        try:
            round_number = round_data.get('round_number', 0)
            up_payout = round_data.get('up_payout', 0.0)
            down_payout = round_data.get('down_payout', 0.0)
            prize_pool = round_data.get('prize_pool', 0.0)
            remaining_time = round_data.get('remaining_time', 0)
            balance = round_data.get('balance', 0.0)
            wallet_address = round_data.get('wallet_address', '')
            has_bet = round_data.get('has_bet', False)
            bet_direction = round_data.get('bet_direction', None)
            bet_amount = round_data.get('bet_amount', None)
            
            # Check if round has changed (new round)
            current_round_text = self.roundNumberLabel.text().replace("#", "")
            try:
                current_round = int(current_round_text) if current_round_text and current_round_text != "0" else 0
            except ValueError:
                current_round = 0
            
            # Update bet display based on whether bet exists
            if has_bet and bet_direction and bet_amount is not None:
                # Show bet amount in the direction button
                if bet_direction == 'UP':
                    self.upLabel.setText(
                        f'<span style="color: white;">UP</span> '
                        f'<span style="color: #4caf50;">- {bet_amount:.4f} SOL</span>'
                    )
                    self.downLabel.setText("DOWN")
                elif bet_direction == 'DOWN':
                    self.downLabel.setText(
                        f'<span style="color: white;">DOWN</span> '
                        f'<span style="color: #f44336;">- {bet_amount:.4f} SOL</span>'
                    )
                    self.upLabel.setText("UP")
            else:
                # No bet exists, show just the direction
                self.upLabel.setText("UP")
                self.downLabel.setText("DOWN")
            
            self.roundNumberLabel.setText(f"#{round_number}")
            self.upPayoutLabel.setText(f"{up_payout:.2f}x Payout")
            self.downPayoutLabel.setText(f"{down_payout:.2f}x Payout")
            self.prizePoolValueLabel.setText(f"{prize_pool:.4f} SOL")
            self.walletBalanceValueLabel.setText(f"{balance:.4f} SOL")
            
            # Validate bet amount when round changes
            self._validate_bet_amount()
            
            # Update latest bets if wallet address is provided
            if wallet_address:
                self.update_latest_bets(wallet_address)
            
            # Update Enter UP/DOWN button state based on whether bet exists
            # Only enable if bot is running AND no bet exists for current round
            worker = getattr(self, "_bot_worker", None)
            bot_running = worker is not None and worker.isRunning()
            
            if bot_running and not has_bet:
                self.enterUpButton.setEnabled(True)
                self.enterDownButton.setEnabled(True)
            else:
                self.enterUpButton.setEnabled(False)
                self.enterDownButton.setEnabled(False)
            
            # Format remaining time
            if remaining_time > 0:
                mins = remaining_time // 60
                secs = remaining_time % 60
                if mins > 0:
                    self.remainingTimeLabel.setText(f"{mins}m {secs}s")
                else:
                    self.remainingTimeLabel.setText(f"{secs}s")
                
                # Color based on time remaining
                if remaining_time <= 20:
                    self.remainingTimeLabel.setStyleSheet("color: #ff5252; font: 12pt 'Verdana' bold;")  # Red - bet time!
                elif remaining_time <= 60:
                    self.remainingTimeLabel.setStyleSheet("color: #ffa726; font: 12pt 'Verdana' bold;")  # Orange
                else:
                    self.remainingTimeLabel.setStyleSheet("color: #4caf50; font: 12pt 'Verdana' bold;")  # Green
            else:
                # Show "Locked" when remaining_time <= 0
                self.remainingTimeLabel.setText("Locked")
                self.remainingTimeLabel.setStyleSheet("color: #9e9e9e; font: 12pt 'Verdana' bold;")  # Gray
        except Exception as e:
            pass  # Silently fail if update fails
    
    def _toggle_settings_panel(self):
        """Toggle settings content visibility."""
        if self.settings_panel_visible:
            # Collapse settings content
            self.settingsContentWidget.hide()
            self.settingsToggleButton.setText("▶")
            self.settings_panel_visible = False
            # Shrink settings widget width
            self.widget.setMaximumWidth(85)
            self.widget.setMinimumWidth(85)
        else:
            # Expand settings content
            self.settingsContentWidget.show()
            self.settingsToggleButton.setText("◀")
            self.settings_panel_visible = True
            # Restore settings widget width
            self.widget.setMaximumWidth(500)
            self.widget.setMinimumWidth(500)
        
        # Update window width
        self._update_window_width()
    
    def _toggle_log_panel(self):
        """Toggle log panel width - collapse or expand."""
        if self.log_panel_visible:
            # Collapse log panel to minimal width
            self.logContainer.setMaximumWidth(40)
            self.logContainer.setMinimumWidth(40)
            self.logToggleButton.setText("▶")
            self.logPanel.hide()  # Hide text when collapsed
            self.log_panel_visible = False
        else:
            # Expand log panel to full width
            self.logContainer.setMaximumWidth(500)
            self.logContainer.setMinimumWidth(500)
            self.logToggleButton.setText("◀")
            self.logPanel.show()  # Show text when expanded
            self.log_panel_visible = True
        
        # Update window width
        self._update_window_width()
    
    def _show_place_order(self, direction: str):
        """Show the place order panel and hide round card."""
        self.roundCardPanel.hide()
        self.placeOrderPanel.show()
        
        # Store selected direction
        self.selected_direction = direction
        
        # Update direction badge and confirm button color
        self._update_order_ui_colors()
        
        # Validate bet amount to update button state
        self._validate_bet_amount()
    
    def _show_round_card(self):
        """Show the round card panel and hide place order."""
        self.placeOrderPanel.hide()
        self.roundCardPanel.show()
    
    def _toggle_order_direction(self):
        """Toggle between UP and DOWN for manual order."""
        if self.selected_direction == "UP":
            self.selected_direction = "DOWN"
        else:
            self.selected_direction = "UP"
        
        # Update UI colors
        self._update_order_ui_colors()
    
    def _update_order_ui_colors(self):
        """Update direction badge and confirm button colors based on selected direction."""
        if self.selected_direction == "UP":
            # UP styling - Green
            self.directionBadge.setText("UP")
            self.directionBadge.setStyleSheet(
                "QPushButton {"
                "background-color: #4caf50;"
                "color: white;"
                "font: 12pt 'Verdana' bold;"
                "border: none;"
                "border-radius: 8px;"
                "}"
                "QPushButton:hover {"
                "background-color: #45a049;"
                "}"
            )
            self.confirmOrderButton.setStyleSheet(
                "QPushButton {"
                "background-color: #4caf50;"
                "color: white;"
                "font: 14pt 'Verdana' bold;"
                "border: none;"
                "border-radius: 10px;"
                "}"
                "QPushButton:hover:enabled {"
                "background-color: #45a049;"
                "}"
                "QPushButton:pressed:enabled {"
                "background-color: #3d8b40;"
                "}"
                "QPushButton:disabled {"
                "background-color: rgba(76, 175, 80, 0.3);"
                "color: rgba(255, 255, 255, 0.3);"
                "}"
            )
        else:  # DOWN
            # DOWN styling - Red
            self.directionBadge.setText("DOWN")
            self.directionBadge.setStyleSheet(
                "QPushButton {"
                "background-color: #f44336;"
                "color: white;"
                "font: 12pt 'Verdana' bold;"
                "border: none;"
                "border-radius: 8px;"
                "}"
                "QPushButton:hover {"
                "background-color: #da190b;"
                "}"
            )
            self.confirmOrderButton.setStyleSheet(
                "QPushButton {"
                "background-color: #f44336;"
                "color: white;"
                "font: 14pt 'Verdana' bold;"
                "border: none;"
                "border-radius: 10px;"
                "}"
                "QPushButton:hover:enabled {"
                "background-color: #da190b;"
                "}"
                "QPushButton:pressed:enabled {"
                "background-color: #ba0c0c;"
                "}"
                "QPushButton:disabled {"
                "background-color: rgba(244, 67, 54, 0.3);"
                "color: rgba(255, 255, 255, 0.3);"
                "}"
            )
    
    def _update_amount_from_slider(self, value: int):
        """Update amount input based on slider value."""
        try:
            from decimal import Decimal, ROUND_DOWN
            
            # Get current balance
            balance_text = self.walletBalanceValueLabel.text().replace(" SOL", "")
            balance = Decimal(balance_text) if balance_text else Decimal("0.01")
            
            # Calculate available balance (balance - min_wallet_balance)
            min_wallet_balance = Decimal(str(self.minWalletBalanceSpin.value()))
            available_balance = max(Decimal("0"), balance - min_wallet_balance)
            
            # Calculate amount as percentage of available balance
            percentage = float(value) / 100.0
            amount = (Decimal(str(percentage)) * available_balance).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
            
            # Ensure minimum amount if positive
            if amount > 0:
                amount = max(Decimal("0.000000001"), amount)
            
            self.amountInput.setText(f"{amount:.9f}")
        except:
            pass
    
    def _set_percentage_amount(self, percent: str):
        """Set amount based on percentage button."""
        try:
            from decimal import Decimal, ROUND_DOWN
            
            # Get current balance
            balance_text = self.walletBalanceValueLabel.text().replace(" SOL", "")
            balance = Decimal(balance_text) if balance_text else Decimal("0.01")
            
            # Calculate available balance (balance - min_wallet_balance)
            min_wallet_balance = Decimal(str(self.minWalletBalanceSpin.value()))
            available_balance = max(Decimal("0"), balance - min_wallet_balance)
            
            if percent == "Max":
                # Max = 100% of available balance
                amount = available_balance
                slider_value = 100
            else:
                # Calculate as percentage of available balance
                percentage_value = int(percent.replace("%", ""))
                percentage = float(percentage_value) / 100.0
                amount = (Decimal(str(percentage)) * available_balance).quantize(Decimal("0.000000001"), rounding=ROUND_DOWN)
                slider_value = percentage_value
            
            # Ensure minimum amount if positive
            if amount > 0:
                amount = max(Decimal("0.000000001"), amount)
            
            # Update input text first
            self.amountInput.setText(f"{amount:.9f}")
            
            # Block signals while updating slider to prevent triggering valueChanged
            self.amountSlider.blockSignals(True)
            self.amountSlider.setValue(slider_value)
            self.amountSlider.blockSignals(False)
        except:
            pass
    
    def _validate_bet_amount(self):
        """Validate bet amount and enable/disable confirm button."""
        try:
            amount_text = self.amountInput.text().strip()
            if not amount_text:
                self.confirmOrderButton.setEnabled(False)
                return
            
            amount = float(amount_text)
            
            # Get current round number
            round_text = self.roundNumberLabel.text().replace("#", "")
            current_round = int(round_text) if round_text and round_text != "0" else 0
            
            if current_round <= 0:
                # No active round, disable button
                self.confirmOrderButton.setEnabled(False)
                return
            
            # Determine min bet amount based on even/odd round
            is_even = current_round % 2 == 0
            min_bet = self.evenMinBetSpin.value() if is_even else self.oddMinBetSpin.value()
            
            # Check if amount is less than minimum bet
            if amount < min_bet:
                self.confirmOrderButton.setEnabled(False)
                return
            
            # Get current balance
            balance_text = self.walletBalanceValueLabel.text().replace(" SOL", "").strip()
            try:
                balance = float(balance_text) if balance_text else 0.0
            except ValueError:
                balance = 0.0
            
            # Get minimum wallet balance to keep
            min_wallet_balance = self.minWalletBalanceSpin.value()
            
            # Check if balance is sufficient (balance >= amount + min_wallet_balance)
            if balance < amount + min_wallet_balance:
                self.confirmOrderButton.setEnabled(False)
                return
            
            # All checks passed - enable button
            self.confirmOrderButton.setEnabled(True)
                
        except (ValueError, AttributeError):
            # Invalid amount or widgets not initialized
            self.confirmOrderButton.setEnabled(False)
    
    def _confirm_manual_bet(self):
        """Confirm and place manual bet immediately."""
        try:
            amount = float(self.amountInput.text())
            direction = self.selected_direction
            
            # Validate amount
            if amount <= 0:
                self._append_log(f"❌ Amount must be greater than 0")
                return
            
            # Send manual bet to bot worker if running
            worker = getattr(self, "_bot_worker", None)
            if worker is not None and worker.isRunning():
                # Get current round from UI
                round_text = self.roundNumberLabel.text().replace("#", "")
                try:
                    current_round = int(round_text) if round_text != "0" else None
                    
                    if current_round and current_round > 0:
                        # Place manual bet immediately
                        worker.place_manual_bet(current_round, direction, amount)
                        self._append_log(f"⏳ Processing manual bet...")
                    else:
                        self._append_log(f"⚠️  No active round available")
                except Exception as e:
                    self._append_log(f"⚠️  Could not place bet: {e}")
            else:
                self._append_log(f"⚠️  Bot is not running. Start the bot first.")
            
            # Go back to round card
            self._show_round_card()
        except ValueError:
            self._append_log(f"❌ Invalid amount entered. Please enter a number.")
    
    def _update_window_width(self):
        """Calculate and set window width based on visible panels."""
        # Settings panel width (collapsed or expanded)
        if self.settings_panel_visible:
            width = 500
        else:
            width = 85  # Just the top bar with buttons
        
        # Round card panel (always shown)
        width += 380
        
        # Log panel (collapsed or expanded)
        if self.log_panel_visible:
            width += 500  # Expanded log panel
        else:
            width += 40  # Collapsed log panel
        
        self.setFixedWidth(width)
        QtCore.QTimer.singleShot(50, lambda: self.setMaximumWidth(16777215))
    
    def _show_notification(self, message: str, notification_type: str = "success"):
        """Show a notification banner and system notification.
        
        Args:
            message: The notification message
            notification_type: 'success', 'error', or 'info'
        """
        # Set colors and icons based on type
        if notification_type == "success":
            bg_color = "#4caf50"  # Green
            icon = "✓"
            title = "Success"
        elif notification_type == "error":
            bg_color = "#f44336"  # Red
            icon = "✗"
            title = "Error"
        else:  # info
            bg_color = "#2196f3"  # Blue
            icon = "ℹ"
            title = "Information"
        
        # Update notification style and content
        self.notificationWidget.setStyleSheet(
            f"QWidget {{"
            f"background-color: {bg_color};"
            f"border-radius: 0px;"
            f"}}"
        )
        self.notificationIcon.setText(icon)
        self.notificationLabel.setText(message)
        
        # Show notification with animation
        self.notificationWidget.setMaximumHeight(50)
        
        # Auto-hide after 4 seconds
        self.notificationTimer.start(4000)
        
        # Also show system notification
        if SYSTEM_NOTIFICATIONS_AVAILABLE:
            try:
                system_notification.notify(
                    title=f"Fortuva Bot - {title}",
                    message=message,
                    app_name="Fortuva Bot",
                    timeout=4  # Duration in seconds
                )
            except Exception as e:
                # Silently fail if system notification doesn't work
                print(f"System notification failed: {e}")
    
    def _hide_notification(self):
        """Hide the notification banner."""
        self.notificationWidget.setMaximumHeight(0)



if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    login_form = FortuvaForm()
    login_form.show()

    sys.exit(app.exec_())
