# lakeshore350/driver.py
import serial

class LakeShore350:
    def __init__(self, port="/dev/ttyUSB0", baudrate=57600, timeout=1):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=7,
            parity="O",
            stopbits=1,
            timeout=timeout
        )
        # Auto-connect
        if not self.ser.is_open:
            self.ser.open()

    def write(self, command: str):
        self.ser.write((command + "\n").encode())

    def query(self, command: str) -> str:
        self.write(command)
        return self.ser.readline().decode(errors="ignore").strip()

    def read_temperature(self, channel: str):
        """Return the temperature for a channel ('A', 'B', 'C', 'D')."""
        channel_map = {"A": 1, "B": 2, "C": 3, "D": 4}
        ch = channel_map.get(channel.upper(), 1)
        val = self.query(f"KRDG? {ch}")
        try:
            return float(val)
        except ValueError:
            return val  # preserves T_OVER or error messages

    def set_heater_output(self, loop: int, percent: float):
        self.write(f"MOUT {loop},{percent}")

    def disconnect(self):
        self.ser.close()
