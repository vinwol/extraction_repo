# This code is based on:
# https://answers.opencv.org/question/134248/how-to-define-the-lower-and-upper-range-of-a-color/?answer=134284#post-id-134284

import cv2
import numpy as np
import sys

image_hsv = None
pixel = (20,60,80) 

# mouse callback function
def pick_color(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_hsv[y,x]
        #you might want to adjust the ranges(+-10, etc):
        upper =  np.array([pixel[0] + 10, pixel[1] + 10, pixel[2] + 40])
        lower =  np.array([pixel[0] - 10, pixel[1] - 10, pixel[2] - 40])
        print(pixel, lower, upper)
        image_mask = cv2.inRange(image_hsv,lower,upper)
        cv2.imshow("mask",image_mask)

def main():
    global image_hsv, pixel # so we can use it in mouse callback
    image_src = cv2.imread('./figure_2a.png')
    if image_src is None:
        print ("The image read is None............")
        return
    cv2.imshow("bgr",image_src)
    cv2.namedWindow('hsv')
    cv2.setMouseCallback('hsv', pick_color)
    image_hsv = cv2.cvtColor(image_src,cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv",image_hsv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()
    
