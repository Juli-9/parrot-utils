from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
from pyparrot.Model import Model
import subprocess
import time
import psutil

class DroneManager:
    def __init__(self):
        self.bebop = Bebop()
        self.sensor_data = {}
        self.vision = None
        self.ffplay_process = None
        self.running = False

    def connect(self):
        """
        Connect to the Bebop drone.
        """
        success = self.bebop.connect(5)
        if success:
            print("Successfully connected to Bebop.")
        else:
            print("Failed to connect to Bebop.")
        return success

    def connect_wifi(self, ssid, password=None):
        """
        Connect to the drone's WiFi network on Windows.

        :param ssid: The SSID of the WiFi network.
        :param password: The password for the WiFi network, if any.
        """
        try:
            if password:
                cmd = f"netsh wlan connect name={ssid} ssid={ssid} key={password}"
            else:
                cmd = f"netsh wlan connect name={ssid} ssid={ssid}"

            result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(f"Successfully connected to {ssid}")
            else:
                print(f"Failed to connect to {ssid}: {result.stderr.decode('utf-8')}")
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to {ssid}: {e}")

    def start_video_stream(self):
        """
        Start the video stream using ffplay in a separate process.
        """
        if self.connect():
            self.vision = DroneVision(self.bebop, Model.BEBOP)
            self.bebop.start_video_stream()
            ffplay_cmd = "ffplay -fflags nobuffer -flags low_delay -protocol_whitelist file,rtp,udp -i pyparrot/utils/bebop.sdp"
            self.ffplay_process = subprocess.Popen(ffplay_cmd, shell=True)
            print("Vision successfully started!")
            self.running = True

    def print_sensor_data(self):
        """
        Print sensor data in a readable format. Call this method in your main loop.
        """
        if self.running:
            sensors = self.bebop.sensors.sensors_dict
            print("Sensor Data:")
            for key, value in sensors.items():
                label = key.replace("Changed_", " ").replace("_", " ")
                print(f"{label}: {value}")
            print("-" * 20)  # Separator for readability

    def stop(self):
        """
        Stop the video stream and disconnect.
        """
        if self.vision:
            print("Stopping vision and disconnecting.")
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'ffplay.exe':
                    proc.terminate()
                    break  # Assuming you want to terminate the first found instance
            if self.ffplay_process:
                self.ffplay_process.terminate()
            self.vision.close_video()
            self.bebop.stop_video_stream()
            self.bebop.disconnect()
            self.running = False

    def update_sensor_data(self):
        """
        Fetches the latest sensor data from the drone and updates the sensor_data dictionary.
        """
        current_sensors = self.bebop.sensors.sensors_dict
        for key, value in current_sensors.items():
            # Process or transform the sensor data if necessary
            self.sensor_data[key] = value

    def angle_camera(self, angle):
        """
        Adjust the camera angle of the drone.

        :param angle: The angle to set the camera to.
        """
        self.bebop.pan_tilt_camera(angle, 0)

if __name__ == "__main__":
    manager = DroneManager()

    try:
        # Start the video stream
        manager.start_video_stream()
        
        # Main loop
        while manager.running:
            time.sleep(0.1)  # Sleep to prevent excessive CPU usage
            manager.update_sensor_data()

    except KeyboardInterrupt:
        print("Interrupted by user, stopping...")
        manager.stop()
