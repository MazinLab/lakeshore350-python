import serial
import time

# This file is responsible for querying and setting all outputs (heaters and pumps)


class OutputController:

    def set_heater_range(self, output_num=None, range_val=None):
        """
        Set the heater range for the specified output (1, 2, 3, or 4) to the given range value.
        Usage: set_heater_range(1, 2) sets output 1 to range 2.
        If arguments are not provided, prompt the user for them.
        """
        if output_num is None:
            try:
                output_num = int(input("Enter output number (1, 2, 3, or 4): ").strip())
            except Exception:
                print("Invalid output number.")
                return
        if output_num not in [1, 2, 3, 4]:
            print("Output number must be 1, 2, 3, or 4.")
            return
        if range_val is None:
            try:
                range_val = int(input("Enter range value (integer): ").strip())
            except Exception:
                print("Invalid range value.")
                return
        # Send RANGE command
        cmd = f'RANGE {output_num},{range_val}\n'.encode('ascii')
        self.ser.write(cmd)
        time.sleep(0.2)
        print(f"Sent: RANGE {output_num},{range_val}")
    def __init__(self, ser=None, port='/dev/ttyUSB2'):
        if ser is not None:
            self.ser = ser
        else:
            self.ser = serial.Serial(port=port, baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)

    def set_output_params(self, output_num=None, params=None):
        # Prompt user for output number if not provided
        if output_num is None:
            try:
                output_num = int(input("Enter output number (1, 2, 3, or 4): ").strip())
            except Exception:
                print("Invalid output number.")
                return
        if output_num not in [1, 2, 3, 4]:
            print("Output number must be 1, 2, 3, or 4.")
            return
        # Prompt for arguments if not provided
        if params is None:
            if output_num in [1, 2]:
                print("HTRSET syntax is: →\n    <output> (filled in for you already), <resistance>, <max current>, <max user current>, <current/power>)")
                print("It is recommended to enter 2,0,0.1,1 for Output 1: →\n    50 Ω resistance, no control input, user set max current, max user current 0.1A, read in current)")
                print("It is recommended to enter 1,0,+1.732,1 for Output 2: →\n    25 Ω resistance, no control input, user set max current, max user current 1.73A, read in current)")
                print("Enter HTRSET argument as 4 comma seperated values:")
                arg_str = input("HTRSET args: ").strip()
                params = [p.strip() for p in arg_str.split(",")]
            else:
                print("ANALOG syntax is: →\n    <output> (filled in for you already) <input>,<units>,<high value>, <low value>, <polarity>")
                print("It is recommended to enter 0,1,+5.00000,+0.00000,0 for Output 3/4: →\n     no control input, kelvin, 5 volt max, 0 volt min, 0 polarity")
                print("Enter ANALOG arguments as 5 comma seperated values:")
                arg_str = input("ANALOG args: ").strip()
                params = [p.strip() for p in arg_str.split(",")]
        param_str = ','.join(str(p) for p in params)
        if output_num in [1, 2]:
            cmd = f'HTRSET {output_num},{param_str}\n'.encode('ascii')
            self.ser.write(cmd)
            time.sleep(0.2)
            print(f"Sent: HTRSET {output_num},{param_str}")
        elif output_num in [3, 4]:
            cmd = f'ANALOG {output_num},{param_str}\n'.encode('ascii')
            self.ser.write(cmd)
            time.sleep(0.2)
            print(f"Sent: ANALOG {output_num},{param_str}")

    def query_outputs(self, output_num, suppress_print=False):
        # Query using MOUT, OUTMODE, HTRSET, HTR, AOUT, ANALOG
        output_lines = []
        if output_num not in [1, 2, 3, 4]:
            msg = "Output number must be 1, 2, 3, or 4."
            if not suppress_print:
                print(msg)
            return msg
        cmd = f'MOUT? {output_num}\n'.encode('ascii')
        self.ser.write(cmd)
        time.sleep(0.2)
        response = self.ser.readline().decode('ascii', errors='ignore').strip()
        line = f"MOUT (Manual Output Percentage) {output_num} Status: {response}"
        output_lines.append(line)
        if not suppress_print:
            print(line)
        # Query HTR? and HTRSET? for outputs 1 and 2
        if output_num in [1, 2]:
            htr_cmd = f'HTR? {output_num}\n'.encode('ascii')
            self.ser.write(htr_cmd)
            time.sleep(0.2)
            htr_response = self.ser.readline().decode('ascii', errors='ignore').strip()
            line = f"HTR? {output_num} : {htr_response}"
            output_lines.append(line)
            if not suppress_print:
                print(line)
            htrset_cmd = f'HTRSET? {output_num}\n'.encode('ascii')
            self.ser.write(htrset_cmd)
            time.sleep(0.2)
            htrset_response = self.ser.readline().decode('ascii', errors='ignore').strip()
            line = f"HTRSET? (<htr resistance>,<max current>,<max user current>,<current/power>) {output_num} : {htrset_response}"
            output_lines.append(line)
            if not suppress_print:
                print(line)
        # Query AOUT? and ANALOG? for outputs 3 and 4
        if output_num in [3, 4]:
            aout_cmd = f'AOUT? {output_num}\n'.encode('ascii')
            self.ser.write(aout_cmd)
            time.sleep(0.2)
            aout_response = self.ser.readline().decode('ascii', errors='ignore').strip()
            line = f"AOUT? {output_num} Status: {aout_response}"
            output_lines.append(line)
            if not suppress_print:
                print(line)
            analog_cmd = f'ANALOG? {output_num}\n'.encode('ascii')
            self.ser.write(analog_cmd)
            time.sleep(0.2)
            analog_response = self.ser.readline().decode('ascii', errors='ignore').strip()
            line = f"ANALOG? {output_num} Status: {analog_response}"
            output_lines.append(line)
            if not suppress_print:
                print(line)
        # Query OUTMODE? for all outputs 1-4
        outmode_cmd = f'OUTMODE? {output_num}\n'.encode('ascii')
        self.ser.write(outmode_cmd)
        time.sleep(0.2)
        outmode_response = self.ser.readline().decode('ascii', errors='ignore').strip()
        line = f"OUTMODE? {output_num} Status: {outmode_response}"
        output_lines.append(line)
        if not suppress_print:
            print(line)

        # Query RANGE? for all outputs 1-4 (robust, with error handling)
        try:
            range_cmd = f'RANGE? {output_num}\n'.encode('ascii')
            self.ser.write(range_cmd)
            time.sleep(0.2)
            range_response = self.ser.readline().decode('ascii', errors='ignore').strip()
            line = f"RANGE? {output_num} Status: {range_response}"
            output_lines.append(line)
            if not suppress_print:
                print(line)
        except Exception as e:
            line = f"Error querying RANGE? for output {output_num}: {e}"
            output_lines.append(line)
            if not suppress_print:
                print(line)

        return "\n".join(output_lines)

    def set_outputs(self, output_num, percent):
        """
        Set the specified output (1, 2, 3, or 4) to the given percentage using the MOUT command.
        """
        if output_num not in [1, 2, 3, 4]:
            print("Output number must be 1, 2, 3, or 4.")
            return
        if not (0 <= percent <= 100):
            print("Percent must be between 0 and 100.")
            return
        # cmd = f'MOUT (Manual Output Percentage:) {output_num}, {percent}\n'.encode('ascii')
        cmd = f'MOUT {output_num},{percent}\n'.encode('ascii')
        self.ser.write(cmd)
        time.sleep(0.2)
        print(f"Set Output {output_num} to {percent}%")



