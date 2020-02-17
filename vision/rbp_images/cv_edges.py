#Code modified from Saima Ali's computer vision seminar for ESC204

import cv2 as cv
import numpy as np

if __name__ == "__main__":
    print("Edge Detection")

    im1 = cv.imread('test1.jpg', cv.IMREAD_GRAYSCALE)    
    im2 = cv.imread('test2.jpg', cv.IMREAD_GRAYSCALE)    


    edges1 = cv.Canny(im1,100,200)
    edges2 = cv.Canny(im2,100,200)


    cv.namedWindow('Test 1')
    cv.imshow('Test 1', edges1)

    cv.namedWindow('Test 2')
    cv.imshow('Test 2', edges2)

    cv.waitKey(0)
