import serial
import datetime
import csv
import re

# Configure the serial port
ser = serial.Serial(
    port='COM3',
    baudrate=115200,
    timeout=6 # in seconds
)

def read_serial():
    starttime = datetime.datetime.now()
    formatted_time = starttime.strftime("%Y_%b_%d")
    filename = formatted_time+'_hot_slump_thermocouple.csv'

    #print a division in the csv with headers
    with open(filename, mode='a', newline='') as file: # Mode 'a' is append
        writer = csv.writer(file)
        writer.writerow(['Computer Log Time', 'Thermocouple ID','Cold Junction Temp (C)','Thermocouple Temp (C)'])

    while True:
        if ser.in_waiting > 0:
            # Read a line of serial input, and strip trailing white space
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Received:{line}")

            # Format the line of serial input
            pattern = r"(\w+):(\d+(?:\.\d+)?)" # Expecting "tc_id:5, Cold_Junction_Temp:23.70, Thermocouple_Temp:39.18"
            matches = re.findall(pattern,line)
            if len(matches) == 3:
                thermocouple_id = matches[0][1]
                cold_junction_temp = float(matches[1][1])
                thermocouple_temp = float(matches[2][1])
                timestamp = datetime.datetime.now()
                log = [timestamp,thermocouple_id,cold_junction_temp,thermocouple_temp]
            else:
                log = line

            # Write formatted data to a csv file
            with open(filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(log)
            print(f"Data appended to:{filename}.")

try:
    print("Starting serial monitor. Press Ctrl+C to stop.")
    read_serial()
except KeyboardInterrupt:
    print("Stopping serial monitor.")
finally:
    ser.close()
