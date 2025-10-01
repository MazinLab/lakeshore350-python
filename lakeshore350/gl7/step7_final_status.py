#!/usr/bin/env python3
"""
GL7 Step 7: Final Status Check
"""

import time

def execute_step7(gl7_controller):
    """Execute GL7 Step 7: Final Status Check"""
    print("STEP 7: FINAL STATUS CHECK")
    print("-" * 30)
    
    # Final temperature readings
    print("Final Temperature Check:")
    final_3he_head = gl7_controller.read_temperature('A')  # 3He Head
    final_4he_head = gl7_controller.read_temperature('C')  # 4He Head
    
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
    
    print(f"  4K Stage Temperature (Channel 2): {final_4k_stage} K")
    print(f"  50K Stage Temperature (Channel 3): {final_50k_stage} K")
    print(f"  3He Head Temperature (Input A): {final_3he_head} K")
    print(f"  4He Head Temperature (Input C): {final_4he_head} K")
    
    # Check if GL7 is running (4He head at ~300mK)
    print(f"\nGL7 Operating Status:")
    gl7_running = False
    
    if isinstance(final_4he_head, float):
        if final_4he_head <= 0.5:
            print(f"  ✓ 4He Head at {final_4he_head} K")
            if final_4he_head <= 0.3:
                print("  🎉 GL7 IS NOW RUNNING! 4He Head has reached ~300mK")
                gl7_running = True
            else:
                print("  → GL7 approaching full operation (close to 300mK)")
        else:
            print(f"  → 4He Head at {final_4he_head} K (still cooling)")
    else:
        print(f"  → 4He Head reading: {final_4he_head} (simulation mode)")
        print("  → In actual operation, GL7 would be running at ~300mK")
    
    # Final heater/switch status
    print("\nFinal Heater/Switch Status:")
    for relay_num, name in gl7_controller.relay_pump_heaters.items():
        config, status = gl7_controller.query_relay_status(relay_num)
        print(f"  {name}: {status} (should be OFF)")
    
    for output_num, name in gl7_controller.analog_heat_switches.items():
        config = gl7_controller.query_analog_status(output_num)
        print(f"  {name}: Config={config} (should be ON)")
    
    return gl7_running
