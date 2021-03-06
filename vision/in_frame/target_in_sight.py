import math
import numpy as np
import cv2 as cv
from statistics import mean 
'''from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180

sleep(2)
camera.capture('/home/jon_pi/praxis.jpg')'''

image = cv.imread('l3.jpg')

#only checks right side of image
#crop_img = image[400:1944-400, 0:2592]

blue = ([95,65,0], [165,180,40])

(lower, upper) = blue
lower = np.array(lower, dtype = "uint8")
upper = np.array(upper, dtype = "uint8")
mask = cv.inRange(image, lower, upper)
output = cv.bitwise_and(image, image, mask = mask)

'''new = cv.resize(output, (int(2592/3),int(1944/3)))
cv.imshow("Blue only", new)
cv.waitKey(0)'''

blur = cv.GaussianBlur(output,(5,5),10)

dst = cv.Canny(blur, 100, 200)
    
cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)

lines = cv.HoughLines(dst, 5, np.pi / 180, 50, None, 0, 0)

data = []
angles = []

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
        
        if ((angle > 87) and (angle < 93)):
            data.append(pt1)
            data.append(pt2)
            angles.append(angle)
            cv.line(cdstP, pt1, pt2, (0,0,255), 3, cv.LINE_AA)

data_final = []

for i in range(0,len(data),2):
    temp = (data[i][0] + data[i+1][0])/2
    data_final.append(temp)

data_final.sort()
angles.sort()

def four_lines(sorted_list):
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

    if len(avg_vals) != 4:
        return(False)
    
    return(True)

test1 = four_lines(data_final)

def parallel(sorted_list):
    for i in range(0,len(sorted_list)-1):
        ratio = sorted_list[i]/sorted_list[i+1]
        if (ratio < 0.9) or (ratio > 1.1):
            return(False)
    return(True)

test2 = parallel(angles)

if (test1 == True) and (test2 == True):
    print("Target in sight!")
else:
    print("Target not in sight...")

new = cv.resize(blur, (int(2592/3),int(1144/3)))
cv.imshow("Detected Lines", new)
cv.waitKey(0)

#sm_image = cv.resize(image, (320,180))
#sm_output = cv.resize(output, (320,180))
#cv.imshow("images", np.hstack([sm_image, sm_output]))
#cv.waitKey(0)'''