#DO NOT DELETE< WILL IMPLIMENT FUNCTIONALITY LATER 
# this can run as a python file
# import serial
# import time

# # Connect to the Lake Shore 350 via serial
# ser = serial.Serial(port='/dev/ttyUSB2', baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)

# #Set Analog Output 3 using ANALOG command
# # ser.write(b'OUTMODE 4,3,0,0\n')
# # time.sleep(0.2)
# # print("Executed: OUTMODE 4,3,0")

# # ser.write(b'ANALOG 4,0,1,,5\n')
# # time.sleep(0.2)
# # print("Executed: ANALOG 4,0,1,,5")
# ser.write(b'MOUT 3, 0\n')
# time.sleep(0.2)
# print("Executed: MOUT 3, 0")

# ser.write(b'MOUT 1, 0\n')
# time.sleep(0.2)
# print("Executed: MOUT 1, 0")

# ser.write(b'MOUT? 3\n')
# time.sleep(0.2)
# config1 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"MOUT Output 3 Config: {config1}")


# ser.write(b'ANALOG? 3\n')
# time.sleep(0.2)
# config3 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"Analog Output 3 Config: {config3}")

# # Query ANALOG output 4
# ser.write(b'ANALOG? 4\n')
# time.sleep(0.2)
# config4 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"Analog Output 4 Config: {config4}")
# print("Returns <input>,<units>,<high value>,<low value>,<polarity>[term]")

# # Query AOUT output 3
# ser.write(b'AOUT? 3\n')
# time.sleep(0.2)
# aout3 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"AOUT Output 3: {aout3}")

# # Query AOUT output 4
# ser.write(b'AOUT? 4\n')
# time.sleep(0.2)
# aout4 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"AOUT Output 4: {aout4}")

# ser.write(b'OUTMODE? 3\n')
# time.sleep(0.2)
# outmode3 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"OUTMODE Output 3: {outmode3}")

# ser.write(b'OUTMODE? 4\n')
# time.sleep(0.2)
# outmode4 = ser.readline().decode('ascii', errors='ignore').strip()
# print(f"OUTMODE Output 4: {outmode4}")


# ser.close()
