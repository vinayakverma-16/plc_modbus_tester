# PLC Test Utility

A professional open-source Modbus communication and PLC testing tool for Linux, Windows, and macOS.

![Screenshot Placeholder](docs/screenshot.png)

## Features

### Modbus Communication
- Modbus TCP, RTU, and ASCII
- RS232 and RS485 support
- Read/Write coils and registers (FC01-FC06, FC15, FC16)
- Continuous polling with configurable intervals
- Auto-reconnect and retry

### Register View
- Professional spreadsheet-like table
- Decimal, Hex, Binary, Float, Signed, Unsigned, ASCII display
- Change highlighting
- Search and filter
- CSV export

### Engineering Utilities
- Standard, Scientific, and Programmer calculators
- Numeric base converter (Dec/Hex/Bin/Oct)
- IEEE754 float/double converter
- ASCII/UTF-8 converter
- CRC-16/CRC-32 calculator

### Bit Tool
- Bit viewer with toggle
- Shift left/right
- Byte swap, word swap, endian converter
- Mask generator

### Packet Monitor
- Real-time TX/RX display
- Timestamps, hex, ASCII, CRC
- Error logging
- Save to CSV

### PLC Testing Tools
- Force/Toggle coil
- Write register
- Increment values
- Random generator
- Stress test (automated write bursts)

### Utilities
- Ping PLC
- TCP port test
- Serial port scanner
- Network interface scanner
- Session save/load
- PLC profile manager

### Quality of Life
- Dark/Light theme toggle
- Dockable, resizable panels
- Logging (TXT/CSV/JSON with rotation)
- Keyboard shortcuts
- Register favorites
- Recent connections

## Installation

### Prerequisites
- Python 3.12+
- pip

### Quick Install

```bash
git clone https://github.com/yourusername/plc-test-utility.git
cd plc-test-utility
chmod +x install.sh
./install.sh
```

### Manual Install

```bash
git clone https://github.com/yourusername/plc-test-utility.git
cd plc-test-utility
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
# Using the script
./run.sh

# Or manually
source venv/bin/activate
python main.py
```

## Building

### AppImage (Linux)
Future support planned.

### Debian Package
Future support planned.

## Project Structure

```
plc-test-utility/
├── main.py                 # Application entry point
├── ui/                     # UI components (PySide6)
│   ├── main_window.py      # Main window with dock widgets
│   ├── connection_panel.py # Modbus connection settings
│   ├── register_view.py    # Register data table
│   ├── packet_monitor.py   # TX/RX packet log
│   ├── calculator_panel.py # Standard/Scientific/Programmer
│   ├── converter_panel.py  # Numeric/IEEE754/ASCII/CRC
│   ├── bit_tool_panel.py   # Bit manipulation tools
│   ├── plc_testing_panel.py# PLC testing utilities
│   ├── logging_panel.py    # Log configuration
│   └── utility_panel.py    # Network utilities
├── modbus/                 # Modbus communication layer
├── calculators/            # Calculator engines
├── converters/             # Data converters
├── logger/                 # Log manager
├── utils/                  # Utility functions
├── assets/                 # QSS themes (dark/light)
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md).

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Plugin system
- [ ] Graph view / real-time register plotting
- [ ] Memory map viewer
- [ ] Register watch list
- [ ] Auto-save session
- [ ] AppImage packaging
- [ ] Debian package
- [ ] Multiple poll windows
- [ ] CSV import
- [ ] Keyboard shortcut customization

## License

Distributed under the MIT License. See `LICENSE` for more information.
