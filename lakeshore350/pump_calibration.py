#!/usr/bin/env python3
"""
Pump Calibration Module for Lakeshore 350

This module provides voltage to temperature conversion for the GL7 3-pump and 4-pump diodes
using the calibration data from pumps_switches_cal.csv.
"""

import csv
import os
from scipy.interpolate import interp1d
import numpy as np

class PumpCalibration:
    def __init__(self, calibration_file=None):
        """Initialize the pump calibration with data from CSV file"""
        # Use absolute path if not provided
        if calibration_file is None:
            calibration_file = '/home/kids/lakeshore350-python/gl7_calibrations/pumps_switches_cal.csv'
        self.calibration_file = calibration_file
        self.temperatures = []
        self.voltages = []
        self.interpolator = None
        self._load_calibration_data()
        self._create_interpolator()
    
    def _load_calibration_data(self):
        """Load calibration data from CSV file"""
        cal_file_path = self.calibration_file
        try:
            with open(cal_file_path, 'r') as file:
                reader = csv.reader(file)
                # Skip header row
                next(reader)
                for row in reader:
                    if len(row) >= 2 and row[0].strip() and row[1].strip():
                        try:
                            temp = float(row[0].strip())
                            voltage = float(row[1].strip())
                            self.temperatures.append(temp)
                            self.voltages.append(voltage)
                        except ValueError:
                            continue
        except FileNotFoundError:
            raise FileNotFoundError(f"Pump calibration file not found: {cal_file_path}")
        except Exception as e:
            raise Exception(f"Error loading pump calibration data: {e}")
    
    def _create_interpolator(self):
        """Create interpolation function for voltage to temperature conversion"""
        if len(self.temperatures) < 2:
            raise ValueError("Not enough calibration data points")
        
        # Sort by voltage for interpolation (voltage increases as temperature decreases)
        sorted_data = sorted(zip(self.voltages, self.temperatures))
        sorted_voltages, sorted_temperatures = zip(*sorted_data)
        
        # Create interpolator
        self.interpolator = interp1d(
            sorted_voltages, 
            sorted_temperatures,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )
        
        # Store min/max for range checking
        self.min_voltage = min(sorted_voltages)
        self.max_voltage = max(sorted_voltages)
        self.min_temperature = min(sorted_temperatures)
        self.max_temperature = max(sorted_temperatures)
    
    def convert_voltage_to_temperature(self, voltage):
        """
        Convert pump voltage to temperature using calibration data
        
        Args:
            voltage (float): Voltage in volts
            
        Returns:
            float: Temperature in Kelvin
        """
        if self.interpolator is None:
            raise ValueError("Calibration interpolator not initialized")
        
        if not isinstance(voltage, (int, float)):
            raise ValueError("Voltage must be a number")
        
        # Convert to temperature
        temperature = float(self.interpolator(voltage))
        
        # Warning for extrapolation
        if voltage < self.min_voltage or voltage > self.max_voltage:
            print(f"Warning: pump voltage {voltage:.3f}V is outside calibration range "
                  f"({self.min_voltage:.3f}V to {self.max_voltage:.3f}V)")
        
        return temperature

# Global calibration instance
_calibration_instance = None

def get_pump_calibration():
    """Get or create the global pump calibration instance"""
    global _calibration_instance
    if _calibration_instance is None:
        _calibration_instance = PumpCalibration()
    return _calibration_instance

def convert_pump_voltage_to_temperature(voltage):
    """
    Convert pump voltage to temperature using calibration data
    
    Args:
        voltage (float): Voltage in volts
        
    Returns:
        float: Temperature in Kelvin
    """
    calibration = get_pump_calibration()
    return calibration.convert_voltage_to_temperature(voltage)

if __name__ == "__main__":
    # Test the calibration
    print("Testing pump calibration...")
    
    # Test with some known values
    test_voltages = [0.5, 1.0, 1.5, 1.7]
    
    for voltage in test_voltages:
        try:
            temp = convert_pump_voltage_to_temperature(voltage)
            print(f"Pump: {voltage}V → {temp:.3f}K")
        except Exception as e:
            print(f"Error converting {voltage}V: {e}")
