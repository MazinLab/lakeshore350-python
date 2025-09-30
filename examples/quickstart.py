from lakeshore350.driver import LakeShore350

ls = LakeShore350("/dev/ttyUSB0", 57600)

try:
    print("IDN:", ls.query("*IDN?"))
    print("Temps:", ls.query("KRDG? 0"))
finally:
    ls.close()
