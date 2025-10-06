#!/usr/bin/env python3
"""
GL7 Step 2B: Heat Switch Status Verification
"""

import time
from ..head3_calibration import convert_3head_resistance_to_temperature
from ..head4_calibration import convert_4head_resistance_to_temperature

def execute_step2b(gl7_controller):
    """Execute GL7 Step 2b: Heat Switch Verification"""
    print("GL7 STEP 2B: HEAT SWITCH VERIFICATION")
    print("-" * 40)
    print("Verifying heat switches turn OFF when heads reach ~10K...")
    print("This step checks temperatures and heat switch status before proceeding to pump heating.\n")
    
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
    
    # 3-pump temperature (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    print(f"  3-pump Temperature (Input D): {temp_3pump} K")
    
    # 4-pump temperature (Channel 5)
    temp_4pump = gl7_controller.send_command("KRDG? 5")
    try:
        if temp_4pump and temp_4pump != "T_OVER":
            temp_4pump_val = float(temp_4pump)
        else:
            temp_4pump_val = temp_4pump
    except ValueError:
        temp_4pump_val = temp_4pump
    print(f"  4-pump Temperature (Channel 5): {temp_4pump_val} K")
    print()
    
    # Manual heat switch control
    print("Manual Heat Switch Control:")
    input("Press ENTER to turn OFF 4-switch...")
    print("  → Turning OFF 4-switch (Analog 3 to 0V)")
    gl7_controller.send_command("ANALOG 3,0")
    
    input("Press ENTER to turn OFF 3-switch...")
    print("  → Turning OFF 3-switch (Analog 4 to 0V)")
    gl7_controller.send_command("ANALOG 4,0")
    print()
    
    # Heat Switch Status
    print("Heat Switch Status:")
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
