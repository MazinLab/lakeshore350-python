from lakeshore350.driver import LakeShore350

ls = LakeShore350("/dev/ttyUSB0", 57600)

# Example: set heater 1 to 50%
ls.set_heater_output(1, 50)
print("Heater 1 set to 50%")

# Turn off heater 1
# ls.set_heater_output(1, 0)
# print("Heater 1 turned off")

ls.disconnect()
