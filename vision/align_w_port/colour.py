import math
import numpy as np
import cv2 as cv
from statistics import mean 

image = cv.imread('l1.jpg')

blue = ([100,70,0], [160,130,40])

(lower, upper) = blue
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")
mask = cv.inRange(image, lower, upper)
output = cv.bitwise_and(image, image, mask = mask)

dst = cv.Canny(output, 100, 200)
    
cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)

linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 20, None, 5, 5)

data = np.empty([0,4], int)

if linesP is not None:
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        angle = np.arctan2(l[2] - l[0], l[3] - l[1]) * 180. / np.pi
        length = l[1] - l[3]
        if ((angle > 170) and (angle < 190)) and (length < 300):
            data = np.append(data,l)
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)

x_pos = data.tolist()

x_pos_final = []

for i in range(0,len(x_pos),4):
    x_pos_final.append(x_pos[i])

x_pos_final.sort()

def get_xvals(sorted_list):
    avg_vals = []
    acc = []
    for i in range (0,len(sorted_list)-1):
        test_a = sorted_list[i]
        test_b = sorted_list[i+1]

        test = test_a/test_b

        if test < 0.98:
            temp = mean(acc)
            avg_vals.append(temp)
            acc = []
        if i == (len(sorted_list)-2):
            temp = mean(acc)
            avg_vals.append(temp)
            acc = []
        else:
            acc.append(test_a)

    for i in avg_vals:
        x1 = avg_vals[0]
        x2 = avg_vals[3]

    if len(avg_vals) != 4:
        return(-1)
    
    return([x1, x2])

positions = get_xvals(x_pos_final)

def move(a,b):
    tolerance = 50
    left = a
    right = 2592 - b
    print(left,right)
    test = left - right
    if test > tolerance:
        return('move left')
    if test < -tolerance:
        return('move right')
    else:
        return('ok!')

print(move(positions[0], positions[1]))

new = cv.resize(cdstP, (int(2592/3),int(1944/3)))
cv.imshow("Detected Lines", new)
cv.waitKey(0)

#sm_image = cv.resize(image, (320,180))
#sm_output = cv.resize(output, (320,180))
#cv.imshow("images", np.hstack([sm_image, sm_output]))
#cv.waitKey(0)
