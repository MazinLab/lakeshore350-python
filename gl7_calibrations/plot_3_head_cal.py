import pandas as pd
import matplotlib.pyplot as plt

# Read the calibration CSV, skipping the third column and header comment
cal_path = "gl7_calibrations/3_head_cal.csv"
df = pd.read_csv(cal_path, comment='#')

# Drop any columns except the first two
cols = df.columns[:2]
df = df[list(cols)]

# Remove any rows with non-numeric data
try:
    df = df.dropna()
    df[cols[0]] = pd.to_numeric(df[cols[0]], errors='coerce')
    df[cols[1]] = pd.to_numeric(df[cols[1]], errors='coerce')
    df = df.dropna()
except Exception:
    pass

plt.figure(figsize=(8,6))
plt.plot(df[cols[0]], df[cols[1]], marker='o', linestyle='-', color='C0')
plt.xlabel(cols[0])
plt.ylabel(cols[1])
plt.title('3 Head Calibration: Resistance vs Temperature')
plt.grid(True, ls='--', alpha=0.5)
plt.tight_layout()
plt.savefig('gl7_calibrations/3_head_cal_plot.png', dpi=200)
print('Saved plot: gl7_calibrations/3_head_cal_plot.png')
