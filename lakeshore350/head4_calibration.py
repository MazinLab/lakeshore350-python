#!/usr/bin/env python3
import csv
import os
import numpy as np
from scipy.interpolate import interp1d

# Calibration for 4-head thermometer
# CSV Format: Resistance (Ohms), Temperature (K)
# Generated from gl7_calibrations/4_head_cal.csv

class FourHeadCalibration:
    def __init__(self, cal_path=None):
        if cal_path is None:
            cal_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gl7_calibrations', '4_head_cal.csv')
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
        self.temperatures = np.array(self.temperatures)
        self.resistances = np.array(self.resistances)
        self.interpolator = interp1d(self.resistances, self.temperatures, kind='linear', bounds_error=False, fill_value=(self.temperatures[0], self.temperatures[-1]))

    def resistance_to_temperature(self, resistance):
        if not isinstance(resistance, (int, float)) or resistance <= 0:
            return None
        return float(self.interpolator(resistance))

# Global function to call calibration, used in main.py
def convert_4head_resistance_to_temperature(resistance):
    cal = FourHeadCalibration()
    return cal.resistance_to_temperature(resistance)
