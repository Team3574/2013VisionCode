# This file is part of the project High Tekerz 2013 Vision Code.
#
# the project High Tekerz 2013 Vision Code is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# High Tekerz 2013 Vision Code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the project High Tekerz 2013 Vision Code.  If not, see <http://www.gnu.org/licenses/>.


import operator
import numpy as np
import cv2
import cv
import math
from Rectangle import Rectangle
from Point import Point
#import nt_client

class TargetFinder:
    """
    Processor: Used to process images
    """
    
    tmin1 = 0
    tmin2 = 0
    tmin3 = 235
    
    tmax1 = 255
    tmax2 = 255
    tmax3 = 255
    
    centerPoints = []
    
    kalmanFilters = []
    
    imgSize = 0
    
    def __init__(self):
        for i in range(4):
            self.kalmanFilters.append(cv2.KalmanFilter(dynamParams=2, measureParams=2))
    
    def find_targets(self, img, debug = True):
        """
        find_squares: used to find squares in an image
        
        params:
            img: image to process
        
        return:
            An image of the same size with drawn outlines and
            The number of squares found
        """

        if self.imgSize == 0:
            self.imgSize = img.shape
        

        # Blur the image
        img = cv2.GaussianBlur(img, (5, 5), 0)
    
        # Create Thresh values from slider
        THRESH_MIN = np.array([self.tmin1, self.tmin2, self.tmin3],np.uint8)
        THRESH_MAX = np.array([self.tmax1, self.tmax2, self.tmax3],np.uint8)

        # Convert image to hsv
        hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
        # Do in range
        thresh = cv2.inRange(hsv_img, THRESH_MIN, THRESH_MAX)
        
        # Do canny
        thresh = cv2.Canny(thresh, 2, 4)
        
        # Try to close targets
        st = cv2.getStructuringElement(getattr(cv2, "MORPH_RECT"), (2, 2))
        thresh = cv2.morphologyEx(thresh, getattr(cv2, "MORPH_CLOSE"), st, iterations=2)
    
        # Show the threshed image
        if debug:
            #cv2.imshow('thresh' + str(self.t), thresh);
            cv2.imshow('thresh', thresh);
    
        # Storage for squares
        squares = []
    
        # Get all contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
        del self.centerPoints[:]
        self.centerpoints = []
        tmpCenterPoints = []
    
        # IF we find anything
        if hierarchy != None:
            # Get rid of unnessary values
            hierarchy = hierarchy[0]
    
            # Check if the contours have 4 sides and store it if it does
            for component in zip(contours, hierarchy):
                contour = component[0]
                currHierarchy = component[1]
                
                # Process only good size object
                if cv2.contourArea(contour) > 1000:
                    # Aproximate shape
                    curve = cv2.convexHull(contour)
                    approx = cv2.approxPolyDP(contour, cv2.arcLength(contour, True) * 0.03, True)
                    
                    # If the shape has four corners
                    if len(approx) == 4:
                        # If curent approximation has another one inside of it
                        if currHierarchy[3] < 0:
                            center = self.calculateCenterPoint(approx)
                            self.centerPoints.append(center)
                            squares.append(approx)
                            
                            if debug:
                                # Draw the center point
                                cv2.circle(img, center.getTuple(), 4, (0,255,0), 3)
        
        # Sorting the center points
        self.centerPoints.sort()
        
        if debug:
            # Draw all the squares
            cv2.polylines(img, squares, True, (0, 255, 0), 4)
    
        return img, len(squares)
        
    def classifyTargets(self):
        """
        Returns both the targets and the number of targets
        """
        return (), 0
    
    def calculateDistance(self, rect):
        print "test"

        
    def lineLength(self, point1, point2):
        ans = pow(point2[0] - point1[0], 2) + pow(point2[1] - point1[1], 2)
        ans = math.sqrt(ans);
        return ans

    def calculateCenterPoint(self, rect):
        centerX = (rect[0][0][0] + rect[1][0][0] + rect[2][0][0] + rect[3][0][0]) / 4
        centerY = (rect[0][0][1] + rect[1][0][1] + rect[2][0][1] + rect[3][0][1]) / 4
        return Point(centerX, centerY)
        
    def organizePoints(self):
        self.centerpoints.sort()
                
        
    def min1(self, x):
        self.tmin1 = x

    def min2(self, x):
        self.tmin2 = x
    
    def min3(self, x):
        self.tmin3 = x
    
    def max1(self, x):
        self.tmax1 = x
    
    def max2(self, x):
        self.tmax2 = x
    
    def max3(self, x):
        self.tmax3 = x
        
        
