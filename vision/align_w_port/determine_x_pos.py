import math
import numpy as np
import cv2 as cv
import imutils
from statistics import mean 
from shapedetector import ShapeDetector
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180

sleep(2)
camera.capture('/home/jon_pi/Desktop/esc204/vison/align_w_port/test.jpg')

image = cv.imread('test.jpg')

blue = ([95,65,0], [165,180,10])

(lower, upper) = blue
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")
mask = cv.inRange(image, lower, upper)
output = cv.bitwise_and(image, image, mask = mask)

'''new = cv.resize(output, (int(2592/3),int(1944/3)))
cv.imshow("Blue only", new)
cv.waitKey(0)'''

gray = cv.cvtColor(output, cv.COLOR_BGR2GRAY)
# blurred = cv.GaussianBlur(gray, (5, 5), 0)
thresh = cv.threshold(gray, 60, 255, cv.THRESH_BINARY)[1]

'''new = cv.resize(thresh, (int(2592/3),int(1944/3)))
cv.imshow("Threshold", new)
cv.waitKey(0)'''

cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
	cv.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sd = ShapeDetector()

data = []

for c in cnts:
    M = cv.moments(c)
    cX = int((M["m10"] / (M["m00"] + 1e-7)))
    cY = int((M["m01"] / (M["m00"] + 1e-7)))
    shape = sd.detect(c)
    if (shape == "rectangle") and (len(c) > 20):
        data.append(c)
        c = c.astype("int")
        cv.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv.putText(image, shape, (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

'''new = cv.resize(image, (int(2592/3),int(1944/3)))
cv.imshow("Image", new)
cv.waitKey(0)'''

if len(data) > 2:
    print('warning')

data_in_list = []

for i in data[0]:
    data_in_list.append(i[0][0])

for j in data[1]:
    data_in_list.append(j[0][0])

data_in_list.sort()

def outer_positions(nums):
    x1 = mean(nums[0:10])
    x2 = mean(nums[len(nums)-10:])
    return([x1,x2])

positions = outer_positions(data_in_list)

def move(a,b):
    tolerance = 5
    left = a
    right = 2592 - b
    test = left - right
    if test > tolerance:
        return('move left')
    if test < -tolerance:
        return('move right')
    else:
        return('ok!')

print(move(positions[0],positions[1]))

new = cv.resize(image, (int(2592/3),int(1944/3)))
cv.imshow("Let's find some rectangles", new)
cv.waitKey(0)