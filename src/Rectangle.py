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

from Point import Point

class Rectangle:
	width = 0.0
	height = 0.0
	centerPoint = None
	
	def __init__ (self, width, height, centerPoint):
		self.width = width
		self.height = height
		self.centerPoint = centerPoint
		
	def getWidth(self):
		return self.width
		
	def getHeight(self):
		return self.height
		
	def getCenterPoint(self):
		return self.centerPoint
		
	def setWidth(self, width):
		self.width = width
		
	def setHeight(self, height):
		self.height = height
		
	def setCenterPoint(self, centerPoint):
		self.centerPoint = centerPoint
		
	@staticmethod
	def isTarget(width1, width2, height1, height2):
		if width1 < 20 or width2 < 20:
			return False
		
		width = (width1 + width2) / 2
		height = (height1 + height2) / 2
		ratio = height / width
		print "Ratio: " , ratio
		
		# 3.1 is our ratio we want
		
		if abs(width1 - width2) < 6 and abs(height2-height1) < 6:
			return True
		return False

if __name__ == '__main__':
	testRect = Rectangle(100, 75, Point(6, 60))
	print testRect.getWidth()
	testRect.setWidth(60)
	print testRect.getWidth()
