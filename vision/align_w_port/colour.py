import numpy as np
import cv2

image = cv2.imread('l1.jpg')

boundaries = [([110,70,0], [150,110,10])]

for (lower, upper) in boundaries:
    lower = np.array(lower, dtype = "uint8")
    upper = np.array(upper, dtype = "uint8")
    mask = cv2.inRange(image, lower, upper)
    output = cv2.bitwise_and(image, image, mask = mask)
    sm_image = cv2.resize(image, (160,90))
    sm_output = cv2.resize(output, (160,90))
    cv2.imshow("images", np.hstack([sm_image, sm_output]))
    cv2.waitKey(0)
