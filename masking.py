import cv2
import argparse
from operator import xor
from app import getValues
import os

def callback(value):
    pass


def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)
    cv2.setWindowProperty("Trackbars",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_NORMAL)
    print('seetin')
    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)

def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values


def main(imgPath, filter = 'HSV'):

    range_filter = filter

    if imgPath:
        image = cv2.imread(imgPath)
        # print('image', image, imgPath)
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        camera = cv2.VideoCapture(0)

    while True:
        
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(range_filter)
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))


        if cv2.waitKey(1) & 0xFF is ord('q'):
            break
        
        (flag, encodedImage) = cv2.imencode(".jpg", thresh)

        if not flag:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')


def convertMask(imgPath):
    if imgPath:
        image = cv2.imread(imgPath)
        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        print('Image Path Not Provided')

    v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values('HSV')
    thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

    dest_path = os.path.join('./static/masked_images', 'masked_'+(os.path.basename(imgPath)))
    cv2.imwrite(dest_path, thresh)

    return dest_path