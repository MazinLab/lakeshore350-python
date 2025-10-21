"""This scriot contains explicit serial commands for connecting to the lakeshore 
    It is not intended to be used as part of the typical lakeshore350 python functionality
    IT is intended for testing new serial commmands and quickly executing serial commands if the 
    CLI isn't working or there is a problem with the main codebase. 

    Example, commands to turn on/off heaters isn't working with lakeshore350 --outputs-set, 
    you can do it manually by running this file 

    To run: python3 serial_test.py

    Replace any of the chunks here with any of the lakeshore serial commands, i.e. HTRSET, HTR, DISPLAY, etc. 
"""

import serial
import time

# # Connect to the Lake Shore 350 via serial
ser = serial.Serial(port='/dev/ttyUSB2', baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)


# # Set Analog Output 3 using ANALOG command
# ser.write(b'OUTMODE 4,3,0,0\n')
# time.sleep(0.2)
# print("Executed: OUTMODE 4,3,0")


# # Set ANALOG 3 to output +5V, 0V range, unipolar
# ser.write(b'ANALOG 3,0,0,+5.00000,+0.00000,0,100.0\n')
# time.sleep(0.2)
# print("Executed: ANALOG 3,0,0,+5.00000,+0.00000,0,100.0")


# # Set MOUT 3 to 0 (off)
# ser.write(b'MOUT 3, 0\n')
# time.sleep(0.2)
# print("Executed: MOUT 3, 0")

# # Set MOUT 3 to 100 (on)
# ser.write(b'MOUT 3, 100\n')
# time.sleep(0.2)
# print("Executed: MOUT 3, 100")

# # Query AOUT output 3
# ser.write(b'AOUT? 3\n')
# time.sleep(0.2)
# config1 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"AOUT Output 3 Config: {config1}")


# # Query ANALOG output 3
# ser.write(b'ANALOG? 3\n')
# time.sleep(0.2)
# config3 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"Analog Output 3 Config: {config3}")

# Query ANALOG output 4
# ser.write(b'ANALOG? 3\n')
# time.sleep(0.2)
# config4 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"Analog Output 3 Config: {config4}")
# print("Returns <input>,<units>,<high value>,<low value>,<polarity>[term]")

# Query AOUT output 3
# ser.write(b'MOUT? 3\n')
# time.sleep(0.2)
# mout3 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"MOUT Output 3: {mout3}")

# # Query AOUT output 4
# ser.write(b'AOUT? 4\n')
# time.sleep(0.2)
# aout4 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"AOUT Output 4: {aout4}")

# # Query OUTMODE output 3
# ser.write(b'OUTMODE? 3\n')
# time.sleep(0.2)
# outmode3 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"OUTMODE Output 3: {outmode3}")

# # Query OUTMODE output 4
# ser.write(b'OUTMODE? 4\n')
# time.sleep(0.2)
# outmode4 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"OUTMODE Output 4: {outmode4}")

# # Query Input Display Names
# ser.write(b'INNAME? A\n')
# time.sleep(0.2)
# inname_a = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"Input Display Name A: {inname_a}")

# # Query Input Display Names
# ser.write(b'INNAME? D1\n')
# time.sleep(0.2)
# inname_d1 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"Input Display Name D1: {inname_d1}")

# Change Input Display Name D5 to "TEST_NAME"
ser.write(b'INNAME D5,"TEST_NAME"\n')
time.sleep(0.2)
inname_d5 = ser.readline().decode('ascii', errors='ignore').strip()
print(f"Input Display Name D5: {inname_d5}")


ser.close()
