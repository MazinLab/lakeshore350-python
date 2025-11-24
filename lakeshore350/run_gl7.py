import pandas as pd
import sys
import os
import time
import threading
from datetime import datetime

# ADJUSTABLE PARAMETERS
OUTPUT1_TARGET_PERCENT = 43  # Target percentage for output 1 (4-pump heater)
OUTPUT1_RAMP_TIME_MINUTES = 2  # Ramp time for output 1

OUTPUT2_TARGET_PERCENT = 25  # Initial target percentage for output 2 (3-pump heater)
OUTPUT2_RAMP_TIME_MINUTES = 2  # Initial ramp time for output 2

# Temperature control parameters for 3_Pump_Temp_K (Output 2)
TARGET_3PUMP_TEMP_MIN = 45  # K - minimum target temperature
TARGET_3PUMP_TEMP_MAX = 50  # K - maximum target temperature
TARGET_3PUMP_TEMP_IDEAL = 48  # K - ideal maximum (start reducing power above this)

# Temperature control parameters for 4_Pump_Temp_K (Output 1)
TARGET_4PUMP_TEMP_MIN = 50  # K - minimum target temperature
TARGET_4PUMP_TEMP_MAX = 60  # K - maximum target temperature
TARGET_4PUMP_TEMP_IDEAL = 55  # K - ideal maximum (start reducing power above this)

TEMP_CHECK_INTERVAL = 120  # seconds between temperature checks (2 minutes)
POWER_ADJUSTMENT_STEP = 1.0  # percentage change per adjustment

# Head temperature stabilization parameters
HEAD_STABILIZATION_WINDOW = 5  # Number of readings to check for stability
HEAD_STABILIZATION_TOLERANCE = 0.05  # K - maximum change to consider stable
HEAD_CHECK_INTERVAL = 60  # seconds between head temp checks (1 minute)

# Switch heating parameters
OUTPUT4_TARGET_PERCENT = 50  # Target percentage for output 4 (4-switch heater)
OUTPUT4_RAMP_TIME_MINUTES = 2  # Ramp time for output 4

# 4Head monitoring parameters
HEAD_4_TARGET_TEMP = 2.0  # K - temperature threshold to trigger 3-switch activation
HEAD_4_CHECK_INTERVAL = 120  # seconds between 4head temp checks (2 minutes)

# 3-Switch heating parameters  
OUTPUT3_TARGET_PERCENT = 45  # Target percentage for output 3 (3-switch heater)
OUTPUT3_RAMP_TIME_MINUTES = 2  # Ramp time for output 3

# Global log file handle
log_file = None

