from .driver import LakeShore350

def run(port="/dev/ttyUSB0", baud=57600):
    ls = LakeShore350(port, baud)
    try:
        print(ls.query("*IDN?"))
    finally:
        ls.close()

if __name__ == "__main__":
    run()