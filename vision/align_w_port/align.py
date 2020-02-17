import math
import cv2 as cv
import numpy as np

filename = 'middle1.jpg'
pre_crop = cv.imread(filename, cv.IMREAD_GRAYSCALE)
image = pre_crop[240:1944-240,920:2592-920]
    
dst = cv.Canny(image, 100, 200)
    
cdstP = cv.cvtColor(dst, cv.COLOR_GRAY2BGR)

linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None, 70, 5)

data = np.empty([0,4], int)

if linesP is not None:
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        angle = np.arctan2(l[2] - l[0], l[3] - l[1]) * 180. / np.pi
        length = l[1] - l[3]
        if ((angle > 175) and (angle < 185)) and (length < 300):
            data = np.append(data,l)
            cv.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)

x1 = data[0]
x2 = 752 - data[4]

def move(a,b):
    test = a-b
    if test > 10:
        print('move left')
    if test < 10:
        print('move right')
    else:
        print('ok!')

move(x1,x2)

new = cv.resize(cdstP, (752,1464))
cv.imshow("Detected Lines", new)
cv.waitKey()