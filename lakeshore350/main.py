#!/usr/bin/env python3
"""
Main interface for Lakeshore 350 Driver
"""

import argparse
import serial
from .temperature import TemperatureReader
from .gl7_control import GL7Controller
from .gl7 import test_sequence

def main():
    parser = argparse.ArgumentParser(description="Lakeshore 350 Temperature Controller")
    parser.add_argument("--port", default="/dev/ttyUSB2", help="Serial port (default: /dev/ttyUSB2)")
    parser.add_argument("--input", help="Read specific input (A, B, C, D)")
    parser.add_argument("--channel", type=int, help="Read specific channel (2-5)")
    parser.add_argument("--channels", nargs='+', type=int, help="Read multiple channels (e.g., --channels 2 3 4 5)")
    parser.add_argument("--all-inputs", action="store_true", help="Read all sensor inputs (A, B, C, D)")
    parser.add_argument("--all", action="store_true", help="Read all inputs and channels 2-5")
    parser.add_argument("--info", action="store_true", help="Get device information")
    
    # GL7 automation arguments
    parser.add_argument("--start-gl7", action="store_true", help="Start GL7 sorption cooler sequence (will be production version)")
    
    # Individual GL7 step arguments  
    parser.add_argument("--gl7-step1", action="store_true", help="Execute GL7 Step 1: Initial Status Check")
    parser.add_argument("--gl7-step2a", action="store_true", help="Execute GL7 Step 2A: Pre-cooling Phase")
    parser.add_argument("--gl7-step2b", action="store_true", help="Execute GL7 Step 2B: Heat Switch Status Verification")
    parser.add_argument("--gl7-step3", action="store_true", help="Execute GL7 Step 3: Pump Heating Phase")
    parser.add_argument("--gl7-step4", action="store_true", help="Execute GL7 Step 4: 4He Pump Transition")
    parser.add_argument("--gl7-step5", action="store_true", help="Execute GL7 Step 5: Cooling to 2K and 3He Pump Transition")
    parser.add_argument("--gl7-step6", action="store_true", help="Execute GL7 Step 6: Final Cooldown Monitoring")
    parser.add_argument("--gl7-step7", action="store_true", help="Execute GL7 Step 7: Final Status Check")
    
    # Test sequence arguments (all commands commented out for safe testing)
    parser.add_argument("--start-gl7-test-sequence", action="store_true", help="Start GL7 TEST sequence (ALL COMMANDS COMMENTED OUT)")
    parser.add_argument("--gl7-step1-test", action="store_true", help="Execute GL7 Step 1 TEST: Initial Status Check (safe)")
    parser.add_argument("--gl7-step2a-test", action="store_true", help="Execute GL7 Step 2A TEST: Pre-cooling Phase (safe)")
    parser.add_argument("--gl7-step2b-test", action="store_true", help="Execute GL7 Step 2B TEST: Heat Switch Verification (safe)")
    parser.add_argument("--gl7-step3-test", action="store_true", help="Execute GL7 Step 3 TEST: Pump Heating Phase (safe)")
    parser.add_argument("--gl7-step4-test", action="store_true", help="Execute GL7 Step 4 TEST: 4He Pump Transition (safe)")
    parser.add_argument("--gl7-step5-test", action="store_true", help="Execute GL7 Step 5 TEST: 3He Pump Transition (safe)")
    parser.add_argument("--gl7-step6-test", action="store_true", help="Execute GL7 Step 6 TEST: Final Cooldown (safe)")
    
    # Heater control arguments
    parser.add_argument("--heaters", nargs=2, metavar=('OUTPUT', 'POWER'), help="Set heater output: --heaters <output_num> <power_percent>")
    parser.add_argument("--heaters-both", nargs=2, type=float, metavar=('POWER1', 'POWER2'), help="Set both heaters: --heaters-both <power1> <power2>")
    parser.add_argument("--heaters-query", action="store_true", help="Query current heater status")
    parser.add_argument("--heaters-stop", action="store_true", help="EMERGENCY HEATER STOP: Immediately shut down both heaters")

    # Heat switch control arguments
    parser.add_argument("--switches", nargs=2, metavar=('SWITCH', 'STATE'), help="Set heat switch: --switches <switch_num> <ON/OFF>")
    parser.add_argument("--switches-both", type=str, choices=['ON', 'OFF', 'on', 'off'], help="Set both switches to same state: --switches-both ON/OFF")
    parser.add_argument("--switches-query", action="store_true", help="Query current heat switch status")

    # Display control arguments
    parser.add_argument("--display", action="store_true", help="Check Lakeshore 350 front panel display status")
    parser.add_argument("--set-name", nargs=2, metavar=('INPUT', 'NAME'), help="Set custom input name: --set-name <input> <name>")

    
    args = parser.parse_args()
    
    # If no specific action requested, default to reading all inputs
    if not any([args.input, args.channel, args.channels, args.all_inputs, args.all, args.info,
                args.start_gl7, args.gl7_step1, args.gl7_step2a, args.gl7_step2b, args.gl7_step3,
                args.gl7_step4, args.gl7_step5, args.gl7_step6, args.gl7_step7,
                args.start_gl7_test_sequence, args.gl7_step1_test, args.gl7_step2a_test,
                args.gl7_step2b_test, args.gl7_step3_test, args.gl7_step4_test,
                args.gl7_step5_test, args.gl7_step6_test,
                args.heaters, args.heaters_both, args.heaters_query, args.heaters_stop,
                args.switches, args.switches_both, args.switches_query,
                args.display, args.set_name]):
        args.all_inputs = True
    
    try:
        temp_reader = TemperatureReader(port=args.port)
        gl7_controller = GL7Controller(temp_reader.send_command)
        
        if args.info:
            print("Device Information:")
            info = temp_reader.get_device_info()
            print(f"  {info if info else 'No response'}")
            print()
        
        if args.input:
            print(f"Input {args.input.upper()} Temperature:")
            temp = temp_reader.read_temperature(args.input)
            if isinstance(temp, float):
                print(f"  {temp:.3f} K")
            else:
                print(f"  {temp}")
        
        if args.channel:
            print(f"Channel {args.channel} Temperature:")
            temp = temp_reader.read_temperature(args.channel)
            if isinstance(temp, float):
                print(f"  {temp:.3f} K")
            else:
                print(f"  {temp}")
        
        if args.channels:
            print("Selected Channels:")
            temps = temp_reader.read_channels(args.channels)
            for channel_name, temp in temps.items():
                if isinstance(temp, float):
                    print(f"  {channel_name}: {temp:.3f} K")
                else:
                    print(f"  {channel_name}: {temp}")
        
        if args.all_inputs:
            print("All Sensor Inputs:")
            temps = temp_reader.read_all_inputs()
            for input_name, temp in temps.items():
                if isinstance(temp, float):
                    print(f"  {input_name}: {temp:.3f} K")
                else:
                    print(f"  {input_name}: {temp}")
        
        if args.all:
            print("All Inputs (A-D):")
            input_temps = temp_reader.read_all_inputs()
            for input_name, temp in input_temps.items():
                if isinstance(temp, float):
                    print(f"  {input_name}: {temp:.3f} K")
                else:
                    print(f"  {input_name}: {temp}")
            
            print("\nAll Channels (2-5):")
            channel_temps = temp_reader.read_channels([2, 3, 4, 5])
            for channel_name, temp in channel_temps.items():
                if isinstance(temp, float):
                    print(f"  {channel_name}: {temp:.3f} K")
                else:
                    print(f"  {channel_name}: {temp}")
        
        # GL7 automation sequence (will be production version when commands are uncommented)
        if args.start_gl7:
            print("Starting GL7 Sorption Cooler Sequence...")
            print("NOTE: Currently in TEST/SIMULATION mode - heater commands are commented out")
            print("Stage Temperatures Don't Accurately Reflect Listed Channels/Inputs")
            print("Press Ctrl+C to abort at any time\n")
            
            try:
                success = gl7_controller.start_gl7_sequence()
                if success:
                    print("\nGL7 sequence completed successfully!")
                else:
                    print("\nGL7 sequence stopped due to safety conditions")
            except KeyboardInterrupt:
                print("\n\nGL7 sequence aborted by user")
                print("All systems remain in their current state")
        
        # Individual GL7 step execution
        if args.gl7_step1:
            try:
                result = gl7_controller.execute_step1()
            except KeyboardInterrupt:
                print("\nStep 1 aborted by user")
        
        if args.gl7_step2a:
            try:
                result = gl7_controller.execute_step2a()
            except KeyboardInterrupt:
                print("\nStep 2A aborted by user")
        
        if args.gl7_step2b:
            try:
                result = gl7_controller.execute_step2b()
            except KeyboardInterrupt:
                print("\nStep 2B aborted by user")
        
        if args.gl7_step3:
            try:
                result = gl7_controller.execute_step3()
            except KeyboardInterrupt:
                print("\nStep 3 aborted by user")
        
        if args.gl7_step4:
            try:
                result = gl7_controller.execute_step4()
            except KeyboardInterrupt:
                print("\nStep 4 aborted by user")
        
        if args.gl7_step5:
            try:
                result = gl7_controller.execute_step5()
            except KeyboardInterrupt:
                print("\nStep 5 aborted by user")
        
        if args.gl7_step6:
            try:
                result = gl7_controller.execute_step6()
            except KeyboardInterrupt:
                print("\nStep 6 aborted by user")
        
        if args.gl7_step7:
            print("Executing GL7 Step 7: Final Status Check")
            print("=" * 50)
            try:
                result = gl7_controller.execute_step7()
                print(f"Step 7 completed. GL7 Running: {result}")
            except KeyboardInterrupt:
                print("\nStep 7 aborted by user")
        
        # Test sequence handling (all commands commented out for safety)
        if args.start_gl7_test_sequence:
            print("Starting GL7 TEST SEQUENCE - ALL COMMANDS COMMENTED OUT")
            print("=" * 60)
            print("This is a safe test version with no actual heater activation")
            print("=" * 60)
            try:
                # Execute full test sequence
                test_sequence.execute_step1_test(gl7_controller)
                test_sequence.execute_step2a_test(gl7_controller)
                test_sequence.execute_step2b_test(gl7_controller)
                test_sequence.execute_step3_test(gl7_controller)
                test_sequence.execute_step4_test(gl7_controller)
                test_sequence.execute_step5_test(gl7_controller)
                result = test_sequence.execute_step6_test(gl7_controller)
                print(f"GL7 TEST SEQUENCE completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nGL7 Test sequence aborted by user")
        
        if args.gl7_step1_test:
            print("Executing GL7 Step 1 TEST: Initial Status Check (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step1_test(gl7_controller)
                print(f"Step 1 TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 1 TEST aborted by user")
        
        if args.gl7_step2a_test:
            print("Executing GL7 Step 2A TEST: Pre-cooling Phase (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step2a_test(gl7_controller)
                print(f"Step 2A TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 2A TEST aborted by user")
        
        if args.gl7_step2b_test:
            print("Executing GL7 Step 2B TEST: Heat Switch Verification (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step2b_test(gl7_controller)
                print(f"Step 2B TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 2B TEST aborted by user")
        
        if args.gl7_step3_test:
            print("Executing GL7 Step 3 TEST: Pump Heating Phase (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step3_test(gl7_controller)
                print(f"Step 3 TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 3 TEST aborted by user")
        
        if args.gl7_step4_test:
            print("Executing GL7 Step 4 TEST: 4He Pump Transition (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step4_test(gl7_controller)
                print(f"Step 4 TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 4 TEST aborted by user")
        
        if args.gl7_step5_test:
            print("Executing GL7 Step 5 TEST: 3He Pump Transition (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step5_test(gl7_controller)
                print(f"Step 5 TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 5 TEST aborted by user")
        
        if args.gl7_step6_test:
            print("Executing GL7 Step 6 TEST: Final Cooldown (SAFE)")
            print("=" * 50)
            try:
                result = test_sequence.execute_step6_test(gl7_controller)
                print(f"Step 6 TEST completed. Result: {result}")
            except KeyboardInterrupt:
                print("\nStep 6 TEST aborted by user")
        
        # Heater control handling
        if args.heaters or args.heaters_both or args.heaters_query or args.heaters_stop:
            from .heaters import set_heater_output, query_heater_status, emergency_stop_heaters
            import time
            
            if args.heaters_stop:
                # Emergency stop mode
                success = emergency_stop_heaters(gl7_controller)
                if success:
                    print("\nEmergency heater stop completed successfully.")
                else:
                    print("\nWarning: Some heaters may not have been shut down correctly.")
                    
            elif args.heaters_query:
                # Query mode - just show current status
                print("\nCurrent Heater Status:")
                query_heater_status(gl7_controller, 1)
                query_heater_status(gl7_controller, 2)
                
            elif args.heaters_both:
                # Set both heaters
                print("\nSetting Both Heaters:")
                success1 = set_heater_output(gl7_controller, 1, args.heaters_both[0])
                success2 = set_heater_output(gl7_controller, 2, args.heaters_both[1])
                
                # Wait a moment for commands to take effect
                time.sleep(1)
                
                # Query status after setting
                print("\nHeater Status After Setting:")
                query_heater_status(gl7_controller, 1)
                query_heater_status(gl7_controller, 2)
                
                if success1 and success2:
                    print("\nBoth heaters set successfully.")
                else:
                    print("\nWarning: One or more heaters may not have been set correctly.")
                    
            elif args.heaters:
                # Set single heater
                try:
                    output_num = int(args.heaters[0])
                    power_percent = float(args.heaters[1])
                    
                    if output_num not in [1, 2]:
                        print("Error: Output number must be 1 or 2")
                        return
                    if power_percent < 0 or power_percent > 100:
                        print("Error: Power must be between 0 and 100")
                        return
                    
                    heater_name = "4-pump Heater" if output_num == 1 else "3-pump Heater"
                    print(f"\nSetting {heater_name}:")
                    success = set_heater_output(gl7_controller, output_num, power_percent)
                    
                    # Wait a moment for commands to take effect
                    time.sleep(1)
                    
                    # Query status after setting
                    print(f"\n{heater_name} Status After Setting:")
                    query_heater_status(gl7_controller, output_num)
                    
                    if success:
                        print(f"\n{heater_name} set successfully.")
                    else:
                        print(f"\nWarning: {heater_name} may not have been set correctly.")
                        
                except (ValueError, IndexError):
                    print("Error: Invalid arguments for --heaters. Use: --heaters <output_num> <power_percent>")
                    return
        
        # Heat switch control handling
        if args.switches or args.switches_both or args.switches_query:
            from .switches import set_switch_state, query_switch_status
            import time
            
            if args.switches_query:
                # Query mode - just show current status
                print("\nCurrent Heat Switch Status:")
                query_switch_status(gl7_controller, 3)  # 4-switch
                query_switch_status(gl7_controller, 4)  # 3-switch
                
            elif args.switches_both:
                # Set both switches
                state = args.switches_both.upper()
                set_switch_state(gl7_controller, 3, state)  # 4-switch
                set_switch_state(gl7_controller, 4, state)  # 3-switch
                
                # Wait a moment for commands to take effect
                time.sleep(1)
                
                # Show status of both switches
                query_switch_status(gl7_controller, 3)  # 4-switch
                query_switch_status(gl7_controller, 4)  # 3-switch
                    
            elif args.switches:
                # Set single switch
                try:
                    switch_num = int(args.switches[0])
                    state = args.switches[1].upper()
                    
                    if switch_num not in [3, 4]:
                        print("Error: Switch number must be 3 (for 4-switch) or 4 (for 3-switch)")
                        return
                    if state not in ['ON', 'OFF']:
                        print("Error: State must be ON or OFF")
                        return
                    
                    set_switch_state(gl7_controller, switch_num, state)
                    
                    # Wait a moment for commands to take effect
                    time.sleep(1)
                    
                    # Show status of both switches
                    query_switch_status(gl7_controller, 3)  # 4-switch
                    query_switch_status(gl7_controller, 4)  # 3-switch
                        
                except (ValueError, IndexError):
                    print("Error: Invalid arguments for --switches. Use: --switches <switch_num> <ON/OFF>")
                    return
        
        # Display control handling
        if args.display:
            from .lakeshore_display import check_front_panel_display
            check_front_panel_display(gl7_controller=gl7_controller)
        
        # Set input name handling
        if args.set_name:
            import time
            
            input_name = args.set_name[0].upper()
            custom_name = args.set_name[1]
            
            # Validate input name
            valid_inputs = ['A', 'B', 'C', 'D', 'D2', 'D3', 'D4', 'D5']
            if input_name not in valid_inputs:
                print(f"Error: Input must be one of {valid_inputs}")
                return
            
            # Validate name length (Lakeshore 350 has a character limit)
            if len(custom_name) > 15:
                print("Error: Name must be 15 characters or less")
                return
            
            print(f"Setting {input_name} name to \"{custom_name}\"")
            
            try:
                # Set the custom name
                gl7_controller.send_command(f'INNAME {input_name},"{custom_name}"')
                
                # Wait a moment for the command to take effect
                time.sleep(0.5)
                
                # Verify the change
                new_name = gl7_controller.send_command(f'INNAME? {input_name}')
                print(f"Confirmed: {input_name} = \"{new_name}\"")
                
            except Exception as e:
                print(f"Error setting input name: {e}")

    
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        print("Make sure the Lakeshore 350 is connected and the port is correct.")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            temp_reader.close()
        except:
            pass

if __name__ == "__main__":
    main()
