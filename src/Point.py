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


class Point:
	
	x = 0.0
	y = 0.0
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
	def getX(self):
		return self.x
		
	def getY(self):
		return self.y
		
	def getTuple(self):
		return (self.x, self.y)
		
	def setX(self, x):
		self.x = x
		
	def setY(self, y):
		self.y = y
		
	def __repr__(self):
		return "(" + str(self.x) + "," + str(self.y) + ")"
		
	def __str__(self):
		return "(" + str(self.x) + "," + str(self.y) + ")"
		
	def __cmp__(self, other):
		return cmp(self.x, other.x)
