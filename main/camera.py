import math
import numpy as np
import cv2 as cv
import imutils
from statistics import mean 
from picamera.array import PiRGBArray 
from picamera import PiCamera
from time import sleep

class ShapeDetector:
	def __init__(self):
		pass
	def detect(self, c):
		# initialize the shape name and approximate the contour
		shape = "unidentified"
		peri = cv.arcLength(c, True)
		approx = cv.approxPolyDP(c, 0.04 * peri, True)

		# if the shape is a triangle, it will have 3 vertices
		if len(approx) == 3:
			shape = "triangle"
		# if the shape has 4 vertices, it is either a square or
		# a rectangle
		elif len(approx) == 4:
			# compute the bounding box of the contour and use the
			# bounding box to compute the aspect ratio
			(x, y, w, h) = cv.boundingRect(approx)
			ar = w / float(h)
			# a square will have an aspect ratio that is approximately
			# equal to one, otherwise, the shape is a rectangle
			shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
		# if the shape is a pentagon, it will have 5 vertices
		elif len(approx) == 5:
			shape = "pentagon"
		# otherwise, we assume the shape is a circle
		else:
			shape = "circle"
		# return the name of the shape
		return shape

class SetCam:
    def __init__(self):
        # Set up RBP camera
        self.camera = PiCamera()
        self.camera.rotation = 180
        self.camera.resolution = (2592, 1944)
        self.rawCapture = PiRGBArray(self.camera)

    # Determine what direction to move in
    def x_pos(self, outPos):
        tolerance = 20
        left = outPos[0]
        right = 2592 - outPos[1]
        test = left - right
        if test > tolerance:
            return([1, test]) # move right
        elif test < -tolerance: 
            return([-1, test]) # move left
        else:
            return([0, test]) # ok

    # Function to find x position of outermost edges of rectangles
    def outer_positions(self, stuff):
        stuff.sort()
        x1 = mean(stuff[0:10])
        x2 = mean(stuff[len(stuff)-10:])
        return([x1,x2])

    # Function to determine the distance to move in mm
    def convert_dist(self, x, y):
        ratio = 174/(-7.9217*y + 2592) #mm/px
        dist = int(x*ratio) #[mm/px]*px = mm 
        return(dist)

    # Top-level function 
    def determine_move(self, tof):
        # Capture image with RBP camera
        sleep(5)
        self.camera.capture(self.rawCapture, format='bgr')
        image = self.rawCapture.array
        image = image[:, :, ::-1]
        cv.imwrite('/home/pi/esc204/bruh.jpg',image)
        self.camera.close()

        # Define bounds on red colour segmentation
        red = ([0,0,80], [75,75,255])

        # Perform colour segmentation
        (lower, upper) = red
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        mask = cv.inRange(image, lower, upper)
        output = cv.bitwise_and(image, image, mask = mask)

        # cv.imwrite("/home/jon_pi/Desktop/hello.jpg", output)

        # Convert colour segmented image to grayscale
        gray = cv.cvtColor(output, cv.COLOR_RGB2GRAY)

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

        # Empty array to collect data points of detected rectangles
        array = []

        # Loop through detected shapes
        for c in cnts:
            M = cv.moments(c)
            cX = int((M["m10"] / (M["m00"] + 1e-7)))
            cY = int((M["m01"] / (M["m00"] + 1e-7)))
            shape = sd.detect(c)
            # Only add shape to list if it is a large rectangle
            if (shape == "rectangle") and (len(c) > 20):
                array.append(c)
                c = c.astype("int")
                cv.drawContours(image, [c], -1, (0, 255, 0), 2)
                cv.putText(image, shape, (cX, cY), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        '''new = cv.resize(image, (int(2592/3),int(1944/3)))
        cv.imshow("Image", new)
        cv.waitKey(0)'''

        # Empty list to collect post-processed data
        data = []

        # Collect x coordinates from first rectangle
        for i in array[0]:
            data.append(i[0][0])

        # Collect x coordinates from second rectangle
        for j in array[1]:
            data.append(j[0][0])

        # Find x position of outermost edges
        positions = self.outer_positions(data)

        move = self.x_pos(positions)

        xDist = self.convert_dist(move[1],tof)

        # -1 -> move left, 1 -> move right, 0 -> don't move; magnitude of move in mm
        return((move[0], xDist))

        '''new = cv.resize(image, (int(2592/3),int(1944/3)))
        cv.imshow("Let's find some rectangles", new)
        cv.waitKey()'''
