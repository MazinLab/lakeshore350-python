#!/usr/bin/env python3
"""
GL7 Step 6: Final Cooldown Monitoring
"""

import time

def execute_step6_test(gl7_controller):
    """Execute GL7 Step 6: Final Status Check"""
    print("GL7 STEP 6: FINAL STATUS CHECK")
    print("-" * 35)
    print("Monitoring final cooldown to ~300mK...")
    
    # Temperature Check
    print("\nTemperature Check:")
    final_3he_head = gl7_controller.read_temperature('A')  # 3-head
    final_4he_head = gl7_controller.read_temperature('C')  # 4-head
    
    final_channel_2 = gl7_controller.send_command("KRDG? 2")  # 4K stage
    final_channel_3 = gl7_controller.send_command("KRDG? 3")  # 50K stage
    
    try:
        if final_channel_2 and final_channel_2 != "T_OVER":
            final_4k_stage = float(final_channel_2)
        else:
            final_4k_stage = final_channel_2
    except ValueError:
        final_4k_stage = final_channel_2
        
    try:
        if final_channel_3 and final_channel_3 != "T_OVER":
            final_50k_stage = float(final_channel_3)
        else:
            final_50k_stage = final_channel_3
    except ValueError:
        final_50k_stage = final_channel_3
    
    print(f"  3-head Temperature (Input A): {final_3he_head} K")
    print(f"  4-head Temperature (Input C): {final_4he_head} K")
    print(f"  4K Stage Temperature (Channel 2): {final_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3): {final_50k_stage} K")
    
    # 3-pump temperature (Input D)
    final_3pump = gl7_controller.read_temperature('D')
    print(f"  3-pump Temperature (Input D): {final_3pump} K")
    
    # 4-pump temperature (Channel 5)
    final_4pump = gl7_controller.send_command("KRDG? 5")
    try:
        if final_4pump and final_4pump != "T_OVER":
            final_4pump_val = float(final_4pump)
        else:
            final_4pump_val = final_4pump
    except ValueError:
        final_4pump_val = final_4pump
    print(f"  4-pump Temperature (Channel 5): {final_4pump_val} K")
    
    # Final heater/switch status
    print("\nFinal Heater/Switch Status:")
    print("  4-pump Heater (Heater Output 1): Should be OFF (0% power)")
    print("  3-pump Heater (Heater Output 2): Should be OFF (0% power)")
    
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
        print(f"  {name}: Config={config} {status_text} (should be ON)")
    
    return True
