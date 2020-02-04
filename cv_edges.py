import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print("Edge Detection")

    im1 = cv.imread('good_angle_right.jpg', cv.IMREAD_GRAYSCALE)    
    im2 = cv.imread('bad_angle_right.JPG', cv.IMREAD_GRAYSCALE)    


    edges1 = cv.Canny(im1,100,200)
    edges2 = cv.Canny(im2,100,200)


    cv.namedWindow('Good Case Test')
    cv.imshow('Good Case Test', edges1)

    cv.namedWindow('Bad Case Test')
    cv.imshow('Bad Case Test', edges2)

    cv.waitKey(0)
