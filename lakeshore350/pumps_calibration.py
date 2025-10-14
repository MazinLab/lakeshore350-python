# Calibration for 3 & 4 Pump and 3 & 4 Switch diodes
# CSV Format: Voltage (V), Temperature (K)
# Generated from gl7_calibrations/pumps_switches_cal.csv

import numpy as np
from scipy.interpolate import interp1d
import os
import csv


class PumpsCalibrator:
    def __init__(self, cal_path=None):
        if cal_path is None:
            cal_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gl7_calibrations', 'pumps_switches_cal.csv')
        self.voltages = []
        self.temperatures = []
        with open(cal_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                try:
                    t = float(row[0])
                    v = float(row[1])
                    self.temperatures.append(t)
                    self.voltages.append(v)
                except Exception:
                    continue
        self.voltages = np.array(self.voltages)
        self.temperatures = np.array(self.temperatures)
        self.interpolator = interp1d(self.voltages, self.temperatures, kind='linear', bounds_error=False, fill_value=(self.temperatures[0], self.temperatures[-1]))

# Convenience function to match main.py usage
def voltage_to_temperature(voltage):
    cal = PumpsCalibrator()
    if not isinstance(voltage, (int, float)) or voltage <= 0:
        return None
    return float(cal.interpolator(voltage))
