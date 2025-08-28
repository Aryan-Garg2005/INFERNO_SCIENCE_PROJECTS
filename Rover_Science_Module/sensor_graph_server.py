import serial
import socket
import csv
import ast

ser = serial.Serial('COM3', 9600)

# Set up a server socket
server_ip = '0.0.0.0'  # Listen on all available interfaces
server_port = 8885
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(1)

print(f"Waiting for a connection on {server_ip}:{server_port}...")

while True:
    try:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Create a CSV file for saving sensor data
        csv_file_path = 'sensor_data_server.csv'
        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Temp(c)', 'Humidity','UV_V', 'MQ7', 'pH','Ozone Concentration','MQ4','Soil Temperature','Soil Moisture'])

            while True:
                try:
                    line = ser.readline().decode(errors='ignore')
                except Exception as e:
                    print(f"Error reading from serial port: {e}")
                    continue

                if "Saving:" in line:
                    try:
                        data_tuple = ast.literal_eval(line.split("Saving:")[1].strip())
                        client_socket.send(str(data_tuple).encode())  # Sending as a string to the client

                        # Print and save received sensor readings
                        print("\nReceived sensor readings:")
                        print(data_tuple)
                        csv_writer.writerow(data_tuple)  # Writing the tuple to CSV
                        csvfile.flush()

                    except (ValueError, SyntaxError) as e:
                        print(f"Invalid tuple data received: {line}")
                        continue

    except Exception as e:
        print(f"Error accepting connection: {e}")
        continue
