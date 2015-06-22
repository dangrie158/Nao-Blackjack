import HelperFunctions as hf
import operator
import cv2
import math
import os
from sys import maxint
from numpy import average, copy, reshape
import eigenVectorDetection as ev

VALUE_SIZE = (40, 20)
VALUE_OFFSET = (5,5)


#very easy wrapper class to map values to
# the relative index in the case vector
class Value:
	def __init__(self, index, value):
		self.index = index
		self.value = value

Value.Two = Value(0, 2)
Value.Three = Value(1, 3)
Value.Four = Value(2, 4)
Value.Five = Value(3, 5)
Value.Six = Value(4, 6)
Value.Seven = Value(5, 7)
Value.Eight = Value(6, 8)
Value.Nine = Value(7, 9)
Value.Ten = Value(8, 10)
Value.Jack = Value(8, 10)
Value.Queen = Value(8, 10)
Value.King = Value(8, 10);
Value.Ace = Value(9, 0)
Value.Undefined = Value(-1, -1)

#the representation af a card. this is both,
#the imagedata from the camera and a value to calculate
#the handvalue and the casevector
class Card:

	def __init__(self, imageData, rect, value = Value.Undefined):
		self.image = imageData
		self.frameRectangle = rect
		self.value = value

		if imageData is not None:
			self.generateSIFTDescriptor(hf.SIFT, self.getValueImage())

		if hasattr(Card, "eigenSpace"):
			self.numpyImage = hf.cvImageToNumpy(self.getValueImage())
			self.avgImage = self.numpyImage - Card.averageImage
			self.calculateEigenFace(Card.eigenSpace)

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

	def detectValueSIFT(self, sift):
		matcher = cv2.BFMatcher()
		bestNumGoodMatches = 0
		bestMatch = None
		bestDistance = maxint

		for sampleCardName, sampleCard in Card.sampleFiles.iteritems():
			summaryDistance = 0
			matches = matcher.match(self.descriptor, sampleCard.descriptor)
			matches = sorted(matches, key = lambda x:x.distance)

			for m in matches:
				summaryDistance += int(m.distance)
			if((summaryDistance / len(matches)) < bestDistance):
				bestMatch = sampleCardName
				bestDistance = summaryDistance / len(matches)
		print "Best Match is: " + bestMatch


	def detectValueEigen(self):
		transposedImages = []
		fileNames = []
		for fileName, card in Card.sampleFiles.iteritems():
			fileNames.append(fileName)
			transposedImages.append(card.transposedImg)
		closestFile, distance = ev.calculateDistance(transposedImages, self.transposedImg, fileNames)
		print "closest distance: " + str(distance) + " image: " + fileNames[closestFile]


	def calculateEigenFace(self, eigenspace):
		self.transposedImg = ev.transformToEigenfaceSpace(eigenspace, self.avgImage, ev.NUMFEATURES)

	def generateSIFTDescriptor(self, sift, image):
		self.keypoints, self.descriptor = sift.detectAndCompute(image, None)	


def generateEigenSpace(cards):
	images = []
	for card in cards.itervalues():
		npImg = hf.cvImageToNumpy(card.getValueImage())
		images.append(npImg)
		card.numpyImage = npImg
	avgImage = ev.calculateAverageImg(copy(images))
	#cv2.imshow("average", hf.numpyImageToCV(avgImage))
	normedArrayOfFaces = ev.removeAverageImage(copy(images), avgImage)
	eigenspace = ev.calculateEigenfaces(normedArrayOfFaces.T, len(images[0]), len(images))
	for card in cards.itervalues():
		card.avgImage = card.numpyImage - avgImage
		card.calculateEigenFace(eigenspace)
	return eigenspace, avgImage

def loadSampleFiles(path):
	cardPaths = os.listdir(path)
	trainset = {}
	for card in cardPaths:
		cardName = card[0:-4]
		cardImage = cv2.imread(os.path.join(path, card), 0)
		trainset[cardName] = Card(cardImage, None);
	return trainset

Card.sampleFiles = loadSampleFiles(os.path.join(os.getcwd(), hf.TRAINSET))
Card.eigenSpace, Card.averageImage = generateEigenSpace(Card.sampleFiles)