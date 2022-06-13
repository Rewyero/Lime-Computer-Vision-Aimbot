import math
import time
import timeit
from cv2 import sort
import numpy as np
import cv2
from lib import grab_screen
from termcolor import colored
from win32api import GetSystemMetrics
from lib.assistant import activate_aim

file_path = "lib\models\cascade\haarcascade_frontalface_default.xml"

faces_cascade = cv2.CascadeClassifier(file_path)    

def run_detection(rangeWidth, rangeheight, show_window, aim_assist, inpt_device):

    print(colored("Input Device: ", "blue"), inpt_device)

    W = GetSystemMetrics(0)
    H = GetSystemMetrics(1)

    centerScreenX, centerScreenY = (rangeWidth / 2), (rangeheight / 2)

    # calculate StartPoint for Draw Line
    start_point = int(centerScreenX), int(centerScreenY)

# Calculate the Range for Detection Window
    vision_window_size = (int(W/2 - rangeWidth/2),
                          int(H/2 - rangeheight/2),
                          int(W/2 + rangeWidth/2),
                          int(H/2 + rangeheight/2))

    print(colored("[OKAY] Starting Screen Capture..", "yellow"))

    while (True):
        start_time = timeit.default_timer()
        # grab screen capture
        frame = np.array(grab_screen.grab(region=vision_window_size))
        #frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)

        # Calc and Print FPS
        cv2.putText(frame, f"FPS: {int(1/(time.perf_counter() - start_time))}",
                    (3, 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (113, 116, 244), 1)

        # Detection
        faces = faces_cascade.detectMultiScale(frame)  # scaleFactor=1.0,
        # minNeighbors=5,
        # minSize=(30, 30))
        #print("Found {0} faces!".format(len(faces)))

        detectedFaces = []
        nearest_points = []

        for x1, y1, width, height in faces:

            cv2.rectangle(frame, (x1, y1), (x1 + width, y1 + height),
                          color=(255, 0, 0), thickness=2)
            x, y = int(x1 + width / 2), int(y1 + height / 2)

            cv2.circle(frame, (x, y), 3, (50, 150, 255), -1)

            # Calculate Distance to the Target from Middle of Screen
            crosshair_dist = int(
                math.dist((x, y), (centerScreenX, centerScreenY)))
            detectedFaces.append((x,y, crosshair_dist, x1 + x, y1 + y)) # x1 + x, y1 + y

        nearest_points = sorted(detectedFaces, key=lambda x: x[2]) # Find nearest position of target

        if len(detectedFaces) >= 1:
            xpos, ypos = int(nearest_points[0][0]), int(nearest_points[0][1])
            cv2.line(frame, (xpos, ypos), (start_point), (244, 242, 113), 2)

        # Recoil Activation
        #assistant.activate_recoil(aim_assist, inpt_device)

        # Check is Nearest Point Found
        if len(nearest_points) > 0:
            xpos = int(W/2 - nearest_points[0][2]) #* -1
            ypos = int(H/2- nearest_points[0][3]) #* -1
            print("detection pos: ", xpos,ypos)
            activate_aim(is_aim=aim_assist, inpt_device=inpt_device, tx=xpos, ty=ypos, screenwidth=vision_window_size[0], screenheight=vision_window_size[1])

        if show_window == True:
            cv2.imshow('Lime Computer Vision', frame)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
