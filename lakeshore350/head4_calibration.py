#!/usr/bin/env python3
"""
4-Head Calibration Module for Lakeshore 350

This module provides resistance to temperature conversion for the GL7 4-head thermometer
using the calibration data from 4_head_cal.csv.
"""

import csv
import os
from scipy.interpolate import interp1d
import numpy as np

class FourHeadCalibration:
    def __init__(self, calibration_file='4_head_cal.csv'):
        """Initialize the 4-head calibration with data from CSV file"""
        self.calibration_file = calibration_file
        self.temperatures = []
        self.resistances = []
        self.interpolator = None
        self._load_calibration_data()
        self._create_interpolator()
    
    def _load_calibration_data(self):
        """Load calibration data from CSV file"""
        # Get the directory of this script, then go to calibration directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cal_file_path = os.path.join(script_dir, "calibration", self.calibration_file)
        
        try:
            with open(cal_file_path, 'r') as file:
                reader = csv.reader(file)
                # Skip header row
                next(reader)
                
                for row in reader:
                    if len(row) >= 2 and row[0].strip() and row[1].strip():
                        try:
                            temp = float(row[0].strip())
                            resistance = float(row[1].strip())
                            self.temperatures.append(temp)
                            self.resistances.append(resistance)
                        except ValueError:
                            # Skip rows with invalid data
                            continue
            
            print(f"Loaded 4-head calibration with {len(self.temperatures)} data points")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"4-head calibration file not found: {cal_file_path}")
        except Exception as e:
            raise Exception(f"Error loading 4-head calibration data: {e}")
    
    def _create_interpolator(self):
        """Create interpolation function for resistance to temperature conversion"""
        if len(self.temperatures) < 2:
            raise ValueError("Not enough calibration data points")
        
        # Sort by resistance for interpolation (resistance decreases as temperature increases)
        sorted_data = sorted(zip(self.resistances, self.temperatures))
        sorted_resistances, sorted_temperatures = zip(*sorted_data)
        
        # Create interpolator
        self.interpolator = interp1d(
            sorted_resistances, 
            sorted_temperatures,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )
        
        # Store min/max for range checking
        self.min_resistance = min(sorted_resistances)
        self.max_resistance = max(sorted_resistances)
        self.min_temperature = min(sorted_temperatures)
        self.max_temperature = max(sorted_temperatures)
    
    def convert_resistance_to_temperature(self, resistance):
        """
        Convert 4-head resistance to temperature using calibration data
        
        Args:
            resistance (float): Resistance in ohms
            
        Returns:
            float: Temperature in Kelvin
        """
        if self.interpolator is None:
            raise ValueError("Calibration interpolator not initialized")
        
        if not isinstance(resistance, (int, float)) or resistance <= 0:
            raise ValueError("Resistance must be a positive number")
        
        # Convert to temperature
        temperature = float(self.interpolator(resistance))
        
        # Warning for extrapolation
        if resistance < self.min_resistance or resistance > self.max_resistance:
            print(f"Warning: 4-head resistance {resistance:.1f}Ω is outside calibration range "
                  f"({self.min_resistance:.1f}Ω to {self.max_resistance:.1f}Ω)")
        
        return temperature

# Global calibration instance
_calibration_instance = None

def get_4head_calibration():
    """Get or create the global 4-head calibration instance"""
    global _calibration_instance
    if _calibration_instance is None:
        _calibration_instance = FourHeadCalibration()
    return _calibration_instance

def convert_4head_resistance_to_temperature(resistance):
    """
    Convert 4-head resistance to temperature using calibration data
    
    Args:
        resistance (float): Resistance in ohms
        
    Returns:
        float: Temperature in Kelvin
    """
    calibration = get_4head_calibration()
    return calibration.convert_resistance_to_temperature(resistance)

if __name__ == "__main__":
    # Test the calibration
    print("Testing 4-head calibration...")
    
    # Test with some known values
    test_resistances = [1073.0, 2000.0, 5000.0, 10000.0]
    
    for resistance in test_resistances:
        try:
            temp = convert_4head_resistance_to_temperature(resistance)
            print(f"4-head: {resistance}Ω → {temp:.3f}K")
        except Exception as e:
            print(f"Error converting {resistance}Ω: {e}")
