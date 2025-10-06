#!/usr/bin/env python3
"""
GL7 Step 1: Initial Status Check (Test Version)
"""

import time
from ...head3_calibration import convert_3head_resistance_to_temperature
from ...head4_calibration import convert_4head_resistance_to_temperature
from ...pump_calibration import convert_pump_voltage_to_temperature

def execute_step1_test(gl7_controller):
    """Execute GL7 Step 1: Initial Status Check"""
    print("GL7 STEP 1: INITIAL STATUS CHECK")
    print("-" * 35)
    
    # Check starting temperatures at specific measurement points
    # 3He Head - read resistance and convert to temperature (Input A)
    resistance_3he_head = gl7_controller.read_temperature('A')
    if isinstance(resistance_3he_head, float) and resistance_3he_head > 0:
        temp_3he_head = convert_3head_resistance_to_temperature(resistance_3he_head)
        print(f"3-head Temperature (Input A): {temp_3he_head:.3f} K")
    else:
        print(f"3-head Temperature (Input A): Unable to read sensor")
    
    # 4He Head - read resistance and convert to temperature (Input C)
    resistance_4he_head = gl7_controller.read_temperature('C')
    if isinstance(resistance_4he_head, float) and resistance_4he_head > 0:
        temp_4he_head = convert_4head_resistance_to_temperature(resistance_4he_head)
        print(f"4-head Temperature (Input C): {temp_4he_head:.3f} K")
    else:
        print(f"4-head Temperature (Input C): Unable to read sensor")
    
    # 4K stage temperature (Input D2)
    temp_4k_stage = gl7_controller.read_temperature('D2')
    
    # 50K stage temperature (Input D3)
    temp_50k_stage = gl7_controller.read_temperature('D3')
    
    # Device stage temperature (Input B)  
    temp_device = gl7_controller.read_temperature('B')
    
    # 3-pump temperature - read voltage and convert to temperature (Input D)
    voltage_3pump = gl7_controller.read_voltage('D')
    
    # Convert 3-pump voltage to temperature using calibration
    if isinstance(voltage_3pump, float) and voltage_3pump > 0:
        temp_3pump = convert_pump_voltage_to_temperature(voltage_3pump)
    else:
        temp_3pump = None
    
    # 4-pump temperature - read voltage from channel 5 and convert to temperature
    voltage_4pump_response = gl7_controller.send_command("VRDG? 5")
    
    try:
        if voltage_4pump_response and voltage_4pump_response != "V_OVER":
            voltage_4pump = float(voltage_4pump_response)
            temp_4pump = convert_pump_voltage_to_temperature(voltage_4pump)
        else:
            voltage_4pump = None
            temp_4pump = None
    except ValueError:
        voltage_4pump = None
        temp_4pump = None
    

    print(f"4K Stage Temperature (Channel 2 (D2)): {temp_4k_stage} K")
    print(f"50K Stage Temperature (Channel 3 (D3)): {temp_50k_stage} K")
    print(f"Device Stage Temperature (Input B): {temp_device} K")
    
    if temp_3pump is not None:
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
    
    print("\nStep 1 Status: INITIAL SYSTEM CHECK COMPLETE")
    print("Note: System status verified, ready for precooling")
    
    return True
