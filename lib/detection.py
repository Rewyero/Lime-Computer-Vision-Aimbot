import math
import multiprocessing
import time
import timeit
import numpy as np
import cv2
import grab_screen
import torch
from termcolor import colored
from win32api import GetSystemMetrics
from assistant import activate_aim, activate_recoil

aim_assist = True # Aim Assist Enable = True || Disabled = False
show_window = False # Show Computer Vision Window (True)
input_device = 1 # (1  Mouse/Keyboard) ( 2 Controller)

vision_width = 400 # 500
vision_heigth = 300 # 280

aim_speed = 4

def GRAB_SCREEN(q):
    # Calculate the Range for Detection Window
    vision_window_size = (int(GetSystemMetrics(0)/2 - vision_width / 2),
                        int(GetSystemMetrics(1)/2 - vision_heigth / 2),
                        int(GetSystemMetrics(0)/2 + vision_width / 2),
                        int(GetSystemMetrics(1)/2 + vision_heigth / 2))

    while True:
        img_screen = np.array(grab_screen.grab(vision_window_size))
        q.put(img_screen)
        q.join()
        activate_recoil()

def run_detection(q):

    print(colored(".....Loading AI Model......", "yellow"))
    model = torch.hub.load('ultralytics/yolov5', 'custom', path='lib/models/mw_warzone.pt', force_reload=True)

    print(colored("[OKAY] Starting Screen Capture..", "yellow"))
    

    while True:
        if not q.empty():

            # grab screen capture
            img_screen = q.get()
            q.task_done()

            # Detection
            result = model(img_screen)
            img_screen =  np.squeeze(result.render())
            targets_detected = result.xyxy[0].tolist()
            detected_points = []
            # check if any object detected
            if len(targets_detected) > 0:
                for xmin, ymin, xmax, ymax, confidance, classid in targets_detected:
                    #Classid: 15 = Operator, 16 = Head
                    if confidance > 0.5 and classid == 16:
                        cx, cy = head_pos_calculation(xmin, ymin, xmax, ymax, classid)
                        crosshair_dist = int(math.dist((cx, cy), (vision_width / 2, vision_heigth / 2)))
                        detected_points.append((cx,cy, crosshair_dist))
                        
                # get nearest point of detection
            if len(detected_points) > 0:
                xpos, ypos = get_nearest_point(cx,cy, detected_points)
                cv2.line(img_screen, (xpos, ypos), (int(vision_width / 2), int(vision_heigth / 2)), (244, 242, 113), 2)
                mouse_x = int((xpos - (vision_width / 2)) * aim_speed)
                mouse_y = int((ypos - (vision_heigth / 2)) * aim_speed)
                activate_aim(is_aim=aim_assist, inpt_device="Mouse", tx=mouse_x, ty=mouse_y)
            q.put(img_screen)
            q.join()
            
def SHOW_SCREEN_WINDOW(q):
    global fps, start_time
    while True:
        if not q.empty():
            start_time = timeit.default_timer()
            img = q.get()
            q.task_done()
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Calc and Print FPS
            cv2.putText(img, f"FPS: {int(1/(time.perf_counter() - start_time))}",
                    (3, 20), cv2.FONT_HERSHEY_DUPLEX, 0.5, (200, 00, 255), 1)
            if show_window:
                cv2.imshow("Lime Computer Vision", img)
        
        if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break

def head_pos_calculation(xmin, ymin, xmax, ymax, classid):

    if classid == 15: # Operator
        heigth_boxes_calculation = 0.6
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


if __name__ == "__main__":
    q = multiprocessing.JoinableQueue()
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

    
    p1 = multiprocessing.Process(target=GRAB_SCREEN, args=(q, ))
    p2 = multiprocessing.Process(target=SHOW_SCREEN_WINDOW, args=(q, ))
    p3 = multiprocessing.Process(target=run_detection, args=(q, ))
    p1.start()
    p2.start()
    p3.start()