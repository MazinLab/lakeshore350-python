# Lake Shore 350 Python Interface

Python interface for reading temperatures from the Lakeshore 350 Temperature Controller.

## Installation

Clone this repository and install:
```bash
git clone https://github.com/MazinLab/lakeshore350-python
python3 -m venv lakeshore350-env
source lakeshore350-env/bin/activate  
cd lakeshore350-python
pip install -e .
```

## Usage
This repo is intended to be functional through simple command line arguments without running any scripts individually. 
To see a comprehensive list of command line functionality, execute ```lakeshore350 --help```

### Basic Checks
Read all inputs (A-C, D1-D5)
```bash
lakeshore350 --all
```

Get device information:
```bash
lakeshore350 --info
```
### Setting and Querying Heaters/Switches
To query the heater status,
```bash
lakeshore350 --outputs-query-all
```
Returns a list of queries for all outputs

To set output parameters (i.e. max current, mode),
```bash
lakeshore350 --outputs-set-params
```

To set heater range,
```bash
lakeshore350 --outputs-set-range
```

To set output percentage,
```bash
lakeshore350 --outputs-set OUTPUT PERCENT
```
## Requirements

- Python 3.7+
- pyserial
- Lake Shore 350 connected via USB serial




