#!/usr/bin/env python3
"""
Heater control query functionality for Lakeshore 350 / GL7
Handles both relay heaters and analog switch heaters
Safe query-only operations - doesn't change any settings
"""

import time

class HeaterController:
    def __init__(self, send_command_func):
        """Initialize with a send_command function from the main controller"""
        self.send_command = send_command_func
    
    def query_relay_heater(self, relay_num):
        """Query relay heater status (safe - read only)"""
        # Query relay configuration
        config_response = self.send_command(f"RELAY? {relay_num}")
        
        # Query relay current state  
        status_response = self.send_command(f"RELAYST? {relay_num}")
        
        result = {
            'relay_number': relay_num,
            'config_raw': config_response,
            'status_raw': status_response,
            'config_parsed': None,
            'status_parsed': None
        }
        
        # Parse configuration response
        if config_response:
            try:
                parts = config_response.split(',')
                if len(parts) >= 1:
                    mode = int(parts[0])
                    mode_text = {0: "Off", 1: "On", 2: "Alarm"}.get(mode, f"Unknown({mode})")
                    result['config_parsed'] = {'mode': mode, 'mode_text': mode_text}
                    
                    if len(parts) >= 3 and mode == 2:  # Alarm mode
                        input_alarm = parts[1]
                        alarm_type = int(parts[2])
                        alarm_text = {0: "Low", 1: "High", 2: "Both"}.get(alarm_type, f"Unknown({alarm_type})")
                        result['config_parsed'].update({
                            'input_alarm': input_alarm,
                            'alarm_type': alarm_type,
                            'alarm_text': alarm_text
                        })
            except (ValueError, IndexError):
                pass
        
        # Parse status response
        if status_response:
            try:
                status = int(status_response)
                status_text = {0: "OFF (heater not energized)", 1: "ON (heater energized)"}.get(status, f"Unknown({status})")
                result['status_parsed'] = {'status': status, 'status_text': status_text}
            except ValueError:
                pass
        
        return result
    
    def query_analog_heater(self, output_num):
        """Query analog heater/switch settings (safe - read only)"""
        config_response = self.send_command(f"ANALOG? {output_num}")
        
        result = {
            'output_number': output_num,
            'config_raw': config_response,
            'config_parsed': None
        }
        
        # Parse the response
        if config_response:
            try:
                parts = config_response.split(',')
                if len(parts) >= 5:
                    input_ch = int(parts[0])
                    units = int(parts[1])
                    high_val = float(parts[2])
                    low_val = float(parts[3])
                    polarity = int(parts[4])
                    
                    input_text = {0: "None", 1: "Input A", 2: "Input B", 3: "Input C", 4: "Input D"}.get(input_ch, f"Input {input_ch}")
                    units_text = {1: "Kelvin", 2: "Celsius", 3: "Sensor Units"}.get(units, f"Units {units}")
                    polarity_text = {0: "Unipolar (0 to +10V)", 1: "Bipolar (-10V to +10V)"}.get(polarity, f"Polarity {polarity}")
                    
                    result['config_parsed'] = {
                        'input_channel': input_ch,
                        'input_text': input_text,
                        'units': units,
                        'units_text': units_text,
                        'high_value': high_val,
                        'low_value': low_val,
                        'polarity': polarity,
                        'polarity_text': polarity_text
                    }
            except (ValueError, IndexError):
                pass
        
        return result
    
    def query_all_relay_heaters(self):
        """Query both relay heaters (He4 and He3 pump heaters)"""
        results = {}
        for relay_num in [1, 2]:
            results[f'relay_heater_{relay_num}'] = self.query_relay_heater(relay_num)
            time.sleep(0.1)  # Small delay between queries
        return results
    
    def query_all_analog_heaters(self):
        """Query both analog heaters/switches (He4 and He3 pump heat switches)"""
        results = {}
        for output_num in [3, 4]:
            results[f'analog_heater_{output_num}'] = self.query_analog_heater(output_num)
            time.sleep(0.1)  # Small delay between queries
        return results
    
    def query_all_heaters(self):
        """Query all heater systems (relays + analogs)"""
        results = {}
        results.update(self.query_all_relay_heaters())
        results.update(self.query_all_analog_heaters())
        return results
