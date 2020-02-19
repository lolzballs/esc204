import math
import numpy as np
import cv2 as cv
import imutils
from statistics import mean 
from shapedetector import ShapeDetector

image = cv.imread('l3.jpg')
ratio = 1

blue = ([95,65,0], [165,180,40])

(lower, upper) = blue
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")
mask = cv.inRange(image, lower, upper)
output = cv.bitwise_and(image, image, mask = mask)

'''new = cv.resize(output, (int(2592/3),int(1944/3)))
cv.imshow("Blue only", new)
cv.waitKey(0)'''

gray = cv.cvtColor(output, cv.COLOR_BGR2GRAY)
blurred = cv.GaussianBlur(gray, (5, 5), 0)
thresh = cv.threshold(gray, 60, 255, cv.THRESH_BINARY)[1]

'''new = cv.resize(thresh, (int(2592/3),int(1944/3)))
cv.imshow("Threshold", new)
cv.waitKey(0)'''

cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL,
	cv.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
sd = ShapeDetector()

# loop over the contours
for c in cnts:
    # compute the center of the contour, then detect the name of the
    # shape using only the contour
    M = cv.moments(c)
    cX = int((M["m10"] / (M["m00"] + 1e-7)) * ratio)
    cY = int((M["m01"] / (M["m00"] + 1e-7)) * ratio)
    shape = sd.detect(c)
    # multiply the contour (x, y)-coordinates by the resize ratio,
    # then draw the contours and the name of the shape on the image
    # c = c.astype("float")
    c *= ratio
    c = c.astype("int")
    cv.drawContours(image, [c], -1, (0, 255, 0), 2)
    cv.putText(image, shape, (cX, cY), cv.FONT_HERSHEY_SIMPLEX,
        0.5, (255, 255, 255), 2)
    # show the output image

new = cv.resize(image, (int(2592/3),int(1944/3)))
cv.imshow("Image", new)
cv.waitKey(0)

'''dst = cv.Canny(output, 100, 200)
    
cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)

lines = cv.HoughLines(dst, 1, np.pi / 180, 100, None, 0, 0)

data = []

if lines is not None:
    for i in range(0, len(lines)):
        rho = lines[i][0][0]
        theta = lines[i][0][1]
        a = math.cos(theta)
        b = math.sin(theta)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        angle = abs(np.arctan2(pt1[1] - pt2[1], pt1[0] - pt2[0]) * 180. / np.pi)
        
        if ((angle > 80) and (angle < 100)):
            data.append(pt1)
            data.append(pt2)
            cv.line(cdstP, pt1, pt2, (0,0,255), 3, cv.LINE_AA)

data_final = []

for i in range(0,len(data),2):
    temp = (data[i][0] + data[i+1][0])/2
    data_final.append(temp)

data_final.sort()

def get_xvals(sorted_list):
    avg_vals = []
    acc = []
    for i in range (1,len(sorted_list)):
        test_a = sorted_list[i-1]
        test_b = sorted_list[i]

        test = test_a/test_b

        acc.append(test_a)
        if test < 0.98:
            temp = mean(acc)
            avg_vals.append(temp)
            acc = []
        if i == (len(sorted_list)-1):
            acc.append(test_b)
            temp = mean(acc)
            avg_vals.append(temp)
            acc = []

    for i in avg_vals:
        x1 = avg_vals[0]
        x2 = avg_vals[3]

    if len(avg_vals) != 4:
        return(-1)
    
    return([x1, x2])

positions = get_xvals(data_final)

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

print(positions)
print(move(positions[0],positions[1]))

new = cv.resize(cdstP, (int(2592/3),int(1944/3)))
cv.imshow("Detected Lines", new)
cv.waitKey(0)'''

#sm_image = cv.resize(image, (320,180))
#sm_output = cv.resize(output, (320,180))
#cv.imshow("images", np.hstack([sm_image, sm_output]))
#cv.waitKey(0)
