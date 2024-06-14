import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Serial port configuration
serial_port = 'COM3'
baud_rate = 115200

# Initialize serial port
ser = serial.Serial(serial_port, baud_rate, timeout=1)
ser.flush()

# Initialize temperature array
temps = np.zeros(768)
max_temp = 0
min_temp = 500

# Create the figure for plotting
fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((24, 32)), cmap='hsv', vmin=160, vmax=360)
plt.colorbar(heatmap)

def read_serial_data():
    global max_temp, min_temp
    if ser.in_waiting > 5000:
        line = ser.read_until(b'\r')
        if len(line) > 4608:
            line = line[:4608]
        split_string = line.decode().strip().split(',')

        # Update min and max temperatures
        max_temp = 0
        min_temp = 500

        for q in range(768):
            try:
                value = float(split_string[q])
                if value > max_temp:
                    max_temp = value
                if value < min_temp:
                    min_temp = value
            except (ValueError, IndexError):
                pass
        
        # Map temperatures to colors
        for q in range(768):
            try:
                value = float(split_string[q])
                mapped_value = np.clip(np.interp(value, [min_temp, max_temp], [180, 360]), 160, 360)
                temps[q] = mapped_value
            except (ValueError, IndexError):
                temps[q] = 0

def update_heatmap(*args):
    read_serial_data()
    heatmap.set_array(temps.reshape((24, 32)))
    return heatmap,

ani = animation.FuncAnimation(fig, update_heatmap, interval=100)

plt.show()
