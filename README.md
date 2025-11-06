# Fortuva Bot - Solana Prediction Bot

[![Python: 3.x](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=gold)](https://www.python.org/downloads)
[![PyQt: 5.15.0](https://img.shields.io/badge/pyqt-5.15.0-darkgreen?logo=qt&logoColor=green)](https://pypi.org/project/PyQt5)
[![Solana](https://img.shields.io/badge/Solana-Blockchain-purple?logo=solana)](https://solana.com)

A sophisticated GUI application for automated Solana blockchain prediction betting with PyQt5.

---

## ✨ Features

- 🎨 **Modern GUI**: Beautiful, dark-themed interface built with PyQt5
- 🔐 **Wallet Support**: Import via keypair file, seed phrase, or private key
- ⚙️ **Configurable Strategies**: Separate settings for even/odd round betting
- 🤖 **Automated Betting**: Set it and forget it with auto-bet mode
- 📊 **Live Stats**: Real-time round info, payouts, and wallet balance
- 📈 **Bet History**: Track your bets with status and payout information
- 🔔 **Notifications**: In-app and system notifications for important events
- 💾 **Persistent Settings**: Your configuration is saved automatically
- 🎯 **Manual Betting**: Take control with manual bet placement
- 📱 **Collapsible Panels**: Maximize screen space by hiding panels

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FORTUVA_AUTOMATION_ENGINE_GUI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

---

## 📥 Download Pre-Built Releases

Don't want to install Python or build from source? Download pre-built executables for your platform!

### Available Releases

🔗 **[View All Releases on GitHub](../../releases)**

#### Windows
📦 **[Download Windows Release (v1.0.0)](../../releases/download/v1.0.0/v1.0.0-windows.zip)**
- Extract the ZIP file
- Run `FortuvaBot.exe`
- No Python installation required!

#### Linux
📦 **[Download Linux Release (v1.0.0)](../../releases/download/v1.0.0/v1.0.0-linux.zip)**
- Extract the ZIP file
- Install dependencies: `./install_linux_deps.sh`
- Run `./FortuvaBot`
- See [Linux User Guide](README_LINUX_USERS.md) for detailed instructions

### What's Included

Each release contains:
- ✅ Standalone executable (no Python needed)
- ✅ All dependencies bundled
- ✅ Application icons and resources
- ✅ Linux: Dependency installation script

### First-Time Setup

1. Download the appropriate release for your OS
2. Extract the ZIP file to your preferred location
3. **Linux users**: Run the dependency installer first
4. Launch the application
5. Configure your wallet and settings
6. Start betting!

---

## 📦 Building Executables

Want to create standalone executables for distribution? We've got you covered!

### Quick Build Commands

```bash
# Install PyInstaller
pip install pyinstaller

# Auto-detect and build for your OS
python build_scripts/build_all.py
```

**Or platform-specific:**

```bash
# Windows
python build_scripts/build_windows.py

# macOS
python build_scripts/build_macos.py

# Linux (binary)
python build_scripts/build_linux.py

# Linux (AppImage - recommended)
python build_scripts/build_linux.py
python build_scripts/build_appimage.py
```

### Output

- **Windows**: `dist/FortuvaBot/FortuvaBot.exe`
- **macOS**: `dist/FortuvaBot.app`
- **Linux**: `dist/FortuvaBot/FortuvaBot` or `dist/FortuvaBot-x86_64.AppImage`

### Detailed Build Instructions

See comprehensive guides:
- 📘 [Quick Start Guide](BUILDING_EXECUTABLES.md)
- 📕 [Detailed Guide](build_executable.md)
- 📗 [Build Workflow](BUILD_WORKFLOW.md)
- 📙 [Build Scripts README](build_scripts/README.md)

### Linux-Specific Notes

**For Users Running the Linux Executable:**

The Linux executable requires Qt/X11 system libraries to be installed:

```bash
# Automatic installation (recommended)
./install_linux_deps.sh

# Or manual installation (Ubuntu/Debian)
sudo apt-get install -y libxcb-xinerama0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxkbcommon-x11-0 libxkbcommon0 libdbus-1-3 \
    libgl1-mesa-glx libglib2.0-0
```

**Documentation:**
- 📘 [Linux User Guide](README_LINUX_USERS.md) - Simple installation instructions
- 🔧 [Linux Troubleshooting](LINUX_TROUBLESHOOTING.md) - Detailed troubleshooting
- 🛠️ [Linux Build Fix](LINUX_BUILD_FIX.md) - Technical details about Qt plugin fix
- 🎨 [Linux UI Fix](LINUX_UI_FIX.md) - UI layout fixes for Linux

**Common Issues:**
- **"Could not load Qt platform plugin 'xcb'"** → Install system dependencies (see above)
- **Table cut off/no scrollbar** → Fixed in latest version
- **Distribution compatibility** → Use AppImage for maximum compatibility across distributions

---

## 💻 Usage

### 1. Wallet Setup

**Option A: Keypair File**
- Click "Browse" and select your keypair JSON file
- Private key will auto-populate

**Option B: Manual Entry**
- Enter seed phrase (space-separated words)
- Or enter private key (base58 or hex format)
- Or paste keypair JSON array

### 2. Configure Bot Settings

#### Network
- **RPC URL**: Solana RPC endpoint (default: mainnet-beta)

#### Timing
- **Bet Time**: Seconds before round ends to place bet
- **Interval Time**: Seconds between checks

#### Strategy (Even/Odd Rounds)
- **Min/Max Bet**: Bet amount range in SOL
- **Multiplier**: Target payout multiplier
- **Mode**: GENERAL or PAYOUT strategy
- **Direction**: UP or DOWN prediction

#### Options
- **Considering Old Bets**: Factor in previous bets
- **Auto Bet**: Enable automatic betting

### 3. Start Bot

1. Click "Set" to save configuration
2. Click "Start" to begin
3. Monitor logs and round info
4. Use "Enter UP/DOWN" for manual bets

### 4. Features

- **Collapsible Panels**: Click ◀/▶ to hide settings or logs
- **Manual Betting**: Click "Enter UP" or "Enter DOWN" when ready
- **Live Updates**: Round info updates automatically
- **Bet History**: View recent bets in the table

---

## 🛠️ Configuration

### Settings Location

Settings are automatically saved to:
- **Windows**: `%APPDATA%\modern-login\bot-config.ini`
- **macOS**: `~/Library/Preferences/com.modern-login.bot-config.plist`
- **Linux**: `~/.config/modern-login/bot-config.conf`

### Configuration Options

All settings can be configured via the GUI:

```
Network:
  - RPC URL

Timing:
  - Bet Time (10-180s)
  - Interval Time (1s~)
  - Min Wallet Balance

Even Round Strategy:
  - Min/Max Bet Amount
  - Multiplier
  - Mode (GENERAL/PAYOUT)
  - Direction (UP/DOWN)

Odd Round Strategy:
  - Min/Max Bet Amount
  - Multiplier
  - Mode (GENERAL/PAYOUT)
  - Direction (UP/DOWN)

Options:
  - Considering Old Bets
  - Auto Bet
```

---

## 📁 Project Structure

```
modern-login/
├── bot/                      # Bot logic modules
│   ├── api.py               # Fortuva API client
│   ├── betting_service.py   # Betting logic
│   ├── blockchain.py        # Solana blockchain interaction
│   ├── cancel_service.py    # Bet cancellation
│   ├── claim_service.py     # Reward claiming
│   ├── close_service.py     # Bet closing
│   └── worker.py            # Background worker thread
├── build_scripts/           # Build automation
│   ├── build_all.py         # Universal build
│   ├── build_windows.py     # Windows build
│   ├── build_macos.py       # macOS build
│   ├── build_linux.py       # Linux build
│   └── build_appimage.py    # AppImage build
├── icons/                   # UI icons
├── img/                     # Images and assets
├── ts/                      # TypeScript version (reference)
├── main.py                  # Main application
├── modern-login*.spec       # PyInstaller specs
├── requirements.txt         # Python dependencies
└── requirements-build.txt   # Build dependencies
```

---

## 🔧 Development

### Running from Source

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Building Resources

If you modify `icons.qrc`:

```bash
pyrcc5 icons.qrc -o icons_rc.py
```

---

## 🐛 Troubleshooting

### Application Won't Start

**Issue**: Missing dependencies
```bash
pip install -r requirements.txt
```

**Issue**: Qt platform plugin errors
```bash
# Linux
sudo apt install libxcb-xinerama0 libqt5widgets5
```

### Can't Import Wallet

**Issue**: Invalid keypair format
- Ensure JSON file contains array of 64 bytes
- Check seed phrase has correct number of words
- Verify private key format (base58/hex)

### Bot Not Placing Bets

**Issue**: Insufficient balance
- Check wallet balance in UI
- Ensure balance > min wallet balance setting

**Issue**: Auto bet disabled
- Verify "Auto Bet" checkbox is checked
- Click "Set" to save settings

### Build Issues

See [Troubleshooting Section](BUILDING_EXECUTABLES.md#-troubleshooting) in build guide.

---

## 📋 Requirements

### Runtime Requirements

- Python 3.8+
- PyQt5 5.15+
- Solana Python SDK
- Internet connection (for RPC)

### Build Requirements

- PyInstaller 6.0+
- Platform-specific tools (see build guides)

---

## 🔒 Security

⚠️ **Important Security Notes**:

1. **Never share your private keys or seed phrases**
2. **Use a dedicated wallet for betting** (don't use your main wallet)
3. **Start with small amounts** to test the bot
4. **Review all settings** before starting
5. **Monitor bot activity** regularly
6. **Keep your Python environment updated**
7. **Be cautious of RPC endpoints** (use trusted sources)

### Best Practices

- ✅ Use environment variables for sensitive data
- ✅ Test on devnet first
- ✅ Keep software updated
- ✅ Backup your wallet regularly
- ✅ Use strong passwords
- ✅ Enable system notifications

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📞 Support

- 📧 Issues: Use GitHub Issues
- 💬 Discussions: Use GitHub Discussions
- 📖 Documentation: See guides in repository

---

## 🙏 Acknowledgments

- PyQt5 for the GUI framework
- Solana for the blockchain platform
- Original modern-login template
- All contributors and testers

---

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk. Cryptocurrency betting involves financial risk. Always:

- Start with small amounts
- Never bet more than you can afford to lose
- Understand the risks involved
- Comply with local laws and regulations
- Test thoroughly before production use

The developers are not responsible for any financial losses incurred while using this software.

---

## 📊 Statistics

Built with ❤️ using:
- Python 🐍
- PyQt5 🎨
- Solana ⚡
- AnchorPy ⚓

---

**Happy Betting! 🎲**

Remember to bet responsibly and only what you can afford to lose.

---

[![Python: 3.x](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=gold)](https://www.python.org/downloads)
[![PyQt: 5.15.0](https://img.shields.io/badge/pyqt-5.15.0-darkgreen?logo=qt&logoColor=green)](https://pypi.org/project/PyQt5)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
