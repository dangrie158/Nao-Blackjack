import HelperFunctions as hf
import operator
import cv2

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
		return hf.getBoundingBox(self.frameRectangle)

	def getRectangleInFrame(self):
		return self.frameRectangle

	def getCenteroidInFrame(self):
		return hf.polygonCentroid(self.frameRectangle)
		