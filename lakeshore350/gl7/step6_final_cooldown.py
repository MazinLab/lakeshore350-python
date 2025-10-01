#!/usr/bin/env python3
"""
GL7 Step 6: Final Cooldown Monitoring
"""

import time

def execute_step6(gl7_controller):
    """Execute GL7 Step 6: Final Cooldown to ~300mK"""
    print("STEP 6: FINAL COOLDOWN TO ~300mK")
    print("-" * 35)
    print("Monitoring final temperature progression...")
    print("Checking 4K Stage, 50K Stage, 3He Head, and 4He Head temperatures...")
    
    temp_4he_head_final = None
    
    for cycle in range(1, 4):
        print(f"\nTemperature Check {cycle}/3:")
        
        # Read all key temperatures
        temp_3he_head = gl7_controller.read_temperature('A')  # 3He Head
        temp_4he_head = gl7_controller.read_temperature('C')  # 4He Head
        
        # Read stage temperatures
        temp_channel_2 = gl7_controller.send_command("KRDG? 2")  # 4K stage
        temp_channel_3 = gl7_controller.send_command("KRDG? 3")  # 50K stage
        
        try:
            if temp_channel_2 and temp_channel_2 != "T_OVER":
                temp_4k_stage = float(temp_channel_2)
            else:
                temp_4k_stage = temp_channel_2
        except ValueError:
            temp_4k_stage = temp_channel_2
            
        try:
            if temp_channel_3 and temp_channel_3 != "T_OVER":
                temp_50k_stage = float(temp_channel_3)
            else:
                temp_50k_stage = temp_channel_3
        except ValueError:
            temp_50k_stage = temp_channel_3
        
        print(f"  4K Stage Temperature (Channel 2): {temp_4k_stage} K")
        print(f"  50K Stage Temperature (Channel 3): {temp_50k_stage} K")
        print(f"  3He Head Temperature (Input A): {temp_3he_head} K")
        print(f"  4He Head Temperature (Input C): {temp_4he_head} K")
        
        temp_4he_head_final = temp_4he_head
        
        # Check if 4He head is approaching 300mK
        if isinstance(temp_4he_head, float):
            if temp_4he_head <= 0.5:
                print(f"    ✓ 4He Head approaching target at {temp_4he_head} K")
                if temp_4he_head <= 0.3:
                    print("    ✓ 4He Head has reached ~300mK - GL7 ready!")
                    break
            else:
                print(f"    → 4He Head cooling toward 300mK target")
        
        if cycle < 3:
            time.sleep(2)
    
    print("\n")
    
    return temp_4he_head_final
