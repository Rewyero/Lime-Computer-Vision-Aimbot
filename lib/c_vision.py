
#import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import math

detector = hub.load("https://tfhub.dev/tensorflow/centernet/resnet50v1_fpn_512x512/1")
size_scale = 3
print("[INFO] Starting Tensorflow..")

def detection_obj(frame):
    image = np.expand_dims(frame, 0)
    img_w, img_h = image.shape[2], image.shape[1]
    # Detection
    result = detector(frame)
    result = {key:value.numpy() for key,value in result.items()}
    boxes = result['detection_boxes'][0]
    scores = result['detection_scores'][0]
    classes = result['detection_classes'][0]

    # Check every detected object
    detected_boxes = []
    for i, box in enumerate(boxes):
        # Choose only person(class:1)
        if classes[i] == 1 and scores[i] >= 0.5:
            ymin, xmin, ymax, xmax = tuple(box)
            if ymin > 0.5 and ymax > 0.8: # CS:Go
            #if int(xmin * img_w * 3) < 450: # Fortnite
                continue
            left, right, top, bottom = int(xmin * img_w), int(xmax * img_w), int(ymin * img_h), int(ymax * img_h)
            detected_boxes.append((left, right, top, bottom))
            #cv2.rectangle(ori_img, (left, top), (right, bottom), (255, 255, 0), 2)

    print("Detected:", len(detected_boxes))

    # Check Closest
    if len(detected_boxes) >= 1:
        min = 99999
        at = 0
        centers = []
        for i, box in enumerate(detected_boxes):
            x1, x2, y1, y2 = box
            c_x = ((x2 - x1) / 2) + x1
            c_y = ((y2 - y1) / 2) + y1
            centers.append((c_x, c_y))
            dist = math.sqrt(math.pow(img_w/2 - c_x, 2) + math.pow(img_h/2 - c_y, 2))
            if dist < min:
                min = dist
                at = i

        # Pixel difference between crosshair(center) and the closest object
        x = centers[at][0] - img_w/2
        y = centers[at][1] - img_h/2 - (detected_boxes[at][3] - detected_boxes[at][2]) * 0.45

        # Move mouse and shoot
        #scale = 1.7 * size_scale
        #x = int(x * scale)
        #y = int(y * scale)
        #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)