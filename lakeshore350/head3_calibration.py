#!/usr/bin/env python3
"""
3-Head calibration module for converting resistance to temperature using the 3-head calibration table.
"""

import csv
import os
import numpy as np
from scipy.interpolate import interp1d

class ThreeHeadCalibration:
    """Converts 3-head resistance readings to temperature using calibration data."""
    
    def __init__(self):
        self.temperatures = []
        self.resistances = []
        self.interpolator = None
        self.load_3head_calibration()
    
    def load_3head_calibration(self):
        """Load the 3-head calibration file."""
        # Script located in lakeshore350 directory, calibration files in calibration directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load 3-head calibration from calibration directory
        three_head_file = os.path.join(script_dir, "calibration", "3_head_cal.csv")
        if os.path.exists(three_head_file):
            self.load_calibration_file(three_head_file)
        else:
            print(f"Warning: 3-head calibration file not found at {three_head_file}")
    
    def load_calibration_file(self, file_path):
        """Load the 3-head calibration file."""
        temperatures = []
        resistances = []
        
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                # Skip header row
                next(reader)
                
                for row in reader:
                    if len(row) >= 2:
                        try:
                            temp = float(row[0])
                            resistance = float(row[1])
                            temperatures.append(temp)
                            resistances.append(resistance)
                        except ValueError:
                            # Skip rows that can't be converted to float
                            continue
            
            # Store calibration data
            self.temperatures = np.array(temperatures)
            self.resistances = np.array(resistances)
            
            # Create interpolation function (resistance -> temperature)
            # Sort by resistance for proper interpolation
            sorted_indices = np.argsort(resistances)
            sorted_resistances = self.resistances[sorted_indices]
            sorted_temperatures = self.temperatures[sorted_indices]
            
            # Create interpolator
            self.interpolator = interp1d(
                sorted_resistances, 
                sorted_temperatures,
                kind='linear',
                bounds_error=False,
                fill_value=(sorted_temperatures[0], sorted_temperatures[-1])
            )
            
        except Exception as e:
            print(f"Error loading 3-head calibration file {file_path}: {e}")
    
    def resistance_to_temperature(self, resistance_ohms):
        """Convert 3-head resistance to temperature."""
        if self.interpolator is None:
            return None
        
        try:
            temperature = float(self.interpolator(resistance_ohms))
            return temperature
        except Exception as e:
            print(f"Error converting 3-head resistance {resistance_ohms} to temperature: {e}")
            return None
    
    def get_calibration_range(self):
        """Get the valid resistance range for 3-head sensor."""
        if len(self.resistances) == 0:
            return None
        
        return {
            'min_resistance': float(np.min(self.resistances)),
            'max_resistance': float(np.max(self.resistances)),
            'min_temperature': float(np.min(self.temperatures)),
            'max_temperature': float(np.max(self.temperatures))
        }
    
    def is_valid_resistance(self, resistance_ohms):
        """Check if resistance is within calibration range."""
        range_info = self.get_calibration_range()
        if not range_info:
            return False
        
        return (range_info['min_resistance'] <= resistance_ohms <= range_info['max_resistance'])

# Global calibration instance
_calibration = None

def get_3head_calibration():
    """Get the global 3-head calibration instance."""
    global _calibration
    if _calibration is None:
        _calibration = ThreeHeadCalibration()
    return _calibration

def convert_3head_resistance_to_temperature(resistance_ohms):
    """Convert 3-head resistance to temperature."""
    calibration = get_3head_calibration()
    return calibration.resistance_to_temperature(resistance_ohms)
