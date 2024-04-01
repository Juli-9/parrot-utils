from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
from pyparrot.Model import Model
import cv2
import time
import os
import subprocess  # Import subprocess module

running = True

# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)

if success:
    # start up the video
    bebopVision = DroneVision(bebop, Model.BEBOP)
    bebopVision.drone_object.start_video_stream()
    
    if success:
        print("Vision successfully started!")
    

        try:
            # Play the video stream using ffplay (requires ffplay to be installed on your system)
            # Use subprocess.Popen to run ffplay without blocking
            ffplay_cmd = "ffplay -fflags nobuffer -flags low_delay -protocol_whitelist file,rtp,udp -i pyparrot/utils/bebop.sdp"
            ffplay_process = subprocess.Popen(ffplay_cmd, shell=True)

            # Keep the program running until interrupted by the user
            while running:
                time.sleep(0.1)  # Sleep to prevent excessive CPU usage

        except KeyboardInterrupt:
            # User interrupted the program (Ctrl+C)
            print("Stopping...")
            running = False

        finally:
            # Clean up resources properly
            print("Finishing demo and stopping vision")
            bebopVision.close_video()

        # disconnect nicely so we don't need a reboot
        bebop.disconnect()

    else:
        print("Failed to start vision")
else:
    print("Error connecting to bebop. Retry")
