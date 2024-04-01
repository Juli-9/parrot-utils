from pyparrot.Bebop import Bebop
from pyparrot.DroneVision import DroneVision
from pyparrot.Model import Model
import cv2
import time
import os

running = True

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        img = self.vision.get_latest_valid_picture()

        if (img is not None):
            filename = "test_image_%06d.png" % self.index
            cv2.imwrite(filename, img)
            self.index += 1

# make my bebop object
bebop = Bebop()

# connect to the bebop
success = bebop.connect(5)

if success:
    # start up the video
    bebopVision = DroneVision(bebop, Model.BEBOP)
    userVision = UserVision(bebopVision)
    bebopVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    #success = bebopVision.open_video()
    success = True
    bebopVision._start_video_buffering()
    
    if success:
        print("Vision successfully started!")
    

        try:
            # Play the video stream using ffplay (requires ffplay to be installed on your system)
            os.system("ffplay -fflags nobuffer -flags low_delay -protocol_whitelist file,rtp,udp -i pyparrot/utils/bebop.sdp")
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
