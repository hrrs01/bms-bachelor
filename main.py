import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import numpy as np
import json
import csv

class BMSMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battery Management System Monitor")
        self.root.geometry("1200x800")
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.voltages_tab = ttk.Frame(self.notebook)
        self.temperatures_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        self.can_tab = ttk.Frame(self.notebook)
        self.ocv_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.voltages_tab, text="Cell Voltages")
        self.notebook.add(self.temperatures_tab, text="Temperatures")
        self.notebook.add(self.config_tab, text="BMS Configuration")
        self.notebook.add(self.can_tab, text="CAN Messages")
        self.notebook.add(self.ocv_tab, text="OCV Mapping")
        
        #bugfix
        self.bms_parameters = {}

        # Setup UI components
        self.setup_voltage_tab()
        self.setup_temperature_tab()
        self.setup_config_tab()
        self.setup_can_tab()
        self.setup_ocv_tab()
        
        # Add refresh button
        self.refresh_btn = tk.Button(root, text="Refresh Data", command=self.refresh_data)
        self.refresh_btn.pack(pady=10)
        
        # Initial data load
        self.refresh_data()
    
    def setup_voltage_tab(self):
        main_frame = tk.Frame(self.voltages_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas with scrollbar for voltage displays
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for voltage displays
        self.voltage_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.voltage_frame, anchor="nw")
        
        # Create voltage entry boxes (7 columns x 20 rows)
        self.voltage_entries = []
        for i in range(140):
            row = i // 14
            col = i % 14
            
            frame = tk.Frame(self.voltage_frame)
            frame.grid(row=row, column=col, padx=5, pady=5)
            
            label = tk.Label(frame, text=f"Cell {i+1}")
            label.pack()
            
            entry = tk.Entry(frame, width=8, justify='center', readonlybackground='white')
            entry.pack()
            entry.config(state='readonly')
            self.voltage_entries.append(entry)
        
        # Configure scrolling
        self.voltage_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def setup_temperature_tab(self):
        main_frame = tk.Frame(self.temperatures_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas with scrollbar for temperature displays
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for temperature displays
        self.temp_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.temp_frame, anchor="nw")
        
        # Create temperature entry boxes (6 columns x 20 rows)
        self.temp_entries = []
        for i in range(120):
            row = i // 14
            col = i % 14
            
            frame = tk.Frame(self.temp_frame)
            frame.grid(row=row, column=col, padx=5, pady=5)
            
            label = tk.Label(frame, text=f"Temp {i+1}")
            label.pack()
            
            entry = tk.Entry(frame, width=8, justify='center', readonlybackground='white')
            entry.pack()
            entry.config(state='readonly')
            self.temp_entries.append(entry)
        
        # Configure scrolling
        self.temp_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def setup_config_tab(self):
        # Create a canvas with scrollbar for configuration
        main_frame = tk.Frame(self.config_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        settings_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        
        # Battery Configuration Section
        battery_frame = ttk.LabelFrame(settings_frame, text="Battery Configuration")
        battery_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Cells in series per slave
        ttk.Label(battery_frame, text="Cells in series per slave:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.cells_series_entry = ttk.Entry(battery_frame, width=10)
        self.cells_series_entry.grid(row=0, column=1, padx=10, pady=5)
        self.cells_series_entry.insert(0, "12")
        
        # Cells in parallel
        ttk.Label(battery_frame, text="Cells in parallel:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.cells_parallel_entry = ttk.Entry(battery_frame, width=10)
        self.cells_parallel_entry.grid(row=1, column=1, padx=10, pady=5)
        self.cells_parallel_entry.insert(0, "4")
        
        # Number of slaves
        ttk.Label(battery_frame, text="Number of slaves:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.num_slaves_entry = ttk.Entry(battery_frame, width=10)
        self.num_slaves_entry.grid(row=2, column=1, padx=10, pady=5)
        self.num_slaves_entry.insert(0, "12")
        
        # Calculate button
        ttk.Button(battery_frame, text="Calculate", command=self.calculate_total_cells).grid(row=3, column=0, padx=10, pady=5)
        
        # Total cells (read-only)
        ttk.Label(battery_frame, text="Total number of cells:").grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        self.total_cells_entry = ttk.Entry(battery_frame, width=10, state='readonly')
        self.total_cells_entry.grid(row=3, column=2, padx=10, pady=5)
        
        # Temperature Sensor Configuration
        temp_sensor_frame = ttk.LabelFrame(settings_frame, text="Temperature Sensor Configuration")
        temp_sensor_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Temperature sensors per slave
        ttk.Label(temp_sensor_frame, text="Temperature sensors per slave:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.temp_sensors_entry = ttk.Entry(temp_sensor_frame, width=10)
        self.temp_sensors_entry.grid(row=0, column=1, padx=10, pady=5)
        self.temp_sensors_entry.insert(0, "10")
        
        # Multiplexed checkbox
        self.multiplexed_var = tk.BooleanVar(value=False)
        self.multiplexed_check = ttk.Checkbutton(temp_sensor_frame, text="Multiplexed Temperature Sensors", 
                                          variable=self.multiplexed_var, command=self.toggle_mux_settings)
        self.multiplexed_check.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Multiplexing pin (initially disabled)
        self.mux_pin_label = ttk.Label(temp_sensor_frame, text="Multiplexing Pin:")
        self.mux_pin_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.mux_pin_label.config(state="disabled")
        
        self.mux_pin_entry = ttk.Entry(temp_sensor_frame, width=10)
        self.mux_pin_entry.grid(row=2, column=1, padx=10, pady=5)
        self.mux_pin_entry.insert(0, "0")
        self.mux_pin_entry.config(state="disabled")
        
        # Voltage thresholds
        voltage_frame = ttk.LabelFrame(settings_frame, text="Voltage Thresholds (V)")
        voltage_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(voltage_frame, text="Cell Overvoltage:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.overvoltage_entry = ttk.Entry(voltage_frame, width=10)
        self.overvoltage_entry.grid(row=0, column=1, padx=10, pady=5)
        self.overvoltage_entry.insert(0, "4.20")
        
        ttk.Label(voltage_frame, text="Cell Undervoltage:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.undervoltage_entry = ttk.Entry(voltage_frame, width=10)
        self.undervoltage_entry.grid(row=1, column=1, padx=10, pady=5)
        self.undervoltage_entry.insert(0, "2.80")
        
        # Temperature thresholds
        temp_frame = ttk.LabelFrame(settings_frame, text="Temperature Thresholds (°C)")
        temp_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(temp_frame, text="Overtemperature:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.overtemp_entry = ttk.Entry(temp_frame, width=10)
        self.overtemp_entry.grid(row=0, column=1, padx=10, pady=5)
        self.overtemp_entry.insert(0, "55.0")
        
        ttk.Label(temp_frame, text="Undertemperature:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.undertemp_entry = ttk.Entry(temp_frame, width=10)
        self.undertemp_entry.grid(row=1, column=1, padx=10, pady=5)
        self.undertemp_entry.insert(0, "-10.0")
        
        # Balance settings
        balance_frame = ttk.LabelFrame(settings_frame, text="Balancing Configuration")
        balance_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(balance_frame, text="Balance Threshold (V):").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.balance_threshold_entry = ttk.Entry(balance_frame, width=10)
        self.balance_threshold_entry.grid(row=0, column=1, padx=10, pady=5)
        self.balance_threshold_entry.insert(0, "0.01")
        
        ttk.Label(balance_frame, text="Balance Start Voltage:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.balance_start_entry = ttk.Entry(balance_frame, width=10)
        self.balance_start_entry.grid(row=1, column=1, padx=10, pady=5)
        self.balance_start_entry.insert(0, "3.90")
        
        self.balance_enable_var = tk.BooleanVar(value=True)
        balance_check = ttk.Checkbutton(balance_frame, text="Enable Cell Balancing", variable=self.balance_enable_var)
        balance_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Communication settings
        comm_frame = ttk.LabelFrame(settings_frame, text="Communication Settings")
        comm_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(comm_frame, text="CAN Bus ID:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.can_id_entry = ttk.Entry(comm_frame, width=10)
        self.can_id_entry.grid(row=0, column=1, padx=10, pady=5)
        self.can_id_entry.insert(0, "0x680")
        
        ttk.Label(comm_frame, text="Update Rate (ms):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.update_rate_entry = ttk.Entry(comm_frame, width=10)
        self.update_rate_entry.grid(row=1, column=1, padx=10, pady=5)
        self.update_rate_entry.insert(0, "500")
        
        # Save button
        save_btn = ttk.Button(settings_frame, text="Save Configuration", command=self.save_config)
        save_btn.pack(pady=20)
        
        # Configure scrolling
        settings_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Calculate total cells initially
        self.calculate_total_cells()

    def setup_can_tab(self):
        # Create a frame for organizing content
        main_frame = ttk.Frame(self.can_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas with scrollbar for temperature displays
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.can_frame = ttk.Frame(canvas)
        canvas.create_window((0,0), width=self.can_frame.winfo_screenwidth() ,window=self.can_frame, anchor="nw")

        # Create a notebook for multiple CAN-related tabs
        can_notebook = ttk.Notebook(self.can_frame)
        can_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab for message configuration
        msg_config_tab = ttk.Frame(can_notebook)
        can_notebook.add(msg_config_tab, text="Message Configuration")
        
        # Tab for parameter mapping
        param_mapping_tab = ttk.Frame(can_notebook)
        can_notebook.add(param_mapping_tab, text="Parameter Mapping")
                
        # Set up each tab
        self.setup_message_config_tab(msg_config_tab)
        self.setup_parameter_mapping_tab(param_mapping_tab)

    def setup_message_config_tab(self, parent):
        # CAN Message configuration
        config_frame = ttk.LabelFrame(parent, text="Create CAN Message")
        config_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Message ID
        ttk.Label(config_frame, text="CAN ID (hex):").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.can_msg_id_entry = ttk.Entry(config_frame, width=12)
        self.can_msg_id_entry.grid(row=0, column=1, padx=10, pady=5)
        self.can_msg_id_entry.insert(0, "0x100")
        
        # Message type
        ttk.Label(config_frame, text="Message Type:").grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        self.msg_type_var = tk.StringVar(value="Standard")
        msg_type_combo = ttk.Combobox(config_frame, textvariable=self.msg_type_var, 
                                    values=["Standard", "Extended"], width=12, state="readonly")
        msg_type_combo.grid(row=0, column=3, padx=10, pady=5)
        
        # DLC (Data Length Code)
        ttk.Label(config_frame, text="DLC (0-8):").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.dlc_var = tk.StringVar(value="8")
        dlc_combo = ttk.Combobox(config_frame, textvariable=self.dlc_var, 
                                values=["0", "1", "2", "3", "4", "5", "6", "7", "8"], width=5, state="readonly")
        dlc_combo.grid(row=1, column=1, padx=10, pady=5)
        dlc_combo.bind("<<ComboboxSelected>>", self.update_data_bytes_frame)
        
        # RTR checkbox
        self.rtr_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="RTR", variable=self.rtr_var).grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        
        # Message name
        ttk.Label(config_frame, text="Message Name:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.msg_name_entry = ttk.Entry(config_frame, width=20)
        self.msg_name_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)
        self.msg_name_entry.insert(0, "BMS_Status")
        
        # Periodic checkbox
        self.periodic_var = tk.BooleanVar(value=True)
        periodic_check = ttk.Checkbutton(config_frame, text="Periodic Message", variable=self.periodic_var, 
                                        command=self.toggle_period_field)
        periodic_check.grid(row=2, column=3, padx=10, pady=5, sticky=tk.W)
        
        # Period (ms)
        ttk.Label(config_frame, text="Period (ms):").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.period_entry = ttk.Entry(config_frame, width=10)
        self.period_entry.grid(row=3, column=1, padx=10, pady=5)
        self.period_entry.insert(0, "1000")
        
        # Create a frame for the data bytes
        self.bytes_frame = ttk.LabelFrame(parent, text="Data Bytes")
        self.bytes_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Create data byte entries and parameter links - this will be populated by update_data_bytes_frame
        self.byte_entries = []
        self.byte_param_vars = []
        self.byte_param_combos = []
        
        # Initially populate data bytes
        self.update_data_bytes_frame()
        
        # Buttons for adding/testing CAN messages
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Add Message", command=self.add_can_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Transmit", command=self.test_can_transmit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_can_form).pack(side=tk.LEFT, padx=5)
        
        # Message List
        list_frame = ttk.LabelFrame(parent, text="Configured CAN Messages")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add listbox with scrollbar
        self.msg_list_frame = ttk.Frame(list_frame)
        self.msg_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.msg_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.msg_listbox = tk.Listbox(self.msg_list_frame, width=80, height=10)
        self.msg_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.msg_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.msg_listbox.yview)
        
        # Buttons for managing messages
        list_button_frame = ttk.Frame(list_frame)
        list_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(list_button_frame, text="Edit Selected", command=self.edit_can_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_button_frame, text="Delete Selected", command=self.delete_can_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_button_frame, text="Export Messages", command=self.export_can_messages).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_button_frame, text="Import Messages", command=self.import_can_messages).pack(side=tk.LEFT, padx=5)
        
        # Add a few example messages
        self.msg_listbox.insert(tk.END, "0x680 [8] BMS_Status (1000ms): SOC|Highest_Cell_V|Lowest_Cell_V|Avg_Cell_V|High_Temp|Low_Temp|Status|Flags")
        self.msg_listbox.insert(tk.END, "0x681 [8] Cell_Voltages (500ms): Cell_1|Cell_2|Cell_3|Cell_4|High_Cell_ID|Low_Cell_ID|00|00")
        self.msg_listbox.insert(tk.END, "0x682 [8] Temperature_Data (1000ms): Temp_1|Temp_2|Temp_3|Temp_4|High_Temp_ID|Low_Temp_ID|00|00")

    def setup_parameter_mapping_tab(self, parent):
        # Create a frame for organizing content
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a scrollable frame for parameter definitions
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        param_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=param_frame, anchor="nw")
        
        # Define the available BMS parameters
        self.bms_parameters = {
            # System parameters
            "SOC": {"description": "State of Charge (%)", "type": "uint8", "unit": "%", "scale": 1},
            "SOH": {"description": "State of Health (%)", "type": "uint8", "unit": "%", "scale": 1},
            "Current": {"description": "Pack Current (A)", "type": "int16", "unit": "A", "scale": 0.1},
            "Voltage": {"description": "Pack Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.1},
            "Power": {"description": "Pack Power (kW)", "type": "int16", "unit": "kW", "scale": 0.01},
            "Status": {"description": "BMS Status", "type": "uint8", "unit": "", "scale": 1},
            "Flags": {"description": "Error/Warning Flags", "type": "uint8", "unit": "", "scale": 1},
            
            # Cell voltage parameters
            "Highest_Cell_V": {"description": "Highest Cell Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "Lowest_Cell_V": {"description": "Lowest Cell Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "Delta_Cell_V": {"description": "Max Cell Voltage Difference (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "Avg_Cell_V": {"description": "Average Cell Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "High_Cell_ID": {"description": "Highest Voltage Cell ID", "type": "uint8", "unit": "", "scale": 1},
            "Low_Cell_ID": {"description": "Lowest Voltage Cell ID", "type": "uint8", "unit": "", "scale": 1},
            
            # Temperature parameters
            "High_Temp": {"description": "Highest Temperature (°C)", "type": "int8", "unit": "°C", "scale": 1},
            "Low_Temp": {"description": "Lowest Temperature (°C)", "type": "int8", "unit": "°C", "scale": 1},
            "Avg_Temp": {"description": "Average Temperature (°C)", "type": "int8", "unit": "°C", "scale": 1},
            "High_Temp_ID": {"description": "Highest Temperature Sensor ID", "type": "uint8", "unit": "", "scale": 1},
            "Low_Temp_ID": {"description": "Lowest Temperature Sensor ID", "type": "uint8", "unit": "", "scale": 1},
            
            # Cell balancing
            "Bal_Status": {"description": "Balancing Status", "type": "uint8", "unit": "", "scale": 1},
            "Cells_Balancing": {"description": "Number of Cells Balancing", "type": "uint8", "unit": "", "scale": 1},
            
            # Individual cell/temp values (these would be expanded based on configuration)
            "Cell_1": {"description": "Cell 1 Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "Cell_2": {"description": "Cell 2 Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "Cell_3": {"description": "Cell 3 Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            "Cell_4": {"description": "Cell 4 Voltage (V)", "type": "uint16", "unit": "V", "scale": 0.001},
            
            "Temp_1": {"description": "Temperature Sensor 1 (°C)", "type": "int8", "unit": "°C", "scale": 1},
            "Temp_2": {"description": "Temperature Sensor 2 (°C)", "type": "int8", "unit": "°C", "scale": 1},
            "Temp_3": {"description": "Temperature Sensor 3 (°C)", "type": "int8", "unit": "°C", "scale": 1},
            "Temp_4": {"description": "Temperature Sensor 4 (°C)", "type": "int8", "unit": "°C", "scale": 1},
            
            # Raw hex value (no parameter mapping)
            "": {"description": "Custom hex value", "type": "hex", "unit": "", "scale": 1},
        }
        
        # Add headers
        ttk.Label(param_frame, text="Parameter", font=("", 10, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(param_frame, text="Description", font=("", 10, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(param_frame, text="Type", font=("", 10, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Label(param_frame, text="Unit", font=("", 10, "bold")).grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        ttk.Label(param_frame, text="Scale", font=("", 10, "bold")).grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
        
        # Add parameter rows to the table
        row = 1
        for param_name, param_details in sorted(self.bms_parameters.items()):
            if param_name == "":
                continue  # Skip the empty parameter
                
            ttk.Label(param_frame, text=param_name).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
            ttk.Label(param_frame, text=param_details["description"]).grid(row=row, column=1, padx=10, pady=2, sticky=tk.W)
            ttk.Label(param_frame, text=param_details["type"]).grid(row=row, column=2, padx=10, pady=2, sticky=tk.W)
            ttk.Label(param_frame, text=param_details["unit"]).grid(row=row, column=3, padx=10, pady=2, sticky=tk.W)
            ttk.Label(param_frame, text=str(param_details["scale"])).grid(row=row, column=4, padx=10, pady=2, sticky=tk.W)
            row += 1
        
        # Add a button to customize parameters (for future expansion)
        ttk.Button(param_frame, text="Add Custom Parameter", command=self.add_custom_parameter).grid(
            row=row, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)
        
        ttk.Button(param_frame, text="Generate Cell Parameters", command=self.generate_cell_parameters).grid(
            row=row, column=2, columnspan=3, padx=10, pady=10, sticky=tk.W)
        
        # Configure canvas for scrolling
        param_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # Add some instructions
        instruction_frame = ttk.LabelFrame(parent, text="Instructions")
        instruction_frame.pack(fill=tk.X, padx=10, pady=10)
        
        instructions = (
            "1. Define CAN messages in the Message Configuration tab\n"
            "2. Use the parameter names from this table in the data byte fields\n"
            "3. Each parameter will be automatically encoded according to its type and scale\n"
            "4. For custom hex values, leave the parameter selection empty and enter the hex value"
        )
        
        ttk.Label(instruction_frame, text=instructions, justify="left").pack(padx=10, pady=10, anchor="w")

    def update_data_bytes_frame(self, event=None):
        # Clear existing widgets
        for widget in self.bytes_frame.winfo_children():
            widget.destroy()
        
        # Clear existing entries and vars lists
        self.byte_entries = []
        self.byte_param_vars = []
        self.byte_param_combos = []
        
        # Get number of bytes from DLC
        num_bytes = int(self.dlc_var.get())
        
        # Create a header row
        ttk.Label(self.bytes_frame, text="Byte").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.bytes_frame, text="Hex Value").grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.bytes_frame, text="Parameter").grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(self.bytes_frame, text="Description").grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.bytes_frame, text="Byte").grid(row=0, column=10, padx=5, pady=5)
        ttk.Label(self.bytes_frame, text="Hex Value").grid(row=0, column=11, padx=5, pady=5)
        ttk.Label(self.bytes_frame, text="Parameter").grid(row=0, column=12, padx=5, pady=5)
        ttk.Label(self.bytes_frame, text="Description").grid(row=0, column=13, padx=5, pady=5)
        
        # Create entries for each byte
        param_names = [""] + sorted([name for name in self.bms_parameters.keys() if name])
        y = 0
        z = 0
        for i in range(num_bytes):
            # Byte label
            if(i > 3):
                y = 4
                z = 10
            ttk.Label(self.bytes_frame, text=f"Byte {i}:").grid(row=i+1-y, column=0+z, padx=5, pady=5, sticky=tk.W)
            
            # Hex value entry
            byte_entry = ttk.Entry(self.bytes_frame, width=5)
            byte_entry.grid(row=i+1-y, column=1+z, padx=5, pady=5)
            byte_entry.insert(0, "00")
            self.byte_entries.append(byte_entry)
            
            # Parameter selection
            param_var = tk.StringVar(value="")
            param_combo = ttk.Combobox(self.bytes_frame, textvariable=param_var, values=param_names, width=15, state="readonly")
            param_combo.grid(row=i+1-y, column=2+z, padx=5, pady=5)
            param_combo.bind("<<ComboboxSelected>>", lambda e, idx=i: self.on_param_selected(e, idx))
            
            self.byte_param_vars.append(param_var)
            self.byte_param_combos.append(param_combo)
            
            # Description label (will be updated when a parameter is selected)
            desc_label = ttk.Label(self.bytes_frame, text="")
            desc_label.grid(row=i+1-y, column=3+z, padx=5, pady=5, sticky=tk.W)
            
            # Store the description label as an attribute of the combo
            param_combo.desc_label = desc_label

    def on_param_selected(self, event, byte_idx):
        # Get the selected parameter
        param_name = self.byte_param_vars[byte_idx].get()
        combo = self.byte_param_combos[byte_idx]
        
        # Update the description label
        if param_name in self.bms_parameters:
            desc = self.bms_parameters[param_name]["description"]
            combo.desc_label.config(text=desc)
            
            # If parameter is selected, disable the hex entry and show a placeholder
            if param_name:
                self.byte_entries[byte_idx].config(state="disabled")
                self.byte_entries[byte_idx].delete(0, tk.END)
                self.byte_entries[byte_idx].insert(0, "--")
            else:
                # If no parameter (blank), enable hex entry
                self.byte_entries[byte_idx].config(state="normal")
                self.byte_entries[byte_idx].delete(0, tk.END)
                self.byte_entries[byte_idx].insert(0, "00")
        else:
            combo.desc_label.config(text="")

    def setup_ocv_tab(self):
        # Create a frame for organizing content
        main_frame = ttk.Frame(self.ocv_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top control section - for temperature profile management
        control_frame = ttk.LabelFrame(main_frame, text="Temperature Profile Control")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Temperature profile selection and manipulation
        profile_frame = ttk.Frame(control_frame)
        profile_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(profile_frame, text="Temperature Profiles:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.profile_listbox = tk.Listbox(profile_frame, width=15, height=5)
        self.profile_listbox.grid(row=0, column=1, rowspan=2, padx=5, pady=5)
        
        # Add default temperature profiles
        self.temp_profiles = {
            "25°C": {"soc": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                    "ocv": [3.0, 3.2, 3.3, 3.35, 3.4, 3.5, 3.6, 3.7, 3.9, 4.1, 4.2]},
            "0°C": {"soc": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                    "ocv": [2.9, 3.1, 3.2, 3.25, 3.3, 3.4, 3.5, 3.6, 3.8, 4.0, 4.1]},
            "45°C": {"soc": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                    "ocv": [3.1, 3.3, 3.4, 3.45, 3.5, 3.6, 3.7, 3.8, 4.0, 4.15, 4.25]}
        }
        
        # Populate listbox with profile names
        for temp in self.temp_profiles.keys():
            self.profile_listbox.insert(tk.END, temp)
        
        # Select the first profile
        self.profile_listbox.select_set(0)
        self.current_profile = "25°C"
        self.profile_listbox.bind('<<ListboxSelect>>', self.on_profile_select)
        
        # Buttons for profile management
        ttk.Button(profile_frame, text="Add Profile", command=self.add_temp_profile).grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Button(profile_frame, text="Rename Profile", command=self.rename_temp_profile).grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        ttk.Button(profile_frame, text="Delete Profile", command=self.delete_temp_profile).grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Button(profile_frame, text="Clone Profile", command=self.clone_temp_profile).grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)
        
        # Main content area - split into panes
        self.content_panes = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.content_panes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane: OCV Data Input
        left_frame = ttk.LabelFrame(self.content_panes, text="OCV Mapping Data")
        self.content_panes.add(left_frame, weight=1)
        
        # Right pane: Graph display
        right_frame = ttk.LabelFrame(self.content_panes, text="OCV vs SOC Curve")
        self.content_panes.add(right_frame, weight=2)
        
        # OCV Data input
        self.data_frame = ttk.Frame(left_frame)
        self.data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a scrollable frame for OCV-SOC pairs
        canvas = tk.Canvas(self.data_frame)
        scrollbar = ttk.Scrollbar(self.data_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for OCV-SOC entries
        self.ocv_entries_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.ocv_entries_frame, anchor="nw")
        
        # Headers for the data table
        ttk.Label(self.ocv_entries_frame, text="SOC (%)").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.ocv_entries_frame, text="OCV (V)").grid(row=0, column=1, padx=5, pady=5)
        
        # Dictionary to hold entries for each profile
        self.profile_entries = {}
        
        # Create initial entries for the default profile
        self.create_profile_entries("25°C")
        
        # Configure canvas scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.ocv_entries_frame.bind("<Configure>", configure_scroll_region)
        
        # Buttons for managing OCV map
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Generate Graph", command=self.generate_ocv_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Point", command=self.add_ocv_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Last Point", command=self.remove_ocv_point).pack(side=tk.LEFT, padx=5)
        
        # Create multiple plot figures option
        self.show_all_curves_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(button_frame, text="Show All Temperature Curves", 
                    variable=self.show_all_curves_var,
                    command=self.generate_ocv_graph).pack(side=tk.LEFT, padx=5)
        
        # Export/Import buttons
        export_import_frame = ttk.Frame(left_frame)
        export_import_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(export_import_frame, text="Export All Profiles", 
                command=self.export_all_ocv_maps).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_import_frame, text="Import Profiles", 
                command=self.import_ocv_maps).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_import_frame, text="Export Current Profile", 
                command=self.export_current_ocv_map).pack(side=tk.LEFT, padx=5)
        
        # Create graph area
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add a graph information frame
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(info_frame, text="Graph Legend:").pack(side=tk.LEFT, padx=5)
        self.graph_info = ttk.Label(info_frame, text="")
        self.graph_info.pack(side=tk.LEFT, padx=5)
        
        # Generate the initial graph
        self.generate_ocv_graph()

    def calculate_total_cells(self):
        try:
            cells_series = int(self.cells_series_entry.get())
            num_slaves = int(self.num_slaves_entry.get())
            cells_parallel = int(self.cells_parallel_entry.get())
            
            # Calculate total cells
            total_cells = cells_series * num_slaves * cells_parallel
            
            # Update the read-only total cells field
            self.total_cells_entry.config(state='normal')
            self.total_cells_entry.delete(0, tk.END)
            self.total_cells_entry.insert(0, str(total_cells))
            self.total_cells_entry.config(state='readonly')
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers in all fields.")

    def toggle_mux_settings(self):
        if self.multiplexed_var.get():
            self.mux_pin_label.config(state="normal")
            self.mux_pin_entry.config(state="normal")
        else:
            self.mux_pin_label.config(state="disabled")
            self.mux_pin_entry.config(state="disabled")
    
    def toggle_period_field(self):
        if self.periodic_var.get():
            self.period_entry.config(state="normal")
        else:
            self.period_entry.config(state="disabled")
        
    def add_can_message(self):
        try:
            can_id = self.can_msg_id_entry.get()
            dlc = self.dlc_var.get()
            name = self.msg_name_entry.get()
            
            # Get period text
            period_text = f"({self.period_entry.get()}ms)" if self.periodic_var.get() else "(on-demand)"
            
            # Collect parameters/data bytes
            data_bytes = []
            for i in range(int(dlc)):
                param_name = self.byte_param_vars[i].get()
                if param_name:
                    data_bytes.append(param_name)
                else:
                    data_bytes.append(self.byte_entries[i].get())
            
            data_str = "|".join(data_bytes)
            
            # Create message string
            message = f"{can_id} [{dlc}] {name} {period_text}: {data_str}"
            
            # Add to listbox
            self.msg_listbox.insert(tk.END, message)
            
            messagebox.showinfo("Success", f"CAN message '{name}' has been added.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add message: {str(e)}")

    def test_can_transmit(self):
        try:
            can_id = self.can_msg_id_entry.get()
            dlc = self.dlc_var.get()
            
            # Create a test message with real values
            test_values = []
            for i in range(int(dlc)):
                param_name = self.byte_param_vars[i].get()
                if param_name:
                    # Get a simulated value for this parameter
                    hex_value = self.get_simulated_param_value(param_name)
                    test_values.append(hex_value)
                else:
                    # Use the raw hex value entered
                    test_values.append(self.byte_entries[i].get())
            
            # In a real app, you would send the CAN message here
            # For demo purposes, we'll just show a message box
            messagebox.showinfo("CAN Test Transmit", 
                            f"Message with ID {can_id} and {dlc} bytes would be transmitted:\n"
                            f"Hex: {' '.join(test_values)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test transmit: {str(e)}")

    def get_simulated_param_value(self, param_name):
        """Generate a simulated value for a given parameter"""
        if param_name not in self.bms_parameters:
            return "00"
            
        param = self.bms_parameters[param_name]
        
        # Generate a plausible value based on parameter type
        if param_name == "SOC":
            value = random.randint(0, 100)
        elif param_name == "SOH":
            value = random.randint(70, 100)
        elif param_name == "Current":
            value = random.randint(-500, 500)  # -50A to 50A with scale 0.1
        elif param_name == "Voltage":
            value = random.randint(3000, 4200)  # 300V to 420V with scale 0.1
        elif param_name == "Power":
            value = random.randint(-10000, 20000)  # -100kW to 200kW with scale 0.01
        elif param_name == "Status":
            value = random.randint(0, 5)
        elif param_name == "Flags":
            value = random.randint(0, 3)
        elif "Cell_V" in param_name:
            value = random.randint(3000, 4200)  # 3.0V to 4.2V with scale 0.001
        elif "Temp" in param_name and not param_name.endswith("ID"):
            value = random.randint(15, 45)  # 15°C to 45°C
        elif "ID" in param_name:
            value = random.randint(1, 16)  # Sensor/cell ID
        elif "Bal" in param_name:
            value = random.randint(0, 1)
        elif "Cell_" in param_name:
            value = random.randint(3000, 4200)  # 3.0V to 4.2V with scale 0.001
        else:
            value = 0
        
        # Convert to appropriate hex representation based on type
        if param["type"] == "uint8" or param["type"] == "int8":
            return f"{value & 0xFF:02X}"
        elif param["type"] == "uint16" or param["type"] == "int16":
            # For 16-bit values, we'd actually need two bytes
            # This is just a simple representation for testing
            return f"{value & 0xFF:02X}"
        else:
            return "00"

    def clear_can_form(self):
        self.can_msg_id_entry.delete(0, tk.END)
        self.can_msg_id_entry.insert(0, "0x100")
        
        self.msg_type_var.set("Standard")
        self.dlc_var.set("8")
        self.rtr_var.set(False)
        
        self.msg_name_entry.delete(0, tk.END)
        self.msg_name_entry.insert(0, "New_Message")
        
        self.periodic_var.set(True)
        self.period_entry.delete(0, tk.END)
        self.period_entry.insert(0, "1000")
        
        # Reset data bytes and parameters
        self.update_data_bytes_frame()

    def edit_can_message(self):
        try:
            selected_index = self.msg_listbox.curselection()[0]
            message = self.msg_listbox.get(selected_index)
            
            # Parse the message
            # Example format: "0x680 [8] BMS_Status (1000ms): SOC|Highest_Cell_V|Lowest_Cell_V|Avg_Cell_V|High_Temp|Low_Temp|Status|Flags"
            parts = message.split()
            
            # Extract CAN ID, DLC, and name
            can_id = parts[0]
            dlc = parts[1].strip('[]')
            name_end = message.find("(")
            name = message[message.find("]")+1:name_end].strip()
            
            # Extract period if it exists
            if "(on-demand)" in message:
                periodic = False
                period = ""
            else:
                periodic = True
                period_start = message.find("(") + 1
                period_end = message.find("ms)")
                period = message[period_start:period_end]
            
            # Extract data bytes or parameter names
            data_start = message.find(":") + 1
            data_bytes = message[data_start:].strip().split("|")
            
            # Update the form with the parsed values
            self.can_msg_id_entry.delete(0, tk.END)
            self.can_msg_id_entry.insert(0, can_id)
            
            self.dlc_var.set(dlc)
            
            self.msg_name_entry.delete(0, tk.END)
            self.msg_name_entry.insert(0, name)
            
            self.periodic_var.set(periodic)
            self.period_entry.delete(0, tk.END)
            self.period_entry.insert(0, period)
            
            # Update data bytes frame for the new DLC
            self.update_data_bytes_frame()
            
            # Update the parameter selections and values
            for i, byte_val in enumerate(data_bytes):
                if i < len(self.byte_param_vars):
                    # Check if this is a parameter name or hex value
                    if byte_val in self.bms_parameters:
                        # It's a parameter name
                        self.byte_param_vars[i].set(byte_val)
                        self.byte_entries[i].config(state="disabled")
                        self.byte_entries[i].delete(0, tk.END)
                        self.byte_entries[i].insert(0, "--")
                        # Update description
                        self.byte_param_combos[i].desc_label.config(text=self.bms_parameters[byte_val]["description"])
                    else:
                        # It's a hex value
                        self.byte_param_vars[i].set("")
                        self.byte_entries[i].config(state="normal")
                        self.byte_entries[i].delete(0, tk.END)
                        self.byte_entries[i].insert(0, byte_val)
            
            # Delete the old message
            self.msg_listbox.delete(selected_index)
            
        except IndexError:
            messagebox.showerror("Selection Error", "Please select a message to edit.")
        except Exception as e:
            messagebox.showerror("Error", f"Error editing message: {str(e)}")

    def add_custom_parameter(self):
        """Add a custom parameter to the BMS parameters list"""
        try:
            # Create a dialog to get parameter details
            dialog = CustomParameterDialog(self.root, self.bms_parameters.keys())
            if dialog.result:
                param_name, description, param_type, unit, scale = dialog.result
                
                # Add to parameters dictionary
                self.bms_parameters[param_name] = {
                    "description": description,
                    "type": param_type,
                    "unit": unit,
                    "scale": float(scale)
                }
                
                # Refresh the parameter mapping tab
                parent = self.notebook.winfo_children()[2]  # Parameter mapping tab
                self.setup_parameter_mapping_tab(parent)
                
                # Update the comboboxes in the message config tab
                for combo in self.byte_param_combos:
                    current_val = combo.get()
                    param_names = [""] + sorted([name for name in self.bms_parameters.keys() if name])
                    combo['values'] = param_names
                    combo.set(current_val)  # Restore current selection
                    
                messagebox.showinfo("Success", f"Parameter '{param_name}' has been added.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add parameter: {str(e)}")

    def generate_cell_parameters(self):
        """Generate parameters for all cells and temperature sensors based on configuration"""
        try:
            # Get the number of cells and temperature sensors from the configuration
            num_cells = int(self.total_cells_entry.get()) if hasattr(self, 'total_cells_entry') else 140
            num_temps = int(self.temp_sensors_entry.get()) * int(self.num_slaves_entry.get()) if hasattr(self, 'temp_sensors_entry') and hasattr(self, 'num_slaves_entry') else 120
            
            # Generate cell voltage parameters
            for i in range(1, num_cells + 1):
                param_name = f"Cell_{i}"
                if param_name not in self.bms_parameters:
                    self.bms_parameters[param_name] = {
                        "description": f"Cell {i} Voltage (V)",
                        "type": "uint16",
                        "unit": "V",
                        "scale": 0.001
                    }
            
            # Generate temperature sensor parameters
            for i in range(1, num_temps + 1):
                param_name = f"Temp_{i}"
                if param_name not in self.bms_parameters:
                    self.bms_parameters[param_name] = {
                        "description": f"Temperature Sensor {i} (°C)",
                        "type": "int8",
                        "unit": "°C",
                        "scale": 1
                    }
            
            # Refresh the parameter mapping tab
            parent = self.notebook.winfo_children()[2]  # Parameter mapping tab
            self.setup_parameter_mapping_tab(parent)
            
            # Update the comboboxes in the message config tab
            for combo in self.byte_param_combos:
                current_val = combo.get()
                param_names = [""] + sorted([name for name in self.bms_parameters.keys() if name])
                combo['values'] = param_names
                combo.set(current_val)  # Restore current selection
                
            messagebox.showinfo("Success", f"Generated parameters for {num_cells} cells and {num_temps} temperature sensors.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate parameters: {str(e)}")

    def delete_can_message(self):
        try:
            selected_index = self.msg_listbox.curselection()[0]
            self.msg_listbox.delete(selected_index)
        except IndexError:
            messagebox.showerror("Selection Error", "Please select a message to delete.")

    def export_can_messages(self):
        messages = [self.msg_listbox.get(i) for i in range(self.msg_listbox.size())]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                # Parse messages into a structured format
                structured_messages = []
                
                for message in messages:
                    # Parse the message
                    parts = message.split()
                    can_id = parts[0]
                    dlc = parts[1].strip('[]')
                    
                    name_end = message.find("(")
                    name = message[message.find("]")+1:name_end].strip()
                    
                    # Extract period if it exists
                    if "(on-demand)" in message:
                        periodic = False
                        period = 0
                    else:
                        periodic = True
                        period_start = message.find("(") + 1
                        period_end = message.find("ms)")
                        period = int(message[period_start:period_end])
                    
                    # Extract data bytes or parameter names
                    data_start = message.find(":") + 1
                    data_bytes = message[data_start:].strip().split("|")
                    
                    # Create structured message
                    msg_data = {
                        "id": can_id,
                        "dlc": int(dlc),
                        "name": name,
                        "periodic": periodic,
                        "period_ms": period,
                        "data_bytes": data_bytes
                    }
                    
                    structured_messages.append(msg_data)
                
                # Export as JSON
                with open(file_path, 'w') as file:
                    json.dump(structured_messages, file, indent=2)
                    
                messagebox.showinfo("Export Successful", f"Exported {len(messages)} messages to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting messages: {str(e)}")

    def import_can_messages(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    messages = json.load(file)
                
                # Clear existing messages
                self.msg_listbox.delete(0, tk.END)
                
                # Add imported messages
                for msg in messages:
                    can_id = msg["id"]
                    dlc = msg["dlc"]
                    name = msg["name"]
                    
                    # Format period
                    if msg["periodic"]:
                        period_text = f"({msg['period_ms']}ms)"
                    else:
                        period_text = "(on-demand)"
                    
                    # Format data bytes
                    data_str = "|".join(msg["data_bytes"])
                    
                    # Create message string
                    message = f"{can_id} [{dlc}] {name} {period_text}: {data_str}"
                    
                    # Add to listbox
                    self.msg_listbox.insert(tk.END, message)
                
                messagebox.showinfo("Import Successful", f"Imported {len(messages)} messages from {file_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing messages: {str(e)}")
 
    def create_profile_entries(self, profile_name):
        """Create entry fields for a specific temperature profile"""
        # Clear existing entries in the frame
        for widget in self.ocv_entries_frame.winfo_children()[2:]:  # Skip the headers
            widget.destroy()
        
        # Create entries for SOC-OCV pairs
        soc_entries = []
        ocv_entries = []
        
        # Get the data for this profile
        profile_data = self.temp_profiles[profile_name]
        soc_values = profile_data["soc"]
        ocv_values = profile_data["ocv"]
        
        for i, (soc, ocv) in enumerate(zip(soc_values, ocv_values)):
            # SOC entry
            soc_entry = ttk.Entry(self.ocv_entries_frame, width=10)
            soc_entry.grid(row=i+1, column=0, padx=5, pady=3)
            soc_entry.insert(0, str(soc))
            soc_entries.append(soc_entry)
            
            # OCV entry
            ocv_entry = ttk.Entry(self.ocv_entries_frame, width=10)
            ocv_entry.grid(row=i+1, column=1, padx=5, pady=3)
            ocv_entry.insert(0, str(ocv))
            ocv_entries.append(ocv_entry)
        
        # Store the entries in the profile dictionary
        self.profile_entries[profile_name] = {
            "soc": soc_entries,
            "ocv": ocv_entries
        }

    def on_profile_select(self, event):
        """Handle selection of a different temperature profile"""
        try:
            # Save current profile data
            self.save_current_profile_data()
            
            # Get selected profile
            selection = self.profile_listbox.curselection()
            if selection:
                profile_name = self.profile_listbox.get(selection[0])
                self.current_profile = profile_name
                
                # Update the entries with the selected profile data
                self.create_profile_entries(profile_name)
                
                # Update the graph
                self.generate_ocv_graph()
        except Exception as e:
            messagebox.showerror("Profile Selection Error", f"Error changing profiles: {str(e)}")

    def save_current_profile_data(self):
        """Save the current entries to the profile data"""
        try:
            if self.current_profile in self.profile_entries:
                entries = self.profile_entries[self.current_profile]
                soc_values = [float(entry.get()) for entry in entries["soc"] if entry.get()]
                ocv_values = [float(entry.get()) for entry in entries["ocv"] if entry.get()]
                
                # Update the profile data
                self.temp_profiles[self.current_profile] = {
                    "soc": soc_values,
                    "ocv": ocv_values
                }
        except ValueError as e:
            messagebox.showerror("Invalid Value", "Please ensure all entries contain valid numbers.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving profile data: {str(e)}")

    def add_temp_profile(self):
        """Add a new temperature profile"""
        # Ask for the temperature value
        temp = simpledialog.askstring("New Temperature Profile", 
                                    "Enter temperature value (with unit, e.g., 15°C):")
        if temp:
            if temp in self.temp_profiles:
                messagebox.showerror("Duplicate Profile", f"A profile for {temp} already exists.")
                return
            
            # Save current profile data
            self.save_current_profile_data()
            
            # Create a new profile with default data
            self.temp_profiles[temp] = {"soc": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
                                    "ocv": [3.0, 3.2, 3.3, 3.35, 3.4, 3.5, 3.6, 3.7, 3.9, 4.1, 4.2]}
            
            # Add to listbox
            self.profile_listbox.insert(tk.END, temp)
            
            # Select the new profile
            self.profile_listbox.select_clear(0, tk.END)
            self.profile_listbox.select_set(tk.END)
            self.current_profile = temp
            
            # Create entries for the new profile
            self.create_profile_entries(temp)
            
            # Update the graph
            self.generate_ocv_graph()

    def rename_temp_profile(self):
        """Rename the selected temperature profile"""
        try:
            # Get selected profile
            selection = self.profile_listbox.curselection()
            if not selection:
                messagebox.showerror("Selection Error", "Please select a profile to rename.")
                return
            
            old_name = self.profile_listbox.get(selection[0])
            
            # Ask for the new name
            new_name = simpledialog.askstring("Rename Temperature Profile", 
                                            f"Enter new name for {old_name}:")
            
            if new_name and new_name != old_name:
                if new_name in self.temp_profiles:
                    messagebox.showerror("Duplicate Profile", f"A profile named {new_name} already exists.")
                    return
                
                # Save current profile data
                self.save_current_profile_data()
                
                # Update profile data dictionary
                self.temp_profiles[new_name] = self.temp_profiles.pop(old_name)
                
                # Update profile entries dictionary
                if old_name in self.profile_entries:
                    self.profile_entries[new_name] = self.profile_entries.pop(old_name)
                
                # Update current profile name if needed
                if self.current_profile == old_name:
                    self.current_profile = new_name
                
                # Update listbox
                self.profile_listbox.delete(selection[0])
                self.profile_listbox.insert(selection[0], new_name)
                self.profile_listbox.select_set(selection[0])
                
                # Update graph
                self.generate_ocv_graph()
        except Exception as e:
            messagebox.showerror("Rename Error", f"Error renaming profile: {str(e)}")

    def delete_temp_profile(self):
        """Delete the selected temperature profile"""
        try:
            # Get selected profile
            selection = self.profile_listbox.curselection()
            if not selection:
                messagebox.showerror("Selection Error", "Please select a profile to delete.")
                return
            
            # Don't allow deleting the last profile
            if self.profile_listbox.size() <= 1:
                messagebox.showerror("Delete Error", "Cannot delete the last profile.")
                return
            
            profile_name = self.profile_listbox.get(selection[0])
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Delete", 
                                        f"Are you sure you want to delete the {profile_name} profile?")
            
            if confirm:
                # Remove from dictionaries
                if profile_name in self.temp_profiles:
                    del self.temp_profiles[profile_name]
                
                if profile_name in self.profile_entries:
                    del self.profile_entries[profile_name]
                
                # Remove from listbox
                self.profile_listbox.delete(selection[0])
                
                # Select another profile
                if self.profile_listbox.size() > 0:
                    self.profile_listbox.select_set(0)
                    self.current_profile = self.profile_listbox.get(0)
                    self.create_profile_entries(self.current_profile)
                
                # Update graph
                self.generate_ocv_graph()
        except Exception as e:
            messagebox.showerror("Delete Error", f"Error deleting profile: {str(e)}")

    def clone_temp_profile(self):
        """Clone the selected temperature profile"""
        try:
            # Get selected profile
            selection = self.profile_listbox.curselection()
            if not selection:
                messagebox.showerror("Selection Error", "Please select a profile to clone.")
                return
            
            source_name = self.profile_listbox.get(selection[0])
            
            # Ask for the new name
            new_name = simpledialog.askstring("Clone Temperature Profile", 
                                            f"Enter name for the clone of {source_name}:")
            
            if new_name:
                if new_name in self.temp_profiles:
                    messagebox.showerror("Duplicate Profile", f"A profile named {new_name} already exists.")
                    return
                
                # Save current profile data
                self.save_current_profile_data()
                
                # Clone the profile data
                self.temp_profiles[new_name] = {
                    "soc": self.temp_profiles[source_name]["soc"].copy(),
                    "ocv": self.temp_profiles[source_name]["ocv"].copy()
                }
                
                # Add to listbox
                self.profile_listbox.insert(tk.END, new_name)
                
                # Select the new profile
                self.profile_listbox.select_clear(0, tk.END)
                self.profile_listbox.select_set(tk.END)
                self.current_profile = new_name
                
                # Create entries for the new profile
                self.create_profile_entries(new_name)
                
                # Update the graph
                self.generate_ocv_graph()
        except Exception as e:
            messagebox.showerror("Clone Error", f"Error cloning profile: {str(e)}")

    def generate_ocv_graph(self):
        # Save current profile data first
        self.save_current_profile_data()
        
        try:
            # Clear previous plot
            self.ax.clear()
            
            # Determine if we show all curves or just the current one
            if self.show_all_curves_var.get():
                # Plot all temperature profiles
                colors = plt.cm.tab10(np.linspace(0, 1, len(self.temp_profiles)))
                legend_entries = []
                
                for i, (temp, data) in enumerate(self.temp_profiles.items()):
                    soc_values = data["soc"]
                    ocv_values = data["ocv"]
                    
                    # Sort the data by SOC
                    soc_ocv_pairs = sorted(zip(soc_values, ocv_values), key=lambda pair: pair[0])
                    soc_values = [pair[0] for pair in soc_ocv_pairs]
                    ocv_values = [pair[1] for pair in soc_ocv_pairs]
                    
                    # Plot with a unique color
                    line, = self.ax.plot(soc_values, ocv_values, '-o', 
                                        linewidth=2, markersize=4, 
                                        label=temp, color=colors[i])
                    
                    # Highlight the current profile with a thicker line
                    if temp == self.current_profile:
                        line.set_linewidth(3)
                        line.set_markersize(6)
                    
                    legend_entries.append(line)
                
                # Add a legend
                self.ax.legend(handles=legend_entries, loc='best')
                
                # Update the graph info label
                self.graph_info.config(text="Showing all temperature profiles")
                
            else:
                # Plot only the current profile
                data = self.temp_profiles[self.current_profile]
                soc_values = data["soc"]
                ocv_values = data["ocv"]
                
                # Sort the data by SOC
                soc_ocv_pairs = sorted(zip(soc_values, ocv_values), key=lambda pair: pair[0])
                soc_values = [pair[0] for pair in soc_ocv_pairs]
                ocv_values = [pair[1] for pair in soc_ocv_pairs]
                
                # Create the plot with a blue line
                self.ax.plot(soc_values, ocv_values, 'b-o', linewidth=2, markersize=6)
                
                # Update the graph info label
                self.graph_info.config(text=f"Showing profile: {self.current_profile}")
            
            # Set graph labels and properties
            self.ax.set_xlabel('State of Charge (%)')
            self.ax.set_ylabel('Open Circuit Voltage (V)')
            self.ax.set_title('OCV vs. SOC Relationship by Temperature')
            self.ax.grid(True)
            self.ax.set_xlim(0, 100)
            
            # Get all OCV values for y-axis limits
            all_ocv = []
            for data in self.temp_profiles.values():
                all_ocv.extend(data["ocv"])
            
            min_v = min(all_ocv) * 0.98 if all_ocv else 2.8
            max_v = max(all_ocv) * 1.02 if all_ocv else 4.2
            self.ax.set_ylim(min_v, max_v)
            
            # Update the canvas
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Graph Error", f"Error generating graph: {str(e)}")

    def add_ocv_point(self):
        """Add a new point to the current OCV profile"""
        # Save current profile data first
        self.save_current_profile_data()
        
        try:
            # Add a new row for SOC-OCV entry
            if self.current_profile in self.profile_entries:
                entries = self.profile_entries[self.current_profile]
                row_count = len(entries["soc"])
                
                # Create new entries at the end
                soc_entry = ttk.Entry(self.ocv_entries_frame, width=10)
                soc_entry.grid(row=row_count+1, column=0, padx=5, pady=3)
                
                ocv_entry = ttk.Entry(self.ocv_entries_frame, width=10)
                ocv_entry.grid(row=row_count+1, column=1, padx=5, pady=3)
                
                # Add to the entries list
                entries["soc"].append(soc_entry)
                entries["ocv"].append(ocv_entry)
                
                # Update the profile data with placeholder values
                soc_values = self.temp_profiles[self.current_profile]["soc"]
                ocv_values = self.temp_profiles[self.current_profile]["ocv"]
                
                # Suggest a new SOC value
                if soc_values:
                    new_soc = min(100, max(soc_values) + 10)
                else:
                    new_soc = 0
                    
                # Suggest a new OCV value
                if ocv_values:
                    new_ocv = ocv_values[-1] + 0.1
                else:
                    new_ocv = 3.0
                    
                soc_entry.insert(0, str(new_soc))
                ocv_entry.insert(0, str(new_ocv))
                
        except Exception as e:
            messagebox.showerror("Add Point Error", f"Error adding point: {str(e)}")

    def remove_ocv_point(self):
        """Remove the last point from the current OCV profile"""
        # Save current profile data
        self.save_current_profile_data()
        
        try:
            if self.current_profile in self.profile_entries:
                entries = self.profile_entries[self.current_profile]
                
                # Keep at least 2 points
                if len(entries["soc"]) > 2:
                    # Remove the last entry
                    last_soc_entry = entries["soc"].pop()
                    last_ocv_entry = entries["ocv"].pop()
                    
                    # Destroy the widgets
                    last_soc_entry.destroy()
                    last_ocv_entry.destroy()
                    
                    # Update the profile data
                    self.save_current_profile_data()
                    
                    # Regenerate the graph
                    self.generate_ocv_graph()
                else:
                    messagebox.showinfo("Info", "Need at least 2 data points for the OCV curve.")
        except Exception as e:
            messagebox.showerror("Remove Point Error", f"Error removing point: {str(e)}")

    def export_all_ocv_maps(self):
        """Export all temperature profiles to a file"""
        try:
            # Save current profile data first
            self.save_current_profile_data()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            if file_path:
                import json
                
                # Create a serializable version of the data
                export_data = {}
                for temp, data in self.temp_profiles.items():
                    export_data[temp] = data
                
                with open(file_path, 'w') as file:
                    json.dump(export_data, file, indent=4)
                    
                messagebox.showinfo("Export Successful", 
                                f"Exported {len(self.temp_profiles)} temperature profiles to {file_path}")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting OCV maps: {str(e)}")

    def export_current_ocv_map(self):
        """Export only the current temperature profile to a CSV file"""
        try:
            # Save current profile data
            self.save_current_profile_data()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if file_path:
                data = self.temp_profiles[self.current_profile]
                soc_values = data["soc"]
                ocv_values = data["ocv"]
                
                with open(file_path, 'w') as file:
                    file.write(f"# Temperature: {self.current_profile}\n")
                    file.write("SOC,OCV\n")
                    for soc, ocv in zip(soc_values, ocv_values):
                        file.write(f"{soc},{ocv}\n")
                        
                messagebox.showinfo("Export Successful", 
                                f"Exported {self.current_profile} profile to {file_path}")
                    
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting OCV map: {str(e)}")

    def import_ocv_maps(self):
        """Import temperature profiles from a JSON file"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if not file_path:
                return
                
            # Check file extension
            if file_path.lower().endswith('.json'):
                self.import_json_profiles(file_path)
            elif file_path.lower().endswith('.csv'):
                self.import_csv_profile(file_path)
            else:
                messagebox.showerror("Import Error", "Unsupported file format. Please use JSON or CSV files.")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing OCV maps: {str(e)}")

    def import_json_profiles(self, file_path):
        """Import multiple temperature profiles from a JSON file"""
        try:
            import json
            
            with open(file_path, 'r') as file:
                imported_data = json.load(file)
            
            if not imported_data:
                messagebox.showerror("Import Error", "No valid data found in the file.")
                return
                
            # Ask if we should replace or merge with existing profiles
            if self.temp_profiles:
                response = messagebox.askyesnocancel(
                    "Import Options", 
                    "Do you want to replace all existing profiles?\n"
                    "Yes = Replace all existing profiles\n"
                    "No = Merge with existing profiles\n"
                    "Cancel = Abort import"
                )
                
                if response is None:  # Cancel
                    return
                    
                if response:  # Yes - Replace all
                    self.temp_profiles.clear()
                    self.profile_entries.clear()
                    self.profile_listbox.delete(0, tk.END)
            
            # Import the profiles
            for temp, data in imported_data.items():
                self.temp_profiles[temp] = data
                self.profile_listbox.insert(tk.END, temp)
            
            # Select the first profile if none are selected
            if not self.profile_listbox.curselection() and self.profile_listbox.size() > 0:
                self.profile_listbox.select_set(0)
                self.current_profile = self.profile_listbox.get(0)
                
            # Create entries for the current profile
            if self.current_profile in self.temp_profiles:
                self.create_profile_entries(self.current_profile)
                
            # Update the graph
            self.generate_ocv_graph()
            
            messagebox.showinfo("Import Successful", 
                            f"Imported {len(imported_data)} temperature profiles from {file_path}")
                    
        except Exception as e:
            messagebox.showerror("JSON Import Error", f"Error importing profiles: {str(e)}")

    def import_csv_profile(self, file_path):
        """Import a single temperature profile from a CSV file"""
        try:
            # Read the CSV file
            import csv
            
            # Ask for profile name
            temp_name = None
            soc_values = []
            ocv_values = []
            
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
                # Check if first line has the temperature information
                if lines and lines[0].startswith('# Temperature:'):
                    temp_name = lines[0].replace('# Temperature:', '').strip()
                    lines = lines[1:]  # Skip this line
                
                # If no temp name found, ask user
                if not temp_name:
                    temp_name = simpledialog.askstring("Temperature Profile", 
                                                    "Enter name for the temperature profile:")
                    if not temp_name:
                        return
                
                # Process the remaining lines as CSV
                csv_reader = csv.reader(lines)
                header_skipped = False
                
                for row in csv_reader:
                    if not header_skipped:  # Skip header row
                        header_skipped = True
                        continue
                        
                    if len(row) >= 2:
                        try:
                            soc = float(row[0])
                            ocv = float(row[1])
                            soc_values.append(soc)
                            ocv_values.append(ocv)
                        except ValueError:
                            continue  # Skip rows with non-numeric values
            
            if not soc_values or not ocv_values:
                messagebox.showerror("Import Error", "No valid SOC-OCV data found in the CSV file.")
                return
                
            # Check if profile already exists
            if temp_name in self.temp_profiles:
                replace = messagebox.askyesno("Profile Exists", 
                                            f"A profile named '{temp_name}' already exists. Replace it?")
                if not replace:
                    temp_name = simpledialog.askstring("New Profile Name", 
                                                    "Enter a new name for the imported profile:")
                    if not temp_name or temp_name in self.temp_profiles:
                        return
            
            # Add the new profile
            self.temp_profiles[temp_name] = {
                "soc": soc_values,
                "ocv": ocv_values
            }
            
            # Add to listbox if not already present
            if temp_name not in [self.profile_listbox.get(i) for i in range(self.profile_listbox.size())]:
                self.profile_listbox.insert(tk.END, temp_name)
            
            # Select the new profile
            for i in range(self.profile_listbox.size()):
                if self.profile_listbox.get(i) == temp_name:
                    self.profile_listbox.select_clear(0, tk.END)
                    self.profile_listbox.select_set(i)
                    self.current_profile = temp_name
                    break
            
            # Create entries for the new profile
            self.create_profile_entries(temp_name)
            
            # Update the graph
            self.generate_ocv_graph()
            
            messagebox.showinfo("Import Successful", 
                            f"Imported profile '{temp_name}' from {file_path}")
                    
        except Exception as e:
            messagebox.showerror("CSV Import Error", f"Error importing profile: {str(e)}")
    
    def refresh_data(self):
        # In a real application, this would fetch data from your BMS
        # For demo purposes, we'll generate random data
        
        # Update voltage values
        for entry in self.voltage_entries:
            entry.config(state='normal')
            voltage = random.uniform(3.1, 4.1)
            entry.delete(0, tk.END)
            entry.insert(0, f"{voltage:.3f}V")
            
            # Color based on voltage level (visual indication)
            if voltage > 4.0:
                entry.config(bg="#ffcccc")  # Light red for high voltage
            elif voltage < 3.3:
                entry.config(bg="#ffffcc")  # Light yellow for low voltage
            else:
                entry.config(bg="#e6ffe6")  # Light green for normal
                
            entry.config(state='readonly')
        
        # Update temperature values
        for entry in self.temp_entries:
            entry.config(state='normal')
            temp = random.uniform(15, 45)
            entry.delete(0, tk.END)
            entry.insert(0, f"{temp:.1f}°C")
            
            # Color based on temperature level
            if temp > 40:
                entry.config(bg="#ffcccc")  # Light red for high temp
            elif temp < 20:
                entry.config(bg="#ccccff")  # Light blue for low temp
            else:
                entry.config(bg="#e6ffe6")  # Light green for normal
                
            entry.config(state='readonly')
    
    def save_config(self):
        # In a real application, this would save to the BMS
        # For demo purposes, just print to console
        config = {
            "cells_in_series_per_slave": self.cells_series_entry.get(),
            "cells_in_parallel": self.cells_parallel_entry.get(),
            "number_of_slaves": self.num_slaves_entry.get(),
            "total_cells": self.total_cells_entry.get(),
            "temp_sensors_per_slave": self.temp_sensors_entry.get(),
            "multiplexed_temp_sensors": self.multiplexed_var.get(),
            "multiplexing_pin": self.mux_pin_entry.get() if self.multiplexed_var.get() else "N/A",
            "overvoltage": self.overvoltage_entry.get(),
            "undervoltage": self.undervoltage_entry.get(),
            "overtemp": self.overtemp_entry.get(),
            "undertemp": self.undertemp_entry.get(),
            "balance_threshold": self.balance_threshold_entry.get(),
            "balance_start": self.balance_start_entry.get(),
            "balance_enabled": self.balance_enable_var.get(),
            "can_id": self.can_id_entry.get(),
            "update_rate": self.update_rate_entry.get()
        }
        
        print("Saved configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # Show confirmation message
        messagebox.showinfo("Configuration Saved", 
                         "BMS configuration has been updated successfully.")

class CustomParameterDialog:
    def __init__(self, parent, existing_params):
        self.result = None
        self.existing_params = existing_params
        
        # Create the dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add Custom Parameter")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Parameter name
        ttk.Label(self.dialog, text="Parameter Name:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(self.dialog, width=20)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Description
        ttk.Label(self.dialog, text="Description:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.desc_entry = ttk.Entry(self.dialog, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky=tk.W)
        
        # Parameter type
        ttk.Label(self.dialog, text="Data Type:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.type_var = tk.StringVar(value="uint8")
        type_combo = ttk.Combobox(self.dialog, textvariable=self.type_var, 
                                 values=["uint8", "int8", "uint16", "int16"], width=10)
        type_combo.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Unit
        ttk.Label(self.dialog, text="Unit:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.unit_entry = ttk.Entry(self.dialog, width=10)
        self.unit_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Scale factor
        ttk.Label(self.dialog, text="Scale Factor:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.scale_entry = ttk.Entry(self.dialog, width=10)
        self.scale_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        self.scale_entry.insert(0, "1")
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Add Parameter", command=self.on_add).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", command=self.on_cancel).pack(side=tk.LEFT, padx=10)
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Wait for the dialog to close
        self.dialog.wait_window()
    
    def on_add(self):
        param_name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        param_type = self.type_var.get()
        unit = self.unit_entry.get().strip()
        scale = self.scale_entry.get().strip()
        
        # Validate input
        if not param_name:
            messagebox.showerror("Input Error", "Parameter name cannot be empty.", parent=self.dialog)
            return
            
        if param_name in self.existing_params:
            messagebox.showerror("Input Error", f"Parameter '{param_name}' already exists.", parent=self.dialog)
            return
            
        if not description:
            messagebox.showerror("Input Error", "Description cannot be empty.", parent=self.dialog)
            return
        
        try:
            scale_value = float(scale)
            if scale_value <= 0:
                raise ValueError("Scale factor must be positive")
        except ValueError:
            messagebox.showerror("Input Error", "Scale factor must be a positive number.", parent=self.dialog)
            return
        
        # Store the result
        self.result = (param_name, description, param_type, unit, scale)
        
        # Close the dialog
        self.dialog.destroy()
    
    def on_cancel(self):
        self.dialog.destroy()



if __name__ == "__main__":
    root = tk.Tk()
    app = BMSMonitorApp(root)
    root.mainloop()