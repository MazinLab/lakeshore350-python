# Lake Shore 350 Python Interface

A simple Python interface for reading temperatures from the Lake Shore 350 Temperature Controller.

## Installation

Clone this repository and install:
```bash
git clone https://github.com/MazinLab/lakeshore350-python
cd lakeshore350-python
pip install -e .
```

## Usage

### Command Line

Read all channels:
```bash
lakeshore350 --all
```

Read a specific channel:
```bash
lakeshore350 --channel A
```

Get device information:
```bash
lakeshore350 --info
```

### Python Script

```python
from lakeshore350_simple import LakeShore350

# Connect to device
ls = LakeShore350("/dev/ttyUSB0")

# Read channel A
temp_a = ls.read_temperature("A")
print(f"Channel A: {temp_a}")

# Read all channels
all_temps = ls.read_all_temperatures()
for channel, temp in all_temps.items():
    print(f"Channel {channel}: {temp}")

# Close connection
ls.close()
```

## Features

- Reads temperature from channels A, B, C, D
- Handles over-range conditions (displays "T_OVER")
- Simple command-line interface
- Handles communication errors gracefully

## Requirements

- Python 3.7+
- pyserial
- Lake Shore 350 connected via USB serial  




