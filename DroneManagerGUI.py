import dearpygui.dearpygui as dpg
from DroneManager import DroneManager  # Adjust this import as necessary
import time
import sys

drone_manager = DroneManager()

SSID = "Bebop2-394373"

def connect_callback():
    dpg.set_value("connection_status", "Connecting...")

    if sys.platform == 'linux':
        success = drone_manager.connect_wifi_linux(SSID)
    elif sys.platform.startswith('win'):
        success = drone_manager.connect_wifi_windows(SSID)
    else:
        success = False
        dpg.set_value("connection_status", "Unknown OS: Can't connect WiFi.")

    time.sleep(0.5)
    if success == False:
        dpg.configure_item("connection_status", color=[255, 0, 0], default_value="Cannot connect to WiFi.")
        return
    time.sleep(1)  # Wait for the drone to connect

    connected = drone_manager.connect()
    if connected:
        dpg.configure_item("connection_status", color=[0, 255, 0], default_value="Connected")
    else:
        dpg.set_value("connection_status", "Failed to connect to drone")

def start_stream_callback():
    dpg.set_value("stream_status", "Starting Stream...")
    drone_manager.start_video_stream()
    dpg.configure_item("stream_status", color=[0, 255, 0], default_value="Streaming")

def update_sensors_callback():
    drone_manager.update_sensor_data()
    sensor_data_str = "\n".join(f"{key}: {value}" for key, value in drone_manager.sensor_data.items())
    dpg.set_value("sensor_data_text", sensor_data_str)

def stop_callback():
    drone_manager.stop()
    dpg.configure_item("connection_status", color=[255, 0, 0], default_value="Disconnected")
    dpg.configure_item("stream_status", color=[255, 0, 0], default_value="Stream Stopped")

def angle_camera_callback():
    tilt = dpg.get_value("camera_tilt")
    pan = dpg.get_value("camera_pan")
    drone_manager.angle_camera(tilt, pan)

def exit_callback():
    dpg.destroy_context()

dpg.create_context()
dpg.set_global_font_scale(2)

with dpg.window(label="Drone Manager", width=1200, height=800):
    dpg.add_text("Drone Status:")
    # Initially set the color of these items to red
    dpg.add_text("Not Connected", tag="connection_status", color=[255, 0, 0])
    dpg.add_text("Stream Stopped", tag="stream_status", color=[255, 0, 0])
    dpg.add_button(label="Connect to Drone", callback=connect_callback)
    dpg.add_button(label="Start Video Stream", callback=start_stream_callback)
    dpg.add_slider_float(label="camera_tilt", default_value=0, max_value=20, min_value=-90, tag="camera_tilt", callback=angle_camera_callback)
    dpg.add_slider_float(label="camera_pan", default_value=0, max_value=35, min_value=-35, tag="camera_pan", callback=angle_camera_callback)
    dpg.add_button(label="Update Sensor Data", callback=update_sensors_callback)
    dpg.add_button(label="Stop and Disconnect", callback=stop_callback)
    dpg.add_button(label="Exit", callback=exit_callback)
    dpg.add_text("Sensordata -->", tag="sensor_data_text")

dpg.create_viewport(title='Drone Manager GUI', width=1200, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
