import math
import time
import timeit
import numpy as np
import cv2
from lib import grab_screen
import torch
from termcolor import colored
from win32api import GetSystemMetrics
from lib.assistant import activate_aim, activate_recoil

# Load Model
print(colored(".....Loading AI Model......", "yellow"))
model =  torch.hub.load('ultralytics/yolov5', 'custom', path='lib/models/best.pt', force_reload=True)

vision_width = 500 # 500
vision_heigth = 280 # 280

def check_input_device(input_device):
    if input_device == 1:
        return "Mouse"
    elif input_device == 2:
        return "Controller"
    else:
        input_device = "Mouse"
        return "Error! use Default: Mouse"

def run_detection(show_window, aim_assist, inpt_device):
    inpt_device = check_input_device(input_device=inpt_device)
    print(colored("Input Device: ", "blue"), inpt_device)

    W = GetSystemMetrics(0)
    H = GetSystemMetrics(1)

    # calculate StartPoint for Draw Line
    start_point = int(vision_width / 2), int(vision_heigth / 2)

# Calculate the Range for Detection Window
    vision_window_size = (int(W/2 - vision_width / 2),
                        int(H/2 - vision_heigth / 2),
                        int(W/2 + vision_width / 2),
                        int(H/2 + vision_heigth / 2))

    print(colored("[OKAY] Starting Screen Capture..", "yellow"))

    while (True):

        start_time = timeit.default_timer()
        # grab screen capture
        img_screen = np.array(grab_screen.grab(vision_window_size))
        
        # Detection
        result = model(img_screen)
        img_screen = np.squeeze(result.render())
        targets_detected = result.xyxy[0].tolist()
        
        nearest_points = []
        
        # check if any object detected
        if len(targets_detected) > 0:
            for xmin, ymin, xmax, ymax, confidence, classid in targets_detected:
                #Classid: 15 = Operator, 16 = Head
                if confidence < 0.7 and classid == 15 or confidence > 0.71 and classid == 16:
                    cx, cy = check_classid(xmin,ymin, xmax,ymax, classid)
                    nearest_points = get_detected_points(cx,cy)
                    
            # get nearest point of detection
        if len(nearest_points) > 0:
            xpos, ypos = get_nearest_point(cx,cy, nearest_points)
            cv2.line(img_screen, (xpos, ypos), (start_point), (244, 242, 113), 2)
            mouse_x = int((xpos - (vision_width / 2)) * 3)
            mouse_y = int((ypos - (vision_heigth / 2)) * 3)
            activate_aim(is_aim=aim_assist, inpt_device=inpt_device, tx=mouse_x, ty=mouse_y)
        activate_recoil()

        if show_window == True:
            # Calc and Print FPS
            cv2.putText(img_screen, f"FPS: {int(1/(time.perf_counter() - start_time))}",
                    (3, 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (113, 116, 244), 1)
            cv2.imshow('Lime Computer Vision', img_screen)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break

def check_classid(xmin, ymin, xmax, ymax, classid):
    if classid == 15: # Operator
        heigth_boxes_calculation = 0.8
    elif classid == 16: # Head
        heigth_boxes_calculation = 0.1

    cx = int((xmin+xmax) / 2)
    cy = int((ymin+ymax - (ymax - ymin) * heigth_boxes_calculation) / 2)
    return cx,cy

def get_detected_points(cx,cy):
    detected_points = []
    crosshair_dist = int(math.dist((cx, cy), (vision_width, vision_heigth)))
    detected_points.append((cx,cy, crosshair_dist))
    return detected_points

def get_nearest_point(cx,cy, detected_boxes):
    if len(detected_boxes) > 0:
        detected_boxes = sorted(detected_boxes, key=lambda x: x[2])
        cx, cy = int(detected_boxes[0][0]), int(detected_boxes[0][1])
        return cx, cy
       