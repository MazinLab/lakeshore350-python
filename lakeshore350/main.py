#!/usr/bin/env python3
"""
Main interface for Lakeshore350 Driver 
"""
# Requires outputs.py, temperature.py, head3_calibration.py, head4_calibration.py, pumps_calibration.py
import argparse
import serial
import importlib.util
from .temperature import TemperatureReader
from .head3_calibration import convert_3head_resistance_to_temperature
from .head4_calibration import convert_4head_resistance_to_temperature
from .pumps_calibration import voltage_to_temperature
from .outputs import OutputController

## Defining all arguments 
def main():
    parser = argparse.ArgumentParser(description="Lakeshore 350 Temperature Controller")
    parser.add_argument("--all", action="store_true", help="Read all inputs (A-D), scanner inputs (D2-D5), and all channels (1-8)")
    parser.add_argument("--info", action="store_true", help="Get device information (*IDN?)")
    parser.add_argument("--run-gl7", metavar='CSV_FILE', help="Run GL7 infrastructure with CSV file")
    
    # Output control arguments (replaces heater control)
    parser.add_argument("--outputs-query", type=int, metavar='OUTPUT', help="Query output status: --outputs-query <output_num>")
    parser.add_argument("--outputs-query-all", action="store_true", help="Query all outputs 1-4: --outputs-query-all")
    parser.add_argument("--outputs-set", nargs=2, metavar=('OUTPUT', 'PERCENT'), help="Set output: --outputs-set <output_num> <percent>")
    parser.add_argument("--outputs-set-params", nargs="?", const=True, metavar='PARAMS', help="Set output parameters: --outputs-set-params [<output_num,param1,param2,...>")
    parser.add_argument("--outputs-set-range", nargs=2, metavar=('OUTPUT', 'RANGE'), help="Set heater range: --outputs-set-range <output_num> <range_val>")
    parser.add_argument("--display-show", metavar='INPUT', help="Show panel display INNAME for a specific input (e.g. A or D1)")
    parser.add_argument("--display-show-all", action='store_true', help="Show INNAME for all known inputs")
    parser.add_argument("--display-set-name", nargs='+', metavar=('INPUT','NAME'), help='Set panel display name: --display-set-name <INPUT> "<NAME>" ')

    # Display control arguments
    parser.add_argument("--display", action="store_true", help="Check Lakeshore 350 front panel display status")

    # Raw command - updated to match Lake Shore 370 syntax
    parser.add_argument("--raw-command", nargs='+', help="Send raw command to device (multiple terms joined with spaces)")

    args = parser.parse_args()

    if args.run_gl7:
        spec = importlib.util.spec_from_file_location("run_gl7", "/home/kids/lakeshore350-python/lakeshore350/run_gl7.py")
        run_gl7 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_gl7)
        # Pass the CSV file path to run_gl7
        if hasattr(run_gl7, 'main'):
            run_gl7.main(args.run_gl7)
        return

    try:
        port = "/dev/ttyUSB2"
        temp_reader = TemperatureReader(port=port)

        # Raw command execution - updated to match Lake Shore 370 syntax
        if args.raw_command:
            command = ' '.join(args.raw_command)
            print(f"Connected to Lakeshore 350 on {port} at 57600 baud")
            print(f"Command: {command}")
            response = temp_reader.send_command(command)
            print(f"Response: {response}")
            print("Lakeshore 350 connection closed")
            return

        # Reads hardware info 
        if args.info:
            print("Device Information:")
            print("Command: *IDN?")
            import time
            ser = serial.Serial(port='/dev/ttyUSB2', baudrate=57600, bytesize=7, parity='O', stopbits=1, timeout=2)
            ser.write(b'*IDN?\n')
            time.sleep(0.3)
            info = ser.readline().decode('ascii', errors='ignore').strip()
            print(f"  {info if info else 'No response'}")
            ser.close()
            print()
            print("Note: For raw commands, use: lakeshore350 --raw-command *IDN?")
            print("      (no quotes needed, arguments are joined with spaces)")

        # Prints all channels (temps and/or resistance/voltage)
        if args.all:
            print("Inputs:")
            # Only read A, B, C
            temp_a = temp_reader.read_temperature('A')
            temp_b = temp_reader.read_sensor('B')
            temp_c = temp_reader.read_temperature('C')

            # try to get display names for A-C from the front panel
            from .panel_display import get_display_name
            a_display = get_display_name(port=port, input_name='A') or '3-head'
            b_display = get_display_name(port=port, input_name='B') or 'Empty'
            c_display = get_display_name(port=port, input_name='C') or '4-head'
            a_label = f"Input A ({a_display})"
            b_label = f"Input B ({b_display})"
            c_label = f"Input C ({c_display})"

            # 3 head resistance to temperature conversion 
            # Requires head3_calibration.py and gl7_calibrations/3_head_cal.csv
            # If resistance is out of range/negative, returns None for temp
            if isinstance(temp_a, float):
                temp_a_cal = convert_3head_resistance_to_temperature(temp_a)
                if temp_a_cal is not None:
                    print(f"  {a_label}: {temp_a:.4f} Ω → {temp_a_cal:.3f} K")
                else:
                    print(f"  {a_label}: {temp_a:.4f} Ω → None") 
            else:
                print(f"  {a_label}: {temp_a}")

            # Input B prints resistance
            if isinstance(temp_b, float):
                print(f"  {b_label}: {temp_b:.4f} Ω")
            else:
                print(f"  {b_label}: {temp_b}") # Print w/out formatting for non number

            # 4 head resistance to temperature conversion
            # Print raw, calibrated, and temp from calibrated
            if isinstance(temp_c, float):
                temp_c_calibrated = temp_c + 34.56 #fudge factor for calibration
                temp_c_temp = convert_4head_resistance_to_temperature(temp_c_calibrated)
                print(f"  {c_label}: {temp_c:.4f} Ω (raw), {temp_c_calibrated:.4f} Ω (calibrated) → ", end="")
                if temp_c_temp is not None:
                    print(f"{temp_c_temp:.3f} K")
                else:
                    print("None")
            else:
                print(f"  {c_label}: {temp_c}")


            print("\nSpecial Inputs:")
            d1_resistance = temp_reader.read_sensor('D1')
            d2_voltage = temp_reader.read_sensor('D2')
            d3_temp = temp_reader.read_temperature('D3')
            d4_voltage = temp_reader.read_sensor('D4')
            d5_voltage = temp_reader.read_sensor('D5')
            

            from .panel_display import get_display_name
            
            d1_display = get_display_name(port=port, input_name='D1') or 'Empty'
            d2_display = get_display_name(port=port, input_name='D2') or '4-Pump Switch'
            d3_display = get_display_name(port=port, input_name='D3') or '4K'
            d4_display = get_display_name(port=port, input_name='D4') or '3-pump'
            d5_display = get_display_name(port=port, input_name='D5') or '4-pump'
            d1_name = f"Input D1 ({d1_display})"
            d2_name = f"Input D2 ({d2_display})"
            d3_name = f"Input D3 ({d3_display})"
            d4_name = f"Input D4 ({d4_display})"
            d5_name = f"Input D5 ({d5_display})"

            # D1
            if isinstance(d1_resistance, float):
                print(f"  {d1_name}: {d1_resistance:.4f} Ω")
            else:
                print(f"  {d1_name}: {d1_resistance}")
            # D2 (Switch, print raw value before conversion)
            if isinstance(d2_voltage, float):
                d2_temp = voltage_to_temperature(d2_voltage)
                if d2_temp is not None:
                    print(f"  {d2_name}: {d2_voltage:.4f} V → {d2_temp:.3f} K")
                else:
                    print(f"  {d2_name}: {d2_voltage:.4f} V → None")
            else:
                print(f"  {d2_name}: {d2_voltage}")
            # D3
            if isinstance(d3_temp, float):
                print(f"  {d3_name}: {d3_temp:.3f} K")
            else:
                print(f"  {d3_name}: {d3_temp}")
            # D4
            if isinstance(d4_voltage, float):
                d4_temp = voltage_to_temperature(d4_voltage)
                if d4_temp is not None:
                    print(f"  {d4_name}: {d4_voltage:.4f} V → {d4_temp:.3f} K")
                else:
                    print(f"  {d4_name}: {d4_voltage:.4f} V → None")
            else:
                print(f"  {d4_name}: {d4_voltage}")
            # D5
            if isinstance(d5_voltage, float):
                d5_temp = voltage_to_temperature(d5_voltage)
                if d5_temp is not None:
                    print(f"  {d5_name}: {d5_voltage:.4f} V → {d5_temp:.3f} K")
                else:
                    print(f"  {d5_name}: {d5_voltage:.4f} V → None")
            else:
                print(f"  {d5_name}: {d5_voltage}")

        # Connects to outputs.py 
        # Output 1: 4-pump heater, Output2: 3-pump heater, Output 3: 4 switch, Output 4: 3 switch
        if (
            args.outputs_query is not None or args.outputs_query_all or
            args.outputs_set is not None or args.outputs_set_params is not None or
            args.outputs_set_range is not None
        ):
            output_ctrl = OutputController(port=port)
            # ...existing code...
            if args.outputs_query is not None:
                output_ctrl.query_outputs(args.outputs_query)
            if args.outputs_query_all:
                for i in [1, 2, 3, 4]:
                    output_ctrl.query_outputs(i)
            if args.outputs_set is not None:
                try:
                    output_num = int(args.outputs_set[0])
                    percent = float(args.outputs_set[1])
                except (ValueError, IndexError):
                    print("Error: Invalid arguments for --outputs-set. Use: --outputs-set <output_num> <percent>")
                    return
                output_ctrl.set_outputs(output_num, percent)
            if args.outputs_set_params is not None:
                if args.outputs_set_params is True:
                    # No params provided, use interactive prompt
                    output_ctrl.set_output_params()
                else:
                    try:
                        parts = [p.strip() for p in args.outputs_set_params.split(',')]
                        output_num = int(parts[0])
                        params = [float(p) if '.' in p or 'e' in p.lower() else int(p) for p in parts[1:]]
                    except Exception:
                        print("Error: Invalid arguments for --outputs-set-params. Use: --outputs-set-params <output_num,param1,param2,...>")
                        return
                    output_ctrl.set_output_params(output_num, params)
            if args.outputs_set_range is not None:
                try:
                    output_num = int(args.outputs_set_range[0])
                    range_val = int(args.outputs_set_range[1])
                except (ValueError, IndexError):
                    print("Error: Invalid arguments for --outputs-set-range. Use: --outputs-set-range <output_num> <range_val>")
                    return
                output_ctrl.set_heater_range(output_num, range_val)
        
        
        # Shows current lakeshore front panel 
        if args.display:
            from .lakeshore_display import check_front_panel_display
            check_front_panel_display(port=port)
        

    # Handle serial connection issue
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print("Make sure the Lakeshore 350 is connected and the port is correct.")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            temp_reader.close()
        except:
            pass

if __name__ == "__main__":
    main()
