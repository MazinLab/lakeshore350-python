#!/usr/bin/env python3
"""
GL7 Step 1: Initial Status Check
"""

import time

def execute_step1(gl7_controller):
    """Execute GL7 Step 1: Initial Status Check"""
    print("STEP 1: INITIAL STATUS CHECK")
    print("-" * 30)
    
    # Check starting temperatures at specific measurement points
    # 3He Head temperature (Input A)
    temp_3he_head = gl7_controller.read_temperature('A')
    
    # 4He Head temperature (Input C)
    temp_4he_head = gl7_controller.read_temperature('C')
    
    # 4K stage temperature (Channel 2)
    temp_channel_2 = gl7_controller.send_command("KRDG? 2")
    try:
        if temp_channel_2 and temp_channel_2 != "T_OVER":
            temp_4k_val = float(temp_channel_2)
        else:
            temp_4k_val = temp_channel_2
    except ValueError:
        temp_4k_val = temp_channel_2
    
    # 50K stage temperature (Channel 3)
    temp_channel_3 = gl7_controller.send_command("KRDG? 3")
    try:
        if temp_channel_3 and temp_channel_3 != "T_OVER":
            temp_50k_val = float(temp_channel_3)
        else:
            temp_50k_val = temp_channel_3
    except ValueError:
        temp_50k_val = temp_channel_3
    
    # Device stage temperature (Input B)  
    temp_device = gl7_controller.read_temperature('B')
    
    print(f"3He Head Temperature (Input A): {temp_3he_head} K")
    print(f"4He Head Temperature (Input C): {temp_4he_head} K")
    print(f"4K Stage Temperature (Channel 2): {temp_4k_val} K")
    print(f"50K Stage Temperature (Channel 3): {temp_50k_val} K")
    print(f"Device Stage Temperature (Input B): {temp_device} K")
    
    # Check current heater/switch status
    print("\nCurrent Heater/Switch Status:")
    for relay_num, name in gl7_controller.relay_pump_heaters.items():
        config, status = gl7_controller.query_relay_status(relay_num)
        print(f"  {name} (Relay {relay_num}): Config={config}, Status={status}")
    
    for output_num, name in gl7_controller.analog_heat_switches.items():
        config = gl7_controller.query_analog_status(output_num)
        print(f"  {name} (Analog {output_num}): Config={config}")
    
    print("\n")
    time.sleep(2)
    
    return True
