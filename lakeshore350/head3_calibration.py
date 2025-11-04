#!/usr/bin/env python3
import csv
import os
import numpy as np
from scipy.interpolate import interp1d

# Calibration for 3-head thermometer
# CSV Format: Temperature (K), Resistance (Ohms)
# Calibration file: gl7_calibrations/3_head_cal.csv

class ThreeHeadCalibration:
    def __init__(self, cal_path=None):
        # Try project directory first
        default_project_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gl7_calibrations', '3_head_cal.csv')
        cwd_path = os.path.join(os.getcwd(), 'gl7_calibrations', '3_head_cal.csv')
        if cal_path is None:
            if os.path.exists(cwd_path):
                cal_path = cwd_path
            elif os.path.exists(default_project_path):
                cal_path = default_project_path
            else:
                # Print debug info and raise error with both paths
                print(f"Calibration file not found. Tried: {cwd_path} and {default_project_path}")
                raise FileNotFoundError(f"Calibration file not found. Tried: {cwd_path} and {default_project_path}")
        self.resistances = []
        self.temperatures = []
        with open(cal_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                try:
                    t = float(row[0])
                    r = float(row[1])
                    self.temperatures.append(t)
                    self.resistances.append(r)
                except Exception:
                    continue
        self.resistances = np.array(self.resistances)
        self.temperatures = np.array(self.temperatures)
        self.interpolator = interp1d(self.resistances, self.temperatures, kind='linear', bounds_error=False, fill_value=(self.temperatures[0], self.temperatures[-1]))

    def resistance_to_temperature(self, resistance):
        if not isinstance(resistance, (int, float)) or resistance <= 0:
            return None
        return float(self.interpolator(resistance))

# Global function to call calibration, used in main.py
def convert_3head_resistance_to_temperature(resistance):
    cal = ThreeHeadCalibration()
    return cal.resistance_to_temperature(resistance)
