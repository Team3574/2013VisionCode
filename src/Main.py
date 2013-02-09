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


import cv2
from Processor import Processor
 
# The if __name__ determines the scope in which the
# file is running. If it is the current file running we
# will do the program. This is not needed but it is a
# standard way of making sure it runs properly
if __name__ == '__main__':

    #Debug?
    debug = True    
    
    # Create a Processor object
    processor = Processor()

    # Creeate window
    cv2.namedWindow("Processed")
    cv2.namedWindow("bars")
    
    if debug:
        # Add trackbars to the window to adjust the min hsv values
        cv2.createTrackbar("H-Min", "bars", processor.tmin1, 255, processor.min1)
        cv2.createTrackbar("S-Min", "bars", processor.tmin2, 255, processor.min2)
        cv2.createTrackbar("V-Min", "bars", processor.tmin3, 255, processor.min3)
    
        # Add trackbars to the window to adjust the max hsv values
        cv2.createTrackbar("H-Max", "bars", processor.tmax1, 255, processor.max1)
        cv2.createTrackbar("S-Max", "bars", processor.tmax2, 255, processor.max2)
        cv2.createTrackbar("V-Max", "bars", processor.tmax3, 255, processor.max3)

    # Create Video Capture
    cap = cv2.VideoCapture(0)

    while True:
        # Get the current camera image
        ret, img = cap.read()

        # Returns the image and the ammount of squares found
        img, num = processor.find_squares(img, debug = debug)
        
        # Show the processed image
        cv2.imshow('Processed', img)
        
        # Wait for a key press
        if cv2.waitKey(30) >= 10:
            #Exit the wile loop
            break
