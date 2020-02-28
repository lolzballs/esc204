import math
import numpy as np
import cv2 as cv
import imutils
from statistics import mean 
from shapedetector import ShapeDetector
from picamera import PiCamera
from time import sleep

# Set up RBP camera
camera = PiCamera()
camera.rotation = 180
camera.resolution = (2592, 1944)

# Capture image with RBP camera
sleep(5)
camera.capture('/home/jon_pi/Desktop/esc204/vision/align_w_port/test.jpg')

# Read image with OpenCV
image = cv.imread('test.jpg')

# Define bounds on blue colour segmentation
blue = ([95,65,0], [165,180,10])

# Perform colour segmentation
(lower, upper) = blue
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")
mask = cv.inRange(image, lower, upper)
output = cv.bitwise_and(image, image, mask = mask)

'''new = cv.resize(output, (int(2592/3),int(1944/3)))
cv.imshow("Blue only", new)
cv.waitKey(0)'''

# Convert colour segmented image to grayscale
gray = cv.cvtColor(output, cv.COLOR_BGR2GRAY)

# blurred = cv.GaussianBlur(gray, (5, 5), 0)

# Convert image again to black and white only 
thresh = cv.threshold(gray, 60, 255, cv.THRESH_BINARY)[1]

'''new = cv.resize(thresh, (int(2592/3),int(1944/3)))
cv.imshow("Threshold", new)
cv.waitKey(0)'''

# Detect shapes in image
cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
	cv.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sd = ShapeDetector()

# Empty list to collect data points of detected rectangles
data = []

# Loop through detected shapes
for c in cnts:
    M = cv.moments(c)
    cX = int((M["m10"] / (M["m00"] + 1e-7)))
    cY = int((M["m01"] / (M["m00"] + 1e-7)))
    shape = sd.detect(c)
    # Only add shape to list if it is a large rectangle
    if (shape == "rectangle") and (len(c) > 20):
        data.append(c)
        c = c.astype("int")
        cv.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv.putText(image, shape, (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

'''new = cv.resize(image, (int(2592/3),int(1944/3)))
cv.imshow("Image", new)
cv.waitKey(0)'''

# Check if more than two rectangles are detected
if len(data) > 2:
    print('warning')

# Empty list to collect post-processed data
data_in_list = []

# Collect x coordinates from first rectangle
for i in data[0]:
    data_in_list.append(i[0][0])

# Collect x coordinates from second rectangle
for j in data[1]:
    data_in_list.append(j[0][0])

# Sort x coordinates from largest to smallest
data_in_list.sort()

# Function to find x position of outermost edges of rectangles
def outer_positions(nums):
    x1 = mean(nums[0:10])
    x2 = mean(nums[len(nums)-10:])
    return([x1,x2])

# Find x position of outermost edges
positions = outer_positions(data_in_list)

# Determine what movement is required
def move(a,b):
    tolerance = 20
    left = a
    right = 2592 - b
    print(left,right)
    test = left - right
    if test > tolerance:
        return('move right')
    elif test < -tolerance:
        return('move left')
    else:
        return('ok!')

# Print movement for humans to see
print(move(positions[0],positions[1]))

# Display image of detected rectangles
new = cv.resize(image, (int(2592/3),int(1944/3)))
cv.imshow("Let's find some rectangles", new)
cv.waitKey(0)
