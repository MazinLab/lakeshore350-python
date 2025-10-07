#!/usr/bin/env python3
"""
GL7 Step 1: Initial Status Check
"""

import time
from ..head3_calibration import convert_3head_resistance_to_temperature
from ..head4_calibration import convert_4head_resistance_to_temperature

def execute_step1(gl7_controller):
    """Execute GL7 Step 1: Initial Status Check"""
    print("GL7 STEP 1: INITIAL STATUS CHECK")
    print("-" * 35)
    
    # Check starting temperatures at specific measurement points
    # 3He Head - read resistance and convert to temperature (Input A)
    resistance_3he_head = gl7_controller.read_temperature('A')
    
    # Convert 3-head resistance to temperature using calibration
    if isinstance(resistance_3he_head, float) and resistance_3he_head > 0:
        temp_3he_head = convert_3head_resistance_to_temperature(resistance_3he_head)
    else:
        temp_3he_head = None
    
    # 4He Head - read resistance and convert to temperature (Input C)
    resistance_4he_head = gl7_controller.read_temperature('C')
    
    # Convert 4-head resistance to temperature using calibration
    if isinstance(resistance_4he_head, float) and resistance_4he_head > 0:
        temp_4he_head = convert_4head_resistance_to_temperature(resistance_4he_head)
    else:
        temp_4he_head = None
    
    # 4K stage temperature (Input D2)
    temp_4k_stage = gl7_controller.read_temperature('D2')
    
    # 50K stage temperature (Input D3)
    temp_50k_stage = gl7_controller.read_temperature('D3')
    
    # Device stage temperature (Input B)  
    temp_device = gl7_controller.read_temperature('B')
    
    # 3-pump temperature - read temperature directly (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    
    # 4-pump temperature - read temperature directly from channel 5
    temp_4pump_response = gl7_controller.send_command("KRDG? 5")
    
    try:
        if temp_4pump_response and temp_4pump_response != "T_OVER":
            temp_4pump = float(temp_4pump_response)
        else:
            temp_4pump = None
    except ValueError:
        temp_4pump = None
    

    if temp_3he_head is not None:
        print(f"3-head Temperature (Input A): {temp_3he_head:.3f} K")
    else:
        print(f"3-head Temperature (Input A): Unable to read sensor")
    
    if temp_4he_head is not None:
        print(f"4-head Temperature (Input C): {temp_4he_head:.3f} K")
    else:
        print(f"4-head Temperature (Input C): Unable to read sensor")
    print(f"4K Stage Temperature (Channel 2 (D2)): {temp_4k_stage} K")
    print(f"50K Stage Temperature (Channel 3 (D3)): {temp_50k_stage} K")
    print(f"Device Stage Temperature (Input B): {temp_device} K")
    
    if isinstance(temp_3pump, float) and temp_3pump > 0:
        print(f"3-pump Temperature (Input D): {temp_3pump:.3f} K")
    else:
        print(f"3-pump Temperature (Input D): Unable to read sensor")
    
    if temp_4pump is not None:
        print(f"4-pump Temperature (Channel 5): {temp_4pump:.3f} K")
    else:
        print(f"4-pump Temperature (Channel 5): Unable to read sensor")
    
    # Check current heater/switch status
    print("\nHeater/Switch Status:")
    
    # Check pump heaters (heater outputs 1 & 2)
    # 4He Pump Heater (Output 1)
    mode_1, output_1 = gl7_controller.query_heater_output_status(1)
    try:
        output_1_val = float(output_1) if output_1 else 0.0
        print(f"  4-pump Heater (Heater Output 1): Mode={mode_1}, Output={output_1_val}%")
    except (ValueError, TypeError):
        print(f"  4-pump Heater (Heater Output 1): Mode={mode_1}, Output={output_1}")
    
    # 3He Pump Heater (Output 2)
    mode_2, output_2 = gl7_controller.query_heater_output_status(2)
    try:
        output_2_val = float(output_2) if output_2 else 0.0
        print(f"  3-pump Heater (Heater Output 2): Mode={mode_2}, Output={output_2_val}%")
    except (ValueError, TypeError):
        print(f"  3-pump Heater (Heater Output 2): Mode={mode_2}, Output={output_2}")
    
    # Check heat switches (still on analog outputs 3 & 4)
    for output_num, name in gl7_controller.analog_heat_switches.items():
        config = gl7_controller.query_analog_status(output_num)
        # Parse the config to determine ON/OFF status and voltage
        try:
            config_parts = config.split(',') if config else []
            status_value = int(config_parts[0]) if len(config_parts) > 0 else 0
            voltage = float(config_parts[2]) if len(config_parts) > 2 else 0.0
            status_text = f"(ON, {voltage:.1f}V)" if status_value == 1 else f"(OFF, {voltage:.1f}V)"
        except (ValueError, IndexError):
            status_text = "(UNKNOWN)"
        print(f"  {name} (Analog {output_num}): Config={config} {status_text}")
    
    print("\n")
    time.sleep(2)
    
    return True
