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
model =  torch.hub.load('ultralytics/yolov5', 'custom', path='lib/models/best.pt')

vision_width = 450 # 500
vision_heigth = 350 # 280

aim_speed = 1


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

# Calculate the Range for Detection Window
    vision_window_size = (int(GetSystemMetrics(0)/2 - vision_width / 2),
                        int(GetSystemMetrics(1)/2 - vision_heigth / 2),
                        int(GetSystemMetrics(0)/2 + vision_width / 2),
                        int(GetSystemMetrics(1)/2 + vision_heigth / 2))

    print(colored("[OKAY] Starting Screen Capture..", "yellow"))

    while (True):

        start_time = timeit.default_timer()
        # grab screen capture
        img_screen = np.array(grab_screen.grab(vision_window_size))
        
        # Detection
        result = model(img_screen)
        img_screen =  np.squeeze(result.render())
        targets_detected = result.xyxy[0].tolist()
        detected_points = []
        # check if any object detected
        if len(targets_detected) > 0:
            for xmin, ymin, xmax, ymax, confidance, classid in targets_detected:
                #Classid: 15 = Operator, 16 = Head
                if confidance > 0.6 and classid == 16:
                    cx, cy = head_pos_calculation(xmin, ymin, xmax, ymax, classid)
                    crosshair_dist = int(math.dist((cx, cy), (vision_width / 2, vision_heigth / 2)))
                    detected_points.append((cx,cy, crosshair_dist))
                    
            # get nearest point of detection
        if len(detected_points) > 0:
            xpos, ypos = get_nearest_point(cx,cy, detected_points)
            cv2.line(img_screen, (xpos, ypos), (int(vision_width / 2), int(vision_heigth / 2)), (244, 242, 113), 2)
            mouse_x = int((xpos - (vision_width / 2)) * aim_speed)
            mouse_y = int((ypos - (vision_heigth / 2)) * aim_speed)
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

def head_pos_calculation(xmin, ymin, xmax, ymax, classid):

    if classid == 15: # Operator
        heigth_boxes_calculation = 0.8
    elif classid == 16: # Head
        heigth_boxes_calculation = 0.1

    cx = int((xmin+xmax) / 2)
    cy = int((ymin+ymax - (ymax - ymin) * heigth_boxes_calculation) / 2)
    return cx,cy

def get_nearest_point(cx,cy, detected_boxes):
    if len(detected_boxes) > 0:
        detected_boxes = sorted(detected_boxes, key=lambda x: x[2])
        cx, cy = int(detected_boxes[0][0]), int(detected_boxes[0][1])
        return cx, cy
       