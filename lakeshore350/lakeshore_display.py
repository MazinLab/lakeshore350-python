#!/usr/bin/env python3
"""
Check Lakeshore 350 Front Panel Display Status
"""

import argparse

# Handle imports for both direct execution and module import
try:
    from .temperature import TemperatureReader
    from .gl7_control import GL7Controller
except ImportError:
    # Direct execution path
    from temperature import TemperatureReader
    from gl7_control import GL7Controller

def check_front_panel_display(port="/dev/ttyUSB2", gl7_controller=None):
    """Check what's currently displayed on the Lakeshore 350 front panel"""
    
    print("Checking Lakeshore 350 Front Panel Display Status...")
    print("=" * 55)
    
    try:
        # Use existing controller or create new connection
        if gl7_controller is None:
            temp_reader = TemperatureReader(port=port)
            gl7_controller = GL7Controller(temp_reader.send_command)
            should_close = True
        else:
            should_close = False
        
        # Query main display setup
        display_setup = gl7_controller.send_command("DISPLAY?")
        print(f"\nDisplay Setup: {display_setup}")
        
        if display_setup:
            parts = display_setup.split(',')
            if len(parts) >= 3:
                mode, num_fields, output_source = parts[0], parts[1], parts[2]
                
                # Decode display mode
                mode_names = {
                    '0': 'Input A',
                    '1': 'Input B', 
                    '2': 'Input C',
                    '3': 'Input D',
                    '4': 'Custom',
                    '04': 'Custom',  # Handle leading zero format
                    '5': 'Four Loop',
                    '05': 'Four Loop',  # Handle leading zero format
                    '6': 'All Inputs',
                    '06': 'All Inputs'  # Handle leading zero format
                }
                
                mode_name = mode_names.get(mode, f"Unknown ({mode})")
                print(f"  Display Mode: {mode_name}")
                
                if mode == '4' or mode == '04':  # Custom mode
                    field_sizes = {'0': '2 large', '1': '4 large', '2': '8 small'}
                    field_size = field_sizes.get(num_fields, f"Unknown ({num_fields})")
                    print(f"  Number of Fields: {field_size}")
                    print(f"  Output Source: Output {output_source}")
                    
                    # Query each display field for custom mode
                    print(f"\nCustom Display Fields:")
                    max_fields = 8 if num_fields == '2' else (4 if num_fields == '1' else 2)
                    
                    for field_num in range(1, max_fields + 1):
                        try:
                            field_info = gl7_controller.send_command(f"DISPFLD? {field_num}")
                            if field_info and ',' in field_info:
                                input_num, units = field_info.split(',')
                                
                                input_names = {'1': 'Input A', '2': 'Input B', '3': 'Input C', '4': 'Input D'}
                                unit_names = {'1': 'Kelvin', '2': 'Celsius', '3': 'Sensor units'}
                                
                                input_name = input_names.get(input_num, f"Input {input_num}")
                                unit_name = unit_names.get(units, f"Units {units}")
                                
                                print(f"    Field {field_num}: {input_name} in {unit_name}")
                            else:
                                print(f"    Field {field_num}: {field_info}")
                        except Exception as e:
                            print(f"    Field {field_num}: Error - {e}")
                            
                elif mode == '6' or mode == '06':  # All Inputs mode
                    size_names = {'0': 'small with input names', '1': 'large without input names'}
                    size_name = size_names.get(num_fields, f"Unknown ({num_fields})")
                    print(f"  Display Size: {size_name}")
                    
                elif mode == '5' or mode == '05':  # Four Loop mode
                    print(f"  Output Source: Output {output_source}")
        
        # Get custom input names
        print(f"\nCustom Input Names:")
        try:
            # Input names (A, B, C, D)
            inputs = ['A', 'B', 'C', 'D']
            for input_name in inputs:
                try:
                    name = gl7_controller.send_command(f'INNAME? {input_name}')
                    print(f"  Input {input_name}: \"{name}\"")
                except Exception as e:
                    print(f"  Input {input_name}: Error - {e}")
            
            # Channel names (D2, D3, D4, D5)
            channels = ['D2', 'D3', 'D4', 'D5']
            for channel_name in channels:
                try:
                    name = gl7_controller.send_command(f'INNAME? {channel_name}')
                    print(f"  Channel {channel_name}: \"{name}\"")
                except Exception as e:
                    print(f"  Channel {channel_name}: Error - {e}")
        except Exception as e:
            print(f"  Error reading input names: {e}")
            
        # Close connection only if we created it
        if should_close:
            temp_reader.close()
        
    except Exception as e:
        print(f"Error checking display: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check Lakeshore 350 front panel display")
    parser.add_argument("--port", default="/dev/ttyUSB2", help="Serial port")
    
    args = parser.parse_args()
    check_front_panel_display(args.port)
