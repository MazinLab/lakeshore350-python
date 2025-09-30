from lakeshore350.driver import LakeShore350

# Auto-connect and read all channels
ls = LakeShore350("/dev/ttyUSB0", 57600)
channels = ["A", "B", "C", "D"]
for ch in channels:
    print(f"{ch}: {ls.read_temperature(ch)} K")

ls.disconnect()
