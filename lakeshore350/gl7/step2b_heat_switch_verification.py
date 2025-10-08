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
    
    # 4K stage temperature (Input D3)
    temp_4k_stage = gl7_controller.read_temperature('D3')
    print(f"  4K Stage Temperature (D3): {temp_4k_stage} K")
    
    # 50K stage temperature (Channel 2)
    temp_50k_stage = gl7_controller.read_temperature(2)
    print(f"  50K Stage Temperature (Channel 2): {temp_50k_stage} K")
    
    # 3-pump temperature - read temperature directly (Input D)
    temp_3pump = gl7_controller.read_temperature('D')
    
    # Check if we got a valid temperature reading
    if isinstance(temp_3pump, float) and temp_3pump > 0:
        print(f"  3-pump Temperature (Input D): {temp_3pump:.3f} K")
    else:
        print(f"  3-pump Temperature (Input D): Unable to read sensor")
    
    # 4-pump temperature - read temperature directly from channel 5
    temp_4pump = gl7_controller.read_temperature(5)
    
    if isinstance(temp_4pump, float):
        print(f"  4-pump Temperature (Channel 5): {temp_4pump:.3f} K")
    else:
        print(f"  4-pump Temperature (Channel 5): {temp_4pump}")
    print()
    
    # Import switch controller for centralized switch management
    from ..switches import SwitchController
    switch_ctrl = SwitchController(gl7_controller)
    
    # Manual heat switch control
    print("Manual Heat Switch Control:")
    input("Press ENTER to turn OFF 4-switch...")
    switch_ctrl.turn_off_switch(3)  # 4-switch is on analog output 3
    
    input("Press ENTER to turn OFF 3-switch...")
    switch_ctrl.turn_off_switch(4)  # 3-switch is on analog output 4
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
