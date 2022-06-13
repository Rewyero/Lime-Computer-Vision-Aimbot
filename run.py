# AUTOR: Rewyero
import torch
from lib import detection
from termcolor import colored

print(''' 
======================================
--------LIME COMPUTER VISION----------
======================================
''')
if torch.cuda.is_available():  
    print(colored("CUDA is Available: " + torch.cuda.get_device_name(0), "green"))
else:
    print(colored("CUDA is not Available, Use CPU Only", "red"))

print("-------------------------------")

cv_width = 800 # Computer Vision window width
cv_height = 600 # Computer Vision window height
aim_assist = True # Aim Assist Enable = True || Disabled = False
computerVision_show_window = True # Show Computer Vision Window (True)
input_device = '1' # ("1" Mouse/Keyboard) ("2" Controller)

# Start Screen Capture
detection.run_detection(
cv_width,cv_height,
computerVision_show_window, 
aim_assist, 
input_device)