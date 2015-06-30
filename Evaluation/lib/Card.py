import HelperFunctions as hf
import operator
import cv2
import math
from RecognitionEngine import SIFTRecognitionEngine
from RecognitionEngine import EigenRecognitionEngine
from RecognitionEngine import BinaryRecognitionEngine
from RecognitionEngine import Value

VALUE_SIZE = (40, 20)
VALUE_OFFSET = (5,5)

TRAINSET = "trainingsset2"

CurrentRecognitionEngine = BinaryRecognitionEngine(useValueOnly = False);
CurrentRecognitionEngine.train(TRAINSET)

#the representation af a card. this is both,
#the imagedata from the camera and a value to calculate
#the handvalue and the casevector
class Card(object):

	def __init__(self, imageData, rect, value = Value.Undefined):
		self.image = imageData
		self.frameRectangle = rect
		self.value = value

		if imageData is not None:
			CurrentRecognitionEngine.recognize(self)

	def getValueImage(self):
		return hf.cropPercentage(self.image, (VALUE_OFFSET), tuple(map(operator.add, VALUE_SIZE, VALUE_OFFSET)))

	def getThumbnail(self, thumbnailSize = (70, 100)):
		return cv2.resize(self.image, thumbnailSize)

	def getBoundingBox(self):
		return hf.boundingBox(self.frameRectangle)

	def getRectangleInFrame(self):
		return self.frameRectangle

	def getWidth(self):
		p1, p2 = self.getBoundingBox()
		return p2[0] - p1[0]

	def getHeight(self):
		p1, p2 = self.getBoundingBox()
		return p2[1] - p1[1]

	def getCenteroidInFrame(self):
		return hf.polygonCentroid(self.frameRectangle)

	def getIntersectingBoundingBox(self, other):
		return hf.rectangeIntersectionArea(self.getBoundingBox(), other.getBoundingBox())

	def overlaps(self, other):
		p1, p2 = self.getBoundingBox()
		p3, p4 = other.getBoundingBox()
		return hf.euclidDist(p1, p3) <= self.getWidth() or hf.euclidDist(p2, p4) <= self.getWidth()

	def hasSameBoundingBoxAs(self, other, proximity = 0.6):
		intersectionArea = self.getIntersectingBoundingBox(other)
		if intersectionArea > 0:
			ownArea = hf.rectangleArea(self.getBoundingBox())
			absoluteRatio = ownArea / intersectionArea
			if absoluteRatio > 1 :
				return (1 / absoluteRatio) >= proximity
			else:
				return absoluteRatio >= proximity
		else:
			return False