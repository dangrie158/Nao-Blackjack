import HelperFunctions as hf
import operator
import cv2
import math

VALUE_SIZE = (15, 20)
VALUE_OFFSET = (5,5)

class Card:
	def __init__(self, imageData, rect):
		self.image = imageData
		self.frameRectangle = rect

	def getValue(self):
		return hf.cropPercentage(self.image, (VALUE_OFFSET), tuple(map(operator.add, VALUE_SIZE, VALUE_OFFSET)))

	def getThumbnail(self, thumbnailSize = (70, 100)):
		return cv2.resize(self.image, thumbnailSize)

	def getBoundingBox(self):
		return hf.boundingBox(self.frameRectangle)

	def getRectangleInFrame(self):
		return self.frameRectangle

	def getCenteroidInFrame(self):
		return hf.polygonCentroid(self.frameRectangle)

	def intersectingBoundingBox(self, other):
		return hf.rectangeIntersectionArea(self.getBoundingBox(), other.getBoundingBox())

	def hasSameBoundingBoxAs(self, other, proximity = 0.6):
		intersectionArea = self.intersectingBoundingBox(other)
		if intersectionArea > 0:
			ownArea = hf.rectangleArea(self.getBoundingBox())
			absoluteRatio = ownArea / intersectionArea
			if absoluteRatio > 1 :
				return (1 / absoluteRatio) >= proximity
			else:
				return absoluteRatio >= proximity
		else:
			return False
		