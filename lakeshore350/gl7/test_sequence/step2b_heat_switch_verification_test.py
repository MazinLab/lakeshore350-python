#!/usr/bin/env python3
"""
GL7 Step 2B: Heat Switch Status Verification
"""

import time
from ...head3_calibration import convert_3head_resistance_to_temperature
from ...head4_calibration import convert_4head_resistance_to_temperature
from ...pump_calibration import convert_pump_voltage_to_temperature

def execute_step2b_test(gl7_controller):
    """Execute GL7 Step 2b: Heat Switch Verification"""
    print("GL7 STEP 2B: HEAT SWITCH VERIFICATION")
    print("-" * 40)
    print("Confirm temperature ~10K before turning off switches.\n")
    
    # Temperature Check - Read all temperatures first
    print("Temperature Check:")
    
    # 3He Head - read resistance and convert to temperature (Input A)
    resistance_3he_head = gl7_controller.read_temperature('A')
    if isinstance(resistance_3he_head, float) and resistance_3he_head > 0:
        temp_3he_head = convert_3head_resistance_to_temperature(resistance_3he_head)
        print(f"  3-head Temperature (Input A): {temp_3he_head:.3f} K")
    else:
        print(f"  3-head Temperature (Input A): Unable to read sensor")
    
    # 4He Head - read resistance and convert to temperature (Input C)
    resistance_4he_head = gl7_controller.read_temperature('C')
    if isinstance(resistance_4he_head, float) and resistance_4he_head > 0:
        temp_4he_head = convert_4head_resistance_to_temperature(resistance_4he_head)
        print(f"  4-head Temperature (Input C): {temp_4he_head:.3f} K")
    else:
        print(f"  4-head Temperature (Input C): Unable to read sensor")
    
    # 4K stage temperature (Input D2)
    temp_4k_stage = gl7_controller.read_temperature('D2')
    print(f"  4K Stage Temperature (Channel 2 (D2)): {temp_4k_stage} K")
    
    # 50K stage temperature (Input D3)
    temp_50k_stage = gl7_controller.read_temperature('D3')
    print(f"  50K Stage Temperature (Channel 3 (D3)): {temp_50k_stage} K")
    
    # 3-pump temperature - read voltage and convert to temperature (Input D)
    voltage_3pump = gl7_controller.read_voltage('D')
    
    # Convert 3-pump voltage to temperature using calibration
    if isinstance(voltage_3pump, float) and voltage_3pump > 0:
        temp_3pump = convert_pump_voltage_to_temperature(voltage_3pump)
        print(f"  3-pump Temperature (Input D): {temp_3pump:.3f} K")
    else:
        print(f"  3-pump Temperature (Input D): Unable to read sensor")
    
    # 4-pump temperature - read voltage from channel 5 and convert to temperature
    voltage_4pump_response = gl7_controller.send_command("VRDG? 5")
    
    try:
        if voltage_4pump_response and voltage_4pump_response != "V_OVER":
            voltage_4pump = float(voltage_4pump_response)
            temp_4pump = convert_pump_voltage_to_temperature(voltage_4pump)
            print(f"  4-pump Temperature (Channel 5): {temp_4pump:.3f} K")
        else:
            print(f"  4-pump Temperature (Channel 5): Unable to read sensor")
    except ValueError:
        print(f"  4-pump Temperature (Channel 5): Unable to read sensor")
    print()
    
    # Manual heat switch control (TEST MODE - COMMANDS COMMENTED OUT)
    print("Manual Heat Switch Control:")
    input("Press ENTER to turn OFF 4-switch...")
    print("  → Turning OFF 4-switch (Analog 3 to 0V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 3,0")
    
    input("Press ENTER to turn OFF 3-switch...")
    print("  → Turning OFF 3-switch (Analog 4 to 0V)")
    # COMMENTED OUT: gl7_controller.send_command("ANALOG 4,0")
    print()
    
    # Heat Switch Status
    print("\nHeat Switch Status:")
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
        print(f"  {name} (Analog {output_num}): {config} {status_text}")
    
    print()
    
    # User confirmation before proceeding to pump heating
    input("Press ENTER to confirm both heat switches are OFF and proceed to Step 3 (Pump Heating)...")
    
    return True
