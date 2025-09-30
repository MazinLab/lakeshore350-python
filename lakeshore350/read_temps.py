from .driver import LakeShore350

def safe_parse(value: str):
    """Parse a temperature value, preserving T_OVER or errors."""
    try:
        return float(value)
    except ValueError:
        return value

def run(port="/dev/ttyUSB0", baud=57600):
    ls = LakeShore350(port, baud)
    try:
        response = ls.query("KRDG? 0")  # all channels
        temps = response.split(",")
        labels = ["A", "B", "C", "D", "5", "6", "7", "8"]
        for label, val in zip(labels, temps):
            print(f"{label}: {safe_parse(val)}")
    finally:
        ls.close()

if __name__ == "__main__":
    run()
