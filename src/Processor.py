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


import numpy as np
import cv2
import math

class Processor:
    """
    Processor: Used to process images
    """
    
    tmin1 = 0
    tmin2 = 0
    tmin3 = 200
    
    tmax1 = 255
    tmax2 = 255
    tmax3 = 255
    
    scale = 0.02
    
    distanceToTarget = 0
    
    biggestLine = 0
    
    def find_squares(self, img, debug = True, time = 0):
        """
        find_squares: used to find squares in an image
        
        params:
            img: image to process
        
        return:
            An image of the same size with drawn outlines and
            The number of squares found
        """

        # Blur the image
        img = cv2.GaussianBlur(img, (5, 5), 0)
    
        # Create Thresh values from slider
        THRESH_MIN = np.array([self.tmin1, self.tmin2, self.tmin3],np.uint8)
        THRESH_MAX = np.array([self.tmax1, self.tmax2, self.tmax3],np.uint8)

        # Convert image to hsv
        hsv_img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    
        # Do in range
        thresh = cv2.inRange(hsv_img, THRESH_MIN, THRESH_MAX)
        
        thresh = cv2.dilate(thresh, None)
        
        thresh = cv2.erode(thresh, None)
    
        # Show the threshed image
        if debug:
            cv2.imshow('thresh', thresh);
    
        # Storage for squares
        squares = []
    
        # Get all contours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
        lastContour = None
        length = len(contours)
        status = np.zeros((length, 1))
    
        # Check if the contours have 4 sides and store it if it does
        for contour in contours:
            # New way
            if True:
                if cv2.contourArea(contour) > 1000:
                
                    hull = cv2.convexHull(contour)
                    hull = cv2.approxPolyDP(hull, 0.04*cv2.arcLength(hull, True), True)
                    
                    if len(hull) == 4:
                        length = self.lineLength(hull[0][0], hull[1][0])
                        if time == 0:
                            cv2.drawContours(img, [hull], 0, (255,255,255), thickness = -1)
                        else:
                            cv2.drawContours(img, [hull], 0, (0,255,0), thickness = 2)

            # "Working" way
            if False:
                rect = cv2.minAreaRect(contour)
                
                # Find four vertices of rectangle from above rect
                box = cv2.cv.BoxPoints(rect)
                
                # Round the values and make it integers
                box = np.int0(np.around(box))
                
                # The box array looks like this
                # [
                #     point top right,
                #     point top left,
                #     point bottom left,
                #     point bottom right
                # ]
                
                #calculate the width / length
                dimentionThreshX = self.lineLength(box[0], box[1])
                dimentionThreshY = self.lineLength(box[1], box[2])
                
                #dimentionThreshX = box[0][0] - box[1][0]
                #dimentionThreshY = box[1][1] - box[2][1]
                
                if dimentionThreshY > 0:
                    dimentionThresh = dimentionThreshX / dimentionThreshY
                else:
                    dimentionThresh = 0
                    
                #if box[0][0] > 200:
                    #print dimentionThresh
                    #print dimentionThreshX, ", ", dimentionThreshY
                    #squares.append(box)
                    
                #print dimentionThresh
                
                # in a perfect world our box would always be 3.1 when
                # dividing the width by length. So in this imperfect world
                # we check if it is within a resonalble range ie +- .5
                if dimentionThresh > 2.6 and dimentionThresh < 3.5:
                    print dimentionThresh
                    print box
                    squares.append(box)
        
        self.lastPoints = squares
            
        # Draw all the squares
        cv2.polylines(img, squares, True, (0, 255, 0), 2)
    
        # Return the image we drew on and the number of squares found
        if time == 0:
            return self.find_squares(img, time = 1)
        else:
            return img, len(squares)
    
    def calculateDistance(self, rect):
        print "test"
        
    def lineLength(self, point1, point2):
        ans = pow(point2[0] - point1[0], 2) + pow(point2[1] - point1[1], 2)
        ans = math.sqrt(ans);
        return ans
        
    def find_if_close(cnt1,cnt2):
        row1,row2 = cnt1.shape[0],cnt2.shape[0]
        for i in xrange(row1):
            for j in xrange(row2):
                dist = np.linalg.norm(cnt1[i]-cnt2[j])
                if abs(dist) < 50 :
                    return True
                elif i==row1-1 and j==row2-1:
                    return False
        
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

 
#    The if __name__ determines the scope in which the
#    file is running. If it is the current file running we
#    will do the program. This is not needed but it is a
#    standard way of making sure it runs properly and a 
#    way of putting an example of how to use a class
if __name__ == '__main__':
    # Create Processor object
    processor = Processor()
    
    # Create window
    cv2.namedWindow("Processed")
    
    # Create Video Capture
    cap = cv2.VideoCapture(0)
    
    while True:
        # Get the current camera image
        ret, img = cap.read()
        
        # Returns the image and the ammount of squares found
        img, num = processor.find_squares(img)
        
        # Show the processed image
        cv2.imshow('Processed', img)
        
        # Wait for a key press
        if cv2.waitKey(30) >= 10:
            #Exit the wile loop
            break