def setup_logging():
    """Setup logging to file with date-based naming"""
    global log_file
    
    # Create logs directory if it doesn't exist
    log_dir = "/home/kids/lakeshore350-python/gl7_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate log filename with date
    date_str = datetime.now().strftime("%m-%d-%Y")
    base_filename = f"{date_str}_run_gl7.log"
    log_path = os.path.join(log_dir, base_filename)
    
    # If file exists, append number
    counter = 1
    while os.path.exists(log_path):
        counter += 1
        log_path = os.path.join(log_dir, f"{date_str}_run_gl7_{counter}.log")
    
    log_file = open(log_path, 'w')
    log_print(f"=== GL7 Run Log Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    return log_path

def log_print(message, include_timestamp=True):
    """Print to both console and log file with optional timestamp"""
    if include_timestamp:
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
    else:
        formatted_message = message
    
    print(formatted_message)
    if log_file:
        log_file.write(formatted_message + '\n')
        log_file.flush()

def close_logging():
    """Close the log file"""
    global log_file
    if log_file:
        log_print(f"=== GL7 Run Log Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===", include_timestamp=False)
        log_file.close()
        log_file = None

def parse_fixed_width_line(line, widths):
    """Parse a fixed-width line using column widths"""
    vals = []
    idx = 0
    for w in widths:
        chunk = line[idx:idx + w]
        vals.append(chunk.strip())
        idx += w
    return vals

# Column widths matching record_temps_switches.py exactly
COLUMN_WIDTHS = [28, 12, 12, 17, 17, 17, 20, 18, 16, 18, 16, 17, 16, 17, 16]

# Headers matching your CSV
HEADERS = [
    "Timestamp", "Date", "Time", "4K_Stage_Temp_K", "Switch_Res_Ohm", "Switch_Temp_K",
    "3_Head_Res_Ohm", "3_Head_Temp_K", "4_Head_Res_Raw_Ohm", "4_Head_Res_Sub_Ohm", 
    "4_Head_Temp_K", "3_Pump_Volt", "3_Pump_Temp_K", "4_Pump_Volt", "4_Pump_Temp_K"
]

# Temperature columns to display (excluding resistances and voltages)
TEMP_COLUMNS = ["4K_Stage_Temp_K", "Switch_Temp_K", "3_Head_Temp_K", "4_Head_Temp_K", "3_Pump_Temp_K", "4_Pump_Temp_K"]

def get_current_temp_from_csv(csv_path, temp_column):
    """Get the most recent temperature reading from CSV"""
    try:
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            return None
            
        # Parse the last data line
        last_line = lines[-1].rstrip('\n')
        values = parse_fixed_width_line(last_line, COLUMN_WIDTHS)
        data = dict(zip(HEADERS, values))
        
        temp_str = data.get(temp_column, "")
        return float(temp_str) if temp_str and temp_str.replace('.', '').replace('-', '').isdigit() else None
    except Exception:
        return None

def monitor_and_control_pumps(output_ctrl, csv_path, stop_event):
    """Monitor both pump temperatures and adjust outputs to maintain target ranges"""
    current_power_output1 = OUTPUT1_TARGET_PERCENT  # 4-pump heater
    current_power_output2 = OUTPUT2_TARGET_PERCENT  # 3-pump heater
    
    log_print(f"Starting dual pump temperature monitoring:")
    log_print(f"  3_Pump target: {TARGET_3PUMP_TEMP_MIN}-{TARGET_3PUMP_TEMP_MAX}K (Output 2, ideal <{TARGET_3PUMP_TEMP_IDEAL}K)")
    log_print(f"  4_Pump target: {TARGET_4PUMP_TEMP_MIN}-{TARGET_4PUMP_TEMP_MAX}K (Output 1, ideal <{TARGET_4PUMP_TEMP_IDEAL}K)")
    log_print(f"  Check interval: {TEMP_CHECK_INTERVAL} seconds")
    
    pumps_in_range = False
    
    while not stop_event.is_set():
        temp_3pump = get_current_temp_from_csv(csv_path, "3_Pump_Temp_K")
        temp_4pump = get_current_temp_from_csv(csv_path, "4_Pump_Temp_K")
        
        # Check if both pumps are in their target ranges
        pump3_in_range = (temp_3pump is not None and 
                         TARGET_3PUMP_TEMP_MIN <= temp_3pump <= TARGET_3PUMP_TEMP_MAX)
        pump4_in_range = (temp_4pump is not None and 
                         TARGET_4PUMP_TEMP_MIN <= temp_4pump <= TARGET_4PUMP_TEMP_MAX)
        
        if pump3_in_range and pump4_in_range and not pumps_in_range:
            pumps_in_range = True
            log_print("Both pumps have reached their target temperature ranges!")
            log_print(f"  3_Pump: {temp_3pump:.2f}K (target: {TARGET_3PUMP_TEMP_MIN}-{TARGET_3PUMP_TEMP_MAX}K)")
            log_print(f"  4_Pump: {temp_4pump:.2f}K (target: {TARGET_4PUMP_TEMP_MIN}-{TARGET_4PUMP_TEMP_MAX}K)")
        
        # Log current status every check
        status_msg = f"Pump temps - 3Pump: "
        if temp_3pump is not None:
            status_msg += f"{temp_3pump:.2f}K ({'✓' if pump3_in_range else '✗'}), "
        else:
            status_msg += "No data, "
            
        status_msg += f"4Pump: "
        if temp_4pump is not None:
            status_msg += f"{temp_4pump:.2f}K ({'✓' if pump4_in_range else '✗'})"
        else:
            status_msg += "No data"
            
        log_print(status_msg)
        
        # Control 3_Pump (Output 2)
        if temp_3pump is not None and temp_3pump >= TARGET_3PUMP_TEMP_MIN:
            if temp_3pump > TARGET_3PUMP_TEMP_IDEAL:  # Above ideal (>48K), decrease power
                new_power = max(0, current_power_output2 - POWER_ADJUSTMENT_STEP)
                if new_power != current_power_output2:
                    try:
                        output_ctrl.set_outputs(2, new_power)
                        log_print(f"3_Pump {temp_3pump:.2f}K above ideal, reducing Output 2 to {new_power:.1f}%")
                        current_power_output2 = new_power
                    except Exception as e:
                        log_print(f"Error adjusting Output 2: {e}")
            
            elif temp_3pump < TARGET_3PUMP_TEMP_MIN + 1:  # Too cold (<46K), increase power
                new_power = min(100, current_power_output2 + POWER_ADJUSTMENT_STEP)
                if new_power != current_power_output2:
                    try:
                        output_ctrl.set_outputs(2, new_power)
                        log_print(f"3_Pump {temp_3pump:.2f}K too low, increasing Output 2 to {new_power:.1f}%")
                        current_power_output2 = new_power
                    except Exception as e:
                        log_print(f"Error adjusting Output 2: {e}")
        
        # Control 4_Pump (Output 1)
        if temp_4pump is not None and temp_4pump >= TARGET_4PUMP_TEMP_MIN:
            if temp_4pump > TARGET_4PUMP_TEMP_IDEAL:  # Above ideal (>55K), decrease power
                new_power = max(0, current_power_output1 - POWER_ADJUSTMENT_STEP)
                if new_power != current_power_output1:
                    try:
                        output_ctrl.set_outputs(1, new_power)
                        log_print(f"4_Pump {temp_4pump:.2f}K above ideal, reducing Output 1 to {new_power:.1f}%")
                        current_power_output1 = new_power
                    except Exception as e:
                        log_print(f"Error adjusting Output 1: {e}")
            
            elif temp_4pump < TARGET_4PUMP_TEMP_MIN + 2:  # Too cold (<52K), increase power
                new_power = min(100, current_power_output1 + POWER_ADJUSTMENT_STEP)
                if new_power != current_power_output1:
                    try:
                        output_ctrl.set_outputs(1, new_power)
                        log_print(f"4_Pump {temp_4pump:.2f}K too low, increasing Output 1 to {new_power:.1f}%")
                        current_power_output1 = new_power
                    except Exception as e:
                        log_print(f"Error adjusting Output 1: {e}")
        
        time.sleep(TEMP_CHECK_INTERVAL)
    
    return pumps_in_range

def query_output_brief(output_ctrl, output_num):
    """Query output and print only MOUT and HTR/AOUT lines"""
    try:
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            output_ctrl.query_outputs(output_num)
        
        lines = f.getvalue().strip().split('\n')
        
        # Print first 2 lines (MOUT and HTR/AOUT)
        for i, line in enumerate(lines[:2]):
            if line.strip():
                log_print(f"  {line}")
                
    except Exception as e:
        log_print(f"  Error querying output {output_num}: {e}")

def check_initial_status(csv_path):
    """Check and print values from CSV and query output statuses"""
    log_print("Current sensor readings:")
    
    if not os.path.exists(csv_path):
        log_print(f"Error: CSV file '{csv_path}' not found")
        return False
    
    try:
        # Read the CSV using fixed-width parsing
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 2:
            log_print("CSV file has no data rows")
            return False
            
        # Parse the last data line
        last_line = lines[-1].rstrip('\n')
        values = parse_fixed_width_line(last_line, COLUMN_WIDTHS)
        
        # Create a dictionary of header:value pairs
        data = dict(zip(HEADERS, values))
        
        # Print only temperature values
        for temp_col in TEMP_COLUMNS:
            if temp_col in data:
                log_print(f"{temp_col}: {data[temp_col]}")
        
        # Query output statuses
        log_print("Output statuses:")
        try:
            from lakeshore350.outputs import OutputController
        except ImportError:
            # Fallback for when running as standalone
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from lakeshore350.outputs import OutputController
        
        port = "/dev/ttyUSB2"
        output_ctrl = OutputController(port=port)
        
        for output_num in [1, 2, 3, 4]:
            log_print(f"Output {output_num}:")
            query_output_brief(output_ctrl, output_num)
        
        return True
    except Exception as e:
        log_print(f"Error reading CSV or querying outputs: {e}")
        return False

def ramp_output(output_ctrl, output_num, target_percent, duration_minutes):
    """Ramp output to target percent over duration"""
    steps = 10  # Number of increments
    step_percent = target_percent / steps
    step_duration = (duration_minutes * 60) / steps  # Convert to seconds
    
    for step in range(1, steps + 1):
        percent = step * step_percent
        try:
            output_ctrl.set_outputs(output_num, percent)
            log_print(f"Output {output_num} set to {percent:.1f}%")
        except Exception as e:
            log_print(f"Error setting output {output_num}: {e}")
        
        if step < steps:  # Don't wait after the last step
            time.sleep(step_duration)

def monitor_head_stabilization(csv_path, stop_event, wait_for_pumps_event):
    """Monitor 3_Head and 4_Head temperatures and detect when they stabilize"""
    head3_readings = []
    head4_readings = []
    
    log_print("Starting head temperature stabilization monitoring...")
    log_print(f"  Waiting for pumps to reach target ranges before checking head stability...")
    log_print(f"  Stabilization criteria: {HEAD_STABILIZATION_TOLERANCE}K change over {HEAD_STABILIZATION_WINDOW} readings")
    log_print(f"  Check interval: {HEAD_CHECK_INTERVAL} seconds")
    
    # Wait for pumps to reach target ranges
    while not wait_for_pumps_event.is_set() and not stop_event.is_set():
        time.sleep(1)
    
    if stop_event.is_set():
        return False
        
    log_print("Pumps are in target ranges - now monitoring head stabilization...")
    
    while not stop_event.is_set():
        temp_3head = get_current_temp_from_csv(csv_path, "3_Head_Temp_K")
        temp_4head = get_current_temp_from_csv(csv_path, "4_Head_Temp_K")
        
        if temp_3head is not None:
            head3_readings.append(temp_3head)
            # Keep only the last N readings for stability check
            if len(head3_readings) > HEAD_STABILIZATION_WINDOW:
                head3_readings.pop(0)
        
        if temp_4head is not None:
            head4_readings.append(temp_4head)
            # Keep only the last N readings for stability check
            if len(head4_readings) > HEAD_STABILIZATION_WINDOW:
                head4_readings.pop(0)
        
        # Check if both heads have stabilized
        head3_stable = is_temperature_stable(head3_readings, "3_Head")
        head4_stable = is_temperature_stable(head4_readings, "4_Head")
        
        if head3_stable and head4_stable:
            log_print("Both 3_Head and 4_Head temperatures have stabilized!")
            log_print(f"  3_Head final temp: {temp_3head:.3f}K")
            log_print(f"  4_Head final temp: {temp_4head:.3f}K")
            return True  # Signal that stabilization is complete
        
        # Log current status
        if len(head3_readings) >= HEAD_STABILIZATION_WINDOW and len(head4_readings) >= HEAD_STABILIZATION_WINDOW:
            head3_change = abs(max(head3_readings) - min(head3_readings))
            head4_change = abs(max(head4_readings) - min(head4_readings))
            log_print(f"Head temps - 3Head: {temp_3head:.3f}K (change: {head3_change:.3f}K, stable: {head3_stable}), 4Head: {temp_4head:.3f}K (change: {head4_change:.3f}K, stable: {head4_stable})")
        else:
            # Still collecting initial readings
            log_print(f"Head temps - 3Head: {temp_3head:.3f}K, 4Head: {temp_4head:.3f}K (collecting readings: {len(head3_readings)}/{HEAD_STABILIZATION_WINDOW})")
        
        time.sleep(HEAD_CHECK_INTERVAL)
    
    return False

def is_temperature_stable(readings, sensor_name):
    """Check if temperature readings show stability"""
    if len(readings) < HEAD_STABILIZATION_WINDOW:
        return False
    
    # Calculate the range (max - min) over the window
    temp_range = max(readings) - min(readings)
    
    # Also check if the trend is not decreasing significantly
    # (temperature should not be dropping more than tolerance between first and last reading)
    trend_change = readings[0] - readings[-1]  # Positive if decreasing
    
    # Stable if: small range AND not decreasing significantly
    is_stable = (temp_range <= HEAD_STABILIZATION_TOLERANCE and 
                 trend_change <= HEAD_STABILIZATION_TOLERANCE)
    
    return is_stable

def switch_heating_sequence(output_ctrl):
    """Turn off 4pump (Output 1) and ramp up 4-switch (Output 4)"""
    log_print("Starting switch heating sequence...")
    
    # Turn off 4pump (Output 1)
    try:
        output_ctrl.set_outputs(1, 0)
        log_print("4pump (Output 1) turned off - set to 0%")
    except Exception as e:
        log_print(f"Error turning off Output 1: {e}")
    
    # Ramp up 4-switch (Output 4) to target percentage
    log_print(f"Ramping 4-switch (Output 4) to {OUTPUT4_TARGET_PERCENT}% over {OUTPUT4_RAMP_TIME_MINUTES} minutes...")
    ramp_output(output_ctrl, 4, OUTPUT4_TARGET_PERCENT, OUTPUT4_RAMP_TIME_MINUTES)
    
    log_print("Switch heating sequence completed.")

def monitor_4head_cooldown(csv_path, output_ctrl, stop_event):
    """Monitor 4_Head temperature and trigger 3-switch when it drops below 2K"""
    log_print("Starting 4_Head cooldown monitoring...")
    log_print(f"  Target threshold: {HEAD_4_TARGET_TEMP}K")
    log_print(f"  Check interval: {HEAD_4_CHECK_INTERVAL} seconds")
    log_print("  Will trigger 3pump shutdown and 3-switch activation when threshold is reached")
    
    while not stop_event.is_set():
        temp_4head = get_current_temp_from_csv(csv_path, "4_Head_Temp_K")
        
        if temp_4head is not None:
            log_print(f"4_Head_Temp_K: {temp_4head:.3f}K (target: <{HEAD_4_TARGET_TEMP}K)")
            
            if temp_4head < HEAD_4_TARGET_TEMP:
                log_print(f"4_Head temperature {temp_4head:.3f}K has dropped below {HEAD_4_TARGET_TEMP}K!")
                log_print("Initiating 3pump shutdown and 3-switch activation...")
                
                # Turn off 3pump (Output 2)
                try:
                    output_ctrl.set_outputs(2, 0)
                    log_print("3pump (Output 2) turned off - set to 0%")
                except Exception as e:
                    log_print(f"Error turning off Output 2: {e}")
                
                # Ramp up 3-switch (Output 3)
                log_print(f"Ramping 3-switch (Output 3) to {OUTPUT3_TARGET_PERCENT}% over {OUTPUT3_RAMP_TIME_MINUTES} minutes...")
                ramp_output(output_ctrl, 3, OUTPUT3_TARGET_PERCENT, OUTPUT3_RAMP_TIME_MINUTES)
                log_print("3-switch activation completed.")
                
                return True  # Signal that cooldown threshold was reached
        else:
            log_print("4_Head temperature data not available")
        
        time.sleep(HEAD_4_CHECK_INTERVAL)
    
    return False

def pump_heating(csv_path):
    """Ramp outputs and start dual pump temperature monitoring with head stabilization"""
    log_print("Starting pump heating sequence...")
    
    try:
        from lakeshore350.outputs import OutputController
    except ImportError:
        # Fallback for when running as standalone
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from lakeshore350.outputs import OutputController
    
    port = "/dev/ttyUSB2"
    output_ctrl = OutputController(port=port)
    
    # Ramp outputs simultaneously first
    thread1 = threading.Thread(target=ramp_output, args=(output_ctrl, 1, OUTPUT1_TARGET_PERCENT, OUTPUT1_RAMP_TIME_MINUTES))
    thread2 = threading.Thread(target=ramp_output, args=(output_ctrl, 2, OUTPUT2_TARGET_PERCENT, OUTPUT2_RAMP_TIME_MINUTES))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    log_print("Initial pump heating sequence completed.")
    log_print("Waiting for pumps to reach minimum temperatures...")
    log_print(f"  3_Pump must reach at least {TARGET_3PUMP_TEMP_MIN}K")
    log_print(f"  4_Pump must reach at least {TARGET_4PUMP_TEMP_MIN}K")
    
    # Wait for pumps to reach minimum temperatures
    pumps_reached_minimums = False
    try:
        while not pumps_reached_minimums:
            temp_3pump = get_current_temp_from_csv(csv_path, "3_Pump_Temp_K")
            temp_4pump = get_current_temp_from_csv(csv_path, "4_Pump_Temp_K")
            
            # Check if both pumps are at minimum temperatures
            pump3_at_min = (temp_3pump is not None and temp_3pump >= TARGET_3PUMP_TEMP_MIN)
            pump4_at_min = (temp_4pump is not None and temp_4pump >= TARGET_4PUMP_TEMP_MIN)
            
            if pump3_at_min and pump4_at_min:
                pumps_reached_minimums = True
                log_print("Both pumps have reached minimum temperatures!")
                log_print(f"  3_Pump: {temp_3pump:.2f}K (min: {TARGET_3PUMP_TEMP_MIN}K)")
                log_print(f"  4_Pump: {temp_4pump:.2f}K (min: {TARGET_4PUMP_TEMP_MIN}K)")
                break
            
            # Log current status with detailed info
            if temp_3pump is not None and temp_4pump is not None:
                log_print(f"Waiting for minimums - 3Pump: {temp_3pump:.2f}K ({'✓' if pump3_at_min else f'✗ need {TARGET_3PUMP_TEMP_MIN}K'}), 4Pump: {temp_4pump:.2f}K ({'✓' if pump4_at_min else f'✗ need {TARGET_4PUMP_TEMP_MIN}K'})")
            else:
                log_print("Waiting for pump temperature data...")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        log_print("Manual stop requested...")
        return
    
    # Now start pump temperature control and head stabilization monitoring
    log_print("Starting pump temperature control and head stabilization monitoring...")
    
    # Create stop events
    pump_monitor_stop = threading.Event()
    head_monitor_stop = threading.Event()
    
    # Start pump temperature monitoring/control thread
    pump_monitor_thread = threading.Thread(
        target=monitor_and_control_pumps, 
        args=(output_ctrl, csv_path, pump_monitor_stop)
    )
    pump_monitor_thread.daemon = True
    pump_monitor_thread.start()
    
    # Start head temperature stabilization monitoring thread (with detailed logging)
    head_monitor_thread = threading.Thread(
        target=monitor_head_stabilization_detailed,
        args=(csv_path, head_monitor_stop)
    )
    head_monitor_thread.daemon = True
    head_monitor_thread.start()
    
    stabilization_achieved = False
    
    try:
        # Wait for head stabilization or manual interrupt
        while not head_monitor_stop.is_set():
            if not head_monitor_thread.is_alive():
                # Head monitoring thread completed (stabilization achieved)
                log_print("Head stabilization detected!")
                stabilization_achieved = True
                break
            time.sleep(1)
    except KeyboardInterrupt:
        log_print("Manual stop requested...")
    
    # Clean shutdown of monitoring threads
    log_print("Stopping temperature monitoring...")
    pump_monitor_stop.set()
    head_monitor_stop.set()
    
    # Wait for threads to finish
    pump_monitor_thread.join(timeout=5)
    head_monitor_thread.join(timeout=5)
    
    # If stabilization was achieved, proceed with switch heating
    if stabilization_achieved:
        switch_heating_sequence(output_ctrl)
        
        # After switch heating, monitor 4head cooldown
        cooldown_stop = threading.Event()
        cooldown_achieved = False
        
        try:
            # Start 4head cooldown monitoring
            cooldown_thread = threading.Thread(
                target=monitor_4head_cooldown,
                args=(csv_path, output_ctrl, cooldown_stop)
            )
            cooldown_thread.daemon = True
            cooldown_thread.start()
            
            # Wait for cooldown completion or manual interrupt
            while not cooldown_stop.is_set():
                if not cooldown_thread.is_alive():
                    # Cooldown monitoring completed (threshold reached)
                    cooldown_achieved = True
                    break
                time.sleep(1)
                
        except KeyboardInterrupt:
            log_print("Manual stop requested during cooldown monitoring...")
            cooldown_stop.set()
        
        # Clean shutdown of cooldown monitoring
        cooldown_stop.set()
        cooldown_thread.join(timeout=5)
        
        if cooldown_achieved:
            log_print("4_Head cooldown threshold reached and 3-switch activation completed.")
        else:
            log_print("4_Head cooldown monitoring stopped before threshold was reached.")
    else:
        log_print("Head stabilization not achieved - skipping switch heating sequence.")
    
    log_print("GL7 calibration sequence completed.")

def monitor_head_stabilization_detailed(csv_path, stop_event):
    """Monitor 3_Head and 4_Head temperatures with detailed logging"""
    head3_readings = []
    head4_readings = []
    
    log_print("Starting head temperature stabilization monitoring...")
    log_print(f"  Stabilization criteria: {HEAD_STABILIZATION_TOLERANCE}K change over {HEAD_STABILIZATION_WINDOW} readings")
    log_print(f"  Check interval: {HEAD_CHECK_INTERVAL} seconds")
    
    while not stop_event.is_set():
        # Get current temperatures
        temp_3head = get_current_temp_from_csv(csv_path, "3_Head_Temp_K")
        temp_4head = get_current_temp_from_csv(csv_path, "4_Head_Temp_K")
        temp_3pump = get_current_temp_from_csv(csv_path, "3_Pump_Temp_K")
        temp_4pump = get_current_temp_from_csv(csv_path, "4_Pump_Temp_K")
        
        # Always log pump temps during head monitoring
        pump_status = f"Pump temps during head monitoring - "
        if temp_3pump is not None:
            pump3_in_range = TARGET_3PUMP_TEMP_MIN <= temp_3pump <= TARGET_3PUMP_TEMP_MAX
            pump_status += f"3Pump: {temp_3pump:.2f}K ({'✓' if pump3_in_range else '✗'}), "
        else:
            pump_status += "3Pump: No data, "
            
        if temp_4pump is not None:
            pump4_in_range = TARGET_4PUMP_TEMP_MIN <= temp_4pump <= TARGET_4PUMP_TEMP_MAX
            pump_status += f"4Pump: {temp_4pump:.2f}K ({'✓' if pump4_in_range else '✗'})"
        else:
            pump_status += "4Pump: No data"
            
        log_print(pump_status)
        
        if temp_3head is not None:
            head3_readings.append(temp_3head)
            # Keep only the last N readings for stability check
            if len(head3_readings) > HEAD_STABILIZATION_WINDOW:
                head3_readings.pop(0)
        
        if temp_4head is not None:
            head4_readings.append(temp_4head)
            # Keep only the last N readings for stability check
            if len(head4_readings) > HEAD_STABILIZATION_WINDOW:
                head4_readings.pop(0)
        
        # Check if both heads have stabilized (with detailed logging)
        head3_stable = False
        head4_stable = False
        
        if len(head3_readings) >= HEAD_STABILIZATION_WINDOW:
            head3_change = abs(max(head3_readings) - min(head3_readings))
            head3_trend = head3_readings[0] - head3_readings[-1]  # Positive if decreasing
            head3_stable = (head3_change <= HEAD_STABILIZATION_TOLERANCE and 
                           head3_trend <= HEAD_STABILIZATION_TOLERANCE)
            
            log_print(f"3_Head analysis: temp={temp_3head:.3f}K, change={head3_change:.3f}K, trend={head3_trend:.3f}K, stable={head3_stable}")
            log_print(f"  Readings: {[f'{r:.3f}' for r in head3_readings]}")
        else:
            log_print(f"3_Head: collecting readings ({len(head3_readings)}/{HEAD_STABILIZATION_WINDOW}) - current: {temp_3head:.3f}K")
            
        if len(head4_readings) >= HEAD_STABILIZATION_WINDOW:
            head4_change = abs(max(head4_readings) - min(head4_readings))
            head4_trend = head4_readings[0] - head4_readings[-1]  # Positive if decreasing
            head4_stable = (head4_change <= HEAD_STABILIZATION_TOLERANCE and 
                           head4_trend <= HEAD_STABILIZATION_TOLERANCE)
            
            log_print(f"4_Head analysis: temp={temp_4head:.3f}K, change={head4_change:.3f}K, trend={head4_trend:.3f}K, stable={head4_stable}")
            log_print(f"  Readings: {[f'{r:.3f}' for r in head4_readings]}")
        else:
            log_print(f"4_Head: collecting readings ({len(head4_readings)}/{HEAD_STABILIZATION_WINDOW}) - current: {temp_4head:.3f}K")
        
        if head3_stable and head4_stable:
            log_print("Both 3_Head and 4_Head temperatures have stabilized!")
            log_print(f"  3_Head final temp: {temp_3head:.3f}K")
            log_print(f"  4_Head final temp: {temp_4head:.3f}K")
            return True  # Signal that stabilization is complete
        
        log_print("---")
        time.sleep(HEAD_CHECK_INTERVAL)
    
    return False

def main(csv_file=None):
    log_path = setup_logging()
    log_print(f"Log file: {log_path}", include_timestamp=False)
    
    if csv_file:
        log_print(f"CSV file: {csv_file}", include_timestamp=False)
    
    try:
        if csv_file:
            check_initial_status(csv_file)
            pump_heating(csv_file)
        else:
            log_print("No CSV file provided")
    finally:
        close_logging()

if __name__ == "__main__":
    # Allow running directly with CSV as argument
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(csv_file)