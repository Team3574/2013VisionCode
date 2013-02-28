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
# along with the project High Tekerz 2013 Vision Code.  If not, see 
# <http://www.gnu.org/licenses/>.


import numpy as np
import cv2
import cv
import math
from Point import Point

# If on the robot network
robot = False

if robot:
    import nt_client

class TargetFinder:
    """
    TargetFinder: Used to process squares
    """

    FOCAL_LENGTH = 8 * 0.03937
    TOP_TARGET_HEIGHT = 80 / 0.03937

    SENSOR_HEIGHT = 15 / 0.03937
    
    tmin1 = 0
    tmin2 = 0
    tmin3 = 235
    
    tmax1 = 255
    tmax2 = 255
    tmax3 = 255
    
    centerPoints = []
    centerPointsDict = {}
    
    imgSize = 0

    
    if robot:
        client = nt_client.NetworkTableClient("3574")
    
    def find_targets(self, img, debug = True):
        """
        find_targets: used to find squares in an image
        
        params:
            img: image to process
        
        return:
            An image of the same size with drawn outlines and
            The number of squares found
        """

        if self.imgSize == 0:
            self.imgSize = img.shape

        # Convert image to hsv
        hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
        # Create Thresh values from slider
        THRESH_MIN = np.array([self.tmin1, self.tmin2, self.tmin3],np.uint8)
        THRESH_MAX = np.array([self.tmax1, self.tmax2, self.tmax3],np.uint8)

        # Do in range
        thresh = cv2.inRange(hsv_img, THRESH_MIN, THRESH_MAX)
        
        # Blur the image
        thresh = cv2.GaussianBlur(thresh, (5, 5), 0)

        # Do canny
        thresh = cv2.Canny(thresh, 2, 4)
        
        # Try to close targets
        st = cv2.getStructuringElement(getattr(cv2, "MORPH_RECT"), (4, 4))
        thresh = cv2.morphologyEx(thresh, getattr(cv2, "MORPH_CLOSE"), st, iterations=2)
    
        # Show the threshed image
        if debug:
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
                            
                            if robot:
                                self.client.setValue("Vision/TargetTest", center.x)
                            self.centerPoints.append(center)
                            squares.append(approx)
                            
                            if debug:
                                # Draw the center point
                                cv2.circle(img, center.getTuple(), 4, (0,255,0), 3)

        # Sorting the center points
        #self.centerPoints, num = self.classifyTargets()
        self.centerPointsDict = self.sortTargets(self.centerPoints)

        if debug:
            # Draw all the squares
            cv2.polylines(img, squares, True, (0, 255, 0), 4)

            for i, center in self.centerPointsDict.iteritems():
                if center is not None:
                    cv2.putText(img, str(i), center.getTuple(), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
                
    
        return img
    

    def sortTargets(self, points):
        points = sorted(points, key=lambda point: point.x)

        if len(points) == 4:
            return {"mid-left":points[0], "top":points[1], "mid-right":points[2], "bottom":points[3]}

        ret = dict()

        # New way
        if len(points) == 3:
            angleOneToTwo = self.lineAngle(points[0], points[1])
            angleTwoToThree = self.lineAngle(points[1], points[2])
            
            print angleOneToTwo, "One to two | ", angleTwoToThree, "Two to three"

            # If it is less than 0 we have a left and middle
            if int(angleOneToTwo) in range(-36, -14):
                ret["mid-left"] = points[0]
                ret["top"] = points[1]

                if angleTwoToThree > 20:
                    ret["mid-right"] = None
                    ret["bottom"] = points[2]
                else:
                    ret["mid-right"] = points[2]
                    ret["bottom"] = None
            elif int(angleOneToTwo) in range(0, 4) or int(angleOneToTwo) in range(-11, -6):
                ret["mid-left"] = points[0]
                ret["top"] = None
                ret["mid-right"] = points[1]
                ret["bottom"] = points[2]
            else:
                ret["mid-left"] = None
                ret["top"] = points[0]
                ret["mid-right"] = points[1]
                ret["bottom"] = points[2]
            return ret

        if len(points) == 2:
            angle = self.lineAngle(points[0], points[1])
            
            print angle, "Angle"

            # If it is less than 0 we have a left and middle
            if int(angle) in range(-36, -14):
                ret["mid-left"] = points[0]
                ret["top"] = points[1]
                ret["mid-right"] = None
                ret["bottom"] = None
            elif int(angle) in range(0, 4) or int(angle) in range(-11, -6):
                ret["mid-left"] = points[0]
                ret["top"] = None
                ret["mid-right"] = points[1]
                ret["bottom"] = None
            elif angle > 43:
                ret["mid-left"]= None
                ret["top"] = points[0]
                ret["mid-right"] = None
                ret["bottom"] = points[1]
            elif angle > 42.5:
                ret["mid-left"]= points[0]
                ret["top"] = None
                ret["mid-right"] = None
                ret["bottom"] = points[1]
            elif angle > 40:
                ret["mid-left"]= None
                ret["top"] = None
                ret["mid-right"] = points[0]
                ret["bottom"] = points[1]
            elif int(angle) in range(5, 10):
                ret["mid-left"]= None
                ret["top"] = points[0]
                ret["mid-right"] = points[1]
                ret["bottom"] = None
            return ret

        dic = {}
        for i, point in enumerate(points):
            dic[i] = point
        return dic

        
    def lineLength(self, point1, point2):
        ans = pow(point2.x - point1.x, 2) + pow(point2.y - point1.y, 2)
        ans = math.sqrt(ans);
        return ans 

    def lineAngle(self, point1, point2):
        return math.atan2(point2.y - point1.y, point2.x - point2.y) * 180 / math.pi

    def calculateCenterPoint(self, rect):
        centerX = (rect[0][0][0] + rect[1][0][0] + rect[2][0][0] + rect[3][0][0]) / 4
        centerY = (rect[0][0][1] + rect[1][0][1] + rect[2][0][1] + rect[3][0][1]) / 4
        return Point(centerX, centerY)

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
    
    # Storage for discs and blobs of discs
    # Circles are stored as a tuple containing the circle data
    # an it's calculated target point
    discs = []
    discBlobs = []
    
    imgSize = 0

    # Should work
    if robot:
        client = nt_client.NetworkTableClient("3574")
    
    def find_discs(self, img, debug = True):

        if self.imgSize == 0:
            self.imgSize = img.shape
        
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
        
        # TODO: Clear disc and discblobs
        del self.discBlobs[:]
        self.discBlobs = []
        
        del self.discs[:]
        self.discs = []
        
        # Loop through contours
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 3, True)
            if len(approx) >= 5 and cv2.contourArea(approx) > 1000:
                circle = cv2.fitEllipse(approx)
                
                x, y, w, h = cv2.boundingRect(approx)

                ratioOfWidthToHeight = 0
                if w > h:
                    ratioOfWidthToHeight = float(w)/h
                else:
                    ratioOfWidthToHeight = float(h)/w
                    
                
                # print relative
                if ratioOfWidthToHeight > .5 and ratioOfWidthToHeight < 1.7:
                    bottom = (x + w/2, y + h)
                    self.discs.append((circle, bottom))
                    
                elif ratioOfWidthToHeight >= 1.7  and ratioOfWidthToHeight < 3:
                    bottom = (x + w/2, y + h)
                    self.discBlobs.append((circle, bottom))
        self.sortDiscs()
        if debug:
            for disc in self.discs:
                cv2.ellipse(img, disc[0], (0,255,0))
                cv2.circle(img, disc[1], 4, (0,255,0), 3)
            for disc in self.discBlobs:
                cv2.ellipse(img, disc[0], (255,0,0))
                cv2.circle(img, disc[1], 4, (255,0,0), 3)
            
        return img
    
    def sortDiscs(self):
        if len(self.discs) > 0:
            tmpDiscs = []
            self.discs = sorted(self.discs, key=lambda x: x[1][1])
            middle = 640 / 2
            # TODO: Use brain latter when not so tired and do the simple math
            offset = 1 - float(self.discs[0][1][1]) / middle
            if robot:
                self.client.setValue("/Vision/DiscLocation", offset)
            print "Value Sent", offset, "| Middle", middle
            return
        if robot:
            self.client.setValue("/Vision/DiscLocation", -10000.0)
    
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
