import socket
import ast
import csv
import math
import matplotlib.pyplot as plt

def read_sensor_data(sock, csv_writer, sensor_names, sensor_units, x_values, y_values, axs):
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 
              'tab:brown', 'tab:pink', 'tab:gray', 'tab:cyan']  # Predefined colors
    markers = ['o', 's', 'D', '^', 'v', '<', '>', 'P', 'X']  # Predefined markers

    while True:
        try:
            line = sock.recv(1024).decode(errors='ignore')
            if not line:
                print("Connection closed by the server.")
                break
        except Exception as e:
            print(f"Error reading from remote PC: {e}")
            break

        try:
            data_tuple = ast.literal_eval(line.strip())
        except (ValueError, SyntaxError):
            print(f"Invalid tuple data received: {line}")
            # Log the error
            with open('error_log.txt', 'a') as error_file:
                error_file.write(f"Invalid data: {line}\n")
            continue

        print("\nReceived sensor readings:")
        print(data_tuple)

        # Write to CSV file
        csv_writer.writerow(data_tuple)
        csvfile.flush()

        # Plot sensor values
        sensor_data = dict(zip(sensor_names, data_tuple))
        for i, sensor_name in enumerate(sensor_names):
            x_values[i].append(len(x_values[i]))
            sensor_value = sensor_data[sensor_name]

            # Skip if the sensor value is None or invalid
            if sensor_value is None:
                continue

            y_values[i].append(sensor_value)

            axs[i].cla()  # Clear axis for updated plot
            axs[i].plot(
                x_values[i],
                y_values[i],
                label=f"{sensor_name}",
                color=colors[i % len(colors)],  # Cycle through colors
                linewidth=1,  # Thinner line
                marker=markers[i % len(markers)],  # Cycle through markers
                markersize=3
            )

            # Add grid, labels, and unit annotations
            axs[i].grid(True, linestyle='--', alpha=0.6)
            axs[i].set_title(sensor_name, fontsize=12, weight='bold')
            axs[i].set_xlabel("Sample", fontsize=10)  # X-axis label remains 'Sample'
            axs[i].set_ylabel(f"{sensor_name} ({sensor_units[i]})", fontsize=10)  # Y-axis shows sensor name and unit
            axs[i].legend(fontsize=8, loc='upper right')

            # Dynamic y-limits with bounds to reduce jitter
            if len(y_values[i]) > 1:
                axs[i].set_ylim(
                    max(min(y_values[i]) - 1, 0),  # Ensure y-limit doesn't go below 0
                    max(y_values[i]) + 1
                )

        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust layout to fit title
        plt.draw()
        plt.pause(0.01)

if __name__ == "__main__":
    try:
        remote_pc_ip = "localhost"
        # remote_pc_ip = "192.168.1.56"
        remote_pc_port = 8885

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((remote_pc_ip, remote_pc_port))

        csv_file_path = 'sensor_data.csv'
        with open(csv_file_path, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Temp(c)', 'Humidity', 'UV_V', 'MQ7', 'pH','Ozone Concentration','MQ4', 'Soil Temperature', 'Soil Moisture'])

            plt.ion()

            # Dynamically adjust rows/columns based on number of sensors
            num_sensors = 9  # Adjust this dynamically if needed
            columns = 3
            rows = math.ceil(num_sensors / columns)

            fig, axs = plt.subplots(rows, columns, figsize=(14, 16))
            fig.suptitle('Real-Time Sensor Data Monitoring', fontsize=18, weight='bold')

            # Flatten axs for dynamic sensor count handling
            axs = axs.flatten()

            sensor_names = [
                'Temp(c)',
                'Humidity',
                'UV_V',
                'MQ7',
                'pH',
                'Ozone Concentration',
                'MQ4',
                'Soil Temperature',
                'Soil Moisture'
            ]

            sensor_units = [
                'Celsius',
                '%',         # Humidity in percentage
                'Volts',
                'ppm',
                '',
                'ppm',
                'ppm',
                'Celsius',
                '%',         # Soil Moisture in percentage
            ]

            x_values = [[] for _ in range(len(sensor_names))]
            y_values = [[] for _ in range(len(sensor_names))]

            read_sensor_data(sock, csv_writer, sensor_names, sensor_units, x_values, y_values, axs)
    except KeyboardInterrupt:
        print("Exiting program...")
        sock.close()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
