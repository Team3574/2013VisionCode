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
from Processor2 import TargetFinder
from Processor2 import DiscFinder
from glob import glob

# The if __name__ determines the scope in which the
# file is running. If it is the current file running we
# will do the program. This is not needed but it is a
# standard way of making sure it runs properly
if __name__ == '__main__':

    # Debug?
    debug = True

    # Use a camera?
    camera = False

    # for shooting target
    cameraNumber1 = 1
    # fro frisbees
    cameraNumber2 = 0

    # Create a Processor object
    targetFinder = TargetFinder()
    discFinder = DiscFinder()

    if debug:
        cv2.namedWindow("bars")

        # Add trackbars to the window to adjust the min hsv values
        cv2.createTrackbar("H-Min", "bars", discFinder.tmin1, 255, discFinder.min1)
        cv2.createTrackbar("S-Min", "bars", discFinder.tmin2, 255, discFinder.min2)
        cv2.createTrackbar("V-Min", "bars", discFinder.tmin3, 255, discFinder.min3)

        # Add trackbars to the window to adjust the max hsv values
        cv2.createTrackbar("H-Max", "bars", discFinder.tmax1, 255, discFinder.max1)
        cv2.createTrackbar("S-Max", "bars", discFinder.tmax2, 255, discFinder.max2)
        cv2.createTrackbar("V-Max", "bars", discFinder.tmax3, 255, discFinder.max3)

    if camera:
        if debug:
            # Create window
            cv2.namedWindow("Processed")
            cv2.namedWindow("Processed2")

        # Create Video Capture
        cap = cv2.VideoCapture(cameraNumber1)
        cap2 = cv2.VideoCapture(cameraNumber2)

        while cv2.waitKey(30) < 10:
            # Get the current camera image
            ret, img = cap.read()
            ret2, img2 = cap2.read()

            # Returns the image and the amount of squares found
            img = targetFinder.find_targets(img, debug = debug)

            img2 = discFinder.find_discs(img2, debug = debug)

            if debug:
                # Show the processed image
                cv2.imshow('Processed', img)
                cv2.imshow('Processed2', img2)

    else:
        for image in glob('targets3/*.jpg'):
            img = cv2.imread(image)
            img = targetFinder.find_targets(img, debug = debug)
            cv2.namedWindow('processed' + str(image))
            cv2.imshow('processed' + str(image), img)

        for image in glob('discs/*.jpg'):
            img = cv2.imread(image)
            img = discFinder.find_discs(img, debug = debug)
            cv2.namedWindow('processed' + str(image))
            cv2.imshow('processed' + str(image), img)
        cv2.waitKey(0)
    cv2.destroyAllWindows()