class DiscFinder:
    
    timesRun = 0
    
    tmin1 = 0
    tmin2 = 0
    tmin3 = 190
    
    tmax1 = 255
    tmax2 = 255
    tmax3 = 255
    
    thmin2 = 55
    thmax2 = 255
    
    centerPoints = []
    
    # Should work
    # client = nt_client.INSTANCE
    
    def find_discs(self, img, debug = True):
        
        del self.centerPoints[:]
        self.centerPoints = []
        
        # Blur the image
        img = cv2.GaussianBlur(img, (5,5), 0)
    
        # Create Thresh values from slider
        THRESH_MIN = np.array([self.tmin1, self.tmin2, self.tmin3],np.uint8)
        THRESH_MAX = np.array([self.tmax1, self.tmax2, self.tmax3],np.uint8)

        # Convert image to hsv
        hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
        # Do in range
        thresh = cv2.inRange(hsv_img, THRESH_MIN, THRESH_MAX)
        
        thresh = cv2.GaussianBlur(thresh, (7,7), 0)
        
        # Try to close targets
        st = cv2.getStructuringElement(getattr(cv2, "MORPH_RECT"), (10, 10))
        thresh = cv2.morphologyEx(thresh, getattr(cv2, "MORPH_CLOSE"), st, iterations=2)
        
        # Thresh again
        THRESH_MIN = np.array([self.thmin2],np.uint8)
        THRESH_MAX = np.array([self.thmax2],np.uint8)
        
        # Thresh again
        thresh = cv2.inRange(thresh, THRESH_MIN, THRESH_MAX)
        cv2.imshow('frisbeethresh', thresh)
        
        # Do canny
        thresh = cv2.Canny(thresh, 1, 1)
        
        if debug:
            cv2.imshow('canny', thresh);
        
        
        # Storage for circles
        circles = []
        
        # Look for Contours
        contours, higharchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Storage for discs and blobs of discs
        # Circles are stored as a tuple containing the circle data
        # an it's calculated target point
        discs = []
        discBlobs = []
        
        # Loop through contours
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 3, True)
            if len(approx) >= 5 and cv2.contourArea(approx) > 3000:
                circle = cv2.fitEllipse(approx)
                
                x, y, w, h = cv2.boundingRect(approx)

                relative = 0
                if w > h:
                    relative = float(w)/h
                else:
                    relative = float(h)/w
                    
                
                # print relative
                if relative > .5 and relative < 1.7:
                    bottom = (x + w/2, y + h)
                    discs.append((circle, bottom))
                    
                elif relative >= 1.7  and relative < 3:
                    bottom = (x + w/2, y + h)
                    discsBlobs.append((circle, bottom))       
        if debug:
            for disc in discs:
                cv2.ellipse(img, disc[0], (0,255,0))
                cv2.circle(img, disc[1], 4, (0,255,0), 3)
            for disc in discBlobs:
                cv2.ellipse(img, disc[0], (255,0,0))
                cv2.circle(img, disc[1], 4, (255,0,0), 3)
            
        return img, 0
    
    
    def min1(self, x):
        self.tmin1 = x

    def min2(self, x):
        self.tmin2 = x
    
    def min3(self, x):
        self.tmin3 = x
    
    def max1(self, x):
        self.tmax1 = x
    
    def max2(self, x):
        self.tmax2 = x
    
    def max3(self, x):
        self.tmax3 = x
