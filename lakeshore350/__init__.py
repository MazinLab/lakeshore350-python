"""
Lake Shore 350 Temperature Controller Interface

A modular Python interface for the Lake Shore 350 Temperature Controller.
Currently supports temperature reading from all inputs and channels.
Designed to be extensible for future relay and output control.
"""

from .temperature import TemperatureReader

__version__ = "0.2.0"
__all__ = ["TemperatureReader"]
