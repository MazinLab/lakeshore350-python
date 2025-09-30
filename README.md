# Lake Shore 350 Python Interface

Python interface for reading temperatures from the Lakeshore 350 Temperature Controller.

** Repo still in progress, no heater capability yet 

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

### Command Line

Read all channels and inputs:
```bash
lakeshore350 --all
```

Read a specific channel:
```bash
lakeshore350 --channel A
```


Read a specific input:
```bash
lakeshore350 --input 2
```

Get device information:
```bash
lakeshore350 --info
```

Get list of available commands:
```bash
lakeshore350 --help
```
## Requirements

- Python 3.7+
- pyserial
- Lake Shore 350 connected via USB serial




