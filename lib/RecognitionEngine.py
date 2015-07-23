import os
import cv2
import operator
from sys import maxint
import numpy as np
import eigenVectorDetection as ev
import HelperFunctions as hf


SIFT = cv2.SIFT()

#The size of the corner of the card with the value
#this has not to match the values in Card.py and are independant from one another
#since they both serve their own purpose
VALUE_SIZE = (15, 20)
VALUE_OFFSET = (5,5)

#very easy wrapper class to map values to
# the relative index in the case vector
class Value:
	def __init__(self, index, value, name):
		self.index = index
		self.value = value
		self.name = name

	@staticmethod
	def getValueFromName(name):
		valuePart = name.split("_")[0]

		return {
			"zwei": Value.Two,
			"drei": Value.Three,
			"vier": Value.Four,
			"fuenf": Value.Five,
			"sechs": Value.Six,
			"sieben": Value.Seven,
			"acht": Value.Eight,
			"neun": Value.Nine,
			"zehn": Value.Ten,
			"bube": Value.Jack,
			"dame": Value.Queen,
			"koenig": Value.King,
			"ass": Value.Ace
		}[valuePart]

	@staticmethod
	def getValueFromIndex(index):
		return {
			Value.Two.index: Value.Two,
			Value.Three.index: Value.Three,
			Value.Four.index: Value.Four,
			Value.Five.index: Value.Five,
			Value.Six.index: Value.Six,
			Value.Seven.index: Value.Seven,
			Value.Eight.index: Value.Eight,
			Value.Nine.index: Value.Nine,
			Value.Ten.index: Value.Ten,
			Value.Jack.index: Value.Jack,
			Value.Queen.index: Value.Queen,
			Value.King.index: Value.King,
			Value.Ace.index: Value.Ace
		}[index]

Value.Two = Value(0, 2, "Two")
Value.Three = Value(1, 3, "Three")
Value.Four = Value(2, 4, "Four")
Value.Five = Value(3, 5, "Five")
Value.Six = Value(4, 6, "Six")
Value.Seven = Value(5, 7, "Seven")
Value.Eight = Value(6, 8, "Eight")
Value.Nine = Value(7, 9, "Nine")
Value.Ten = Value(8, 10, "Ten")
Value.Jack = Value(9, 10, "Jack")
Value.Queen = Value(10, 10, "Queen")
Value.King = Value(11, 10, "King");
Value.Ace = Value(12, 0, "Ace")
Value.Undefined = Value(-1, -1, "Unknown")

class RecognitionEngine:
	def __init__(self, useValueOnly = False):
		self.isTrained = False
		self.trainSet = []
		self.useValueOnly = useValueOnly

	def train(self, trainSetPath):
		self.isTrained = True

	def recognize(self, card):
		pass

	def cropImageToValue(self, imageData):
		return hf.cropPercentage(imageData, (VALUE_OFFSET), tuple(map(operator.add, VALUE_SIZE, VALUE_OFFSET)))

class SIFTRecognitionEngine(RecognitionEngine):

	class SiftCard:
		def __init__(self, imageData, value):
			self.keypoints, self.descriptor = SIFT.detectAndCompute(imageData, None)
			self.value = value

	def train(self, trainSetPath):
		path = os.path.join(os.getcwd(), trainSetPath)
		cardPaths = os.listdir(path)
		for cardFile in cardPaths:
			cardImage = cv2.imread(os.path.join(path, cardFile), 0)
			if self.useValueOnly:
				cardImage = self.cropImageToValue(cardImage)

			self.trainSet.append(SIFTRecognitionEngine.SiftCard(cardImage, Value.getValueFromName(cardFile)))

	def recognize(self, card):
		imageData = card.image
		if self.useValueOnly:
			imageData = self.cropImageToValue(imageData)

		card.keypoints, card.descriptor = SIFT.detectAndCompute(imageData, None)
		matcher = cv2.BFMatcher()
		bestNumGoodMatches = 0
		bestMatch = None
		bestDistance = maxint

		for sampleCard in self.trainSet:
			summaryDistance = 0

			matches = matcher.match(card.descriptor, sampleCard.descriptor)
			matches = sorted(matches, key = lambda x:x.distance)

			for m in matches:
				summaryDistance += int(m.distance)

			if(len(matches) > 0 and (summaryDistance / len(matches)) < bestDistance):
				bestMatch = sampleCard
				bestDistance = summaryDistance / len(matches)

		#if everything fails we may never matched
		#this could happen if a blank space gets detected as a card and
		#sift cant find any keypoints
		if bestMatch is not None:
			card.value = bestMatch.value
			return True

		return False

class EigenRecognitionEngine(RecognitionEngine):

	class EigenCard:
		def __init__(self, imageData, value):
			self.numpyImage = hf.cvImageToNumpy(imageData)
			self.value = value

	def train(self, trainSetPath):
		path = os.path.join(os.getcwd(), trainSetPath)
		cardPaths = os.listdir(path)
		self.trainSet = []
		for cardFile in cardPaths:
			cardImage = cv2.imread(os.path.join(path, cardFile), 0)
			if self.useValueOnly:
				cardImage = self.cropImageToValue(cardImage)
			self.trainSet.append(EigenRecognitionEngine.EigenCard(cardImage, Value.getValueFromName(cardFile)))
	
		images = [card.numpyImage for card in self.trainSet]

		self.avgImage = ev.calculateAverageImg(np.copy(images))
		normedArrayOfFaces = ev.removeAverageImage(np.copy(images), self.avgImage)
		self.eigenspace = ev.calculateEigenfaces(normedArrayOfFaces.T, len(images[0]), len(images))

		self.transposedImages = [ev.transformToEigenfaceSpace(self.eigenspace, face, ev.NUMFEATURES) for face in normedArrayOfFaces]

		for card in self.trainSet:
			card.avgImage = card.numpyImage - self.avgImage
			card.transposedImg = ev.transformToEigenfaceSpace(self.eigenspace, self.avgImage, ev.NUMFEATURES)

	def recognize(self, card):
		imageData = card.image
		if self.useValueOnly:
			imageData = self.cropImageToValue(imageData)
		numpyCardImage = hf.cvImageToNumpy(imageData);
		numpyCardImage -= self.avgImage
		transposedImg = ev.transformToEigenfaceSpace(self.eigenspace, numpyCardImage, ev.NUMFEATURES)
		matchIndex, distance = ev.calculateDistance(self.transposedImages, transposedImg)
		
		card.value = self.trainSet[matchIndex].value

		return True

class BinaryRecognitionEngine(RecognitionEngine):

	class BinaryCard:
		def __init__(self, imageData, value):
			self.imageData = imageData
			self.value = value

	def train(self, trainSetPath):
		path = os.path.join(os.getcwd(), trainSetPath)
		cardPaths = os.listdir(path)
		self.trainSet = []
		for cardFile in cardPaths:
			cardImage = cv2.imread(os.path.join(path, cardFile), 0)
			if self.useValueOnly:
				cardImage = self.cropImageToValue(cardImage)

			cardImage = self.preprocess(cardImage)
			self.trainSet.append(BinaryRecognitionEngine.BinaryCard(cardImage, Value.getValueFromName(cardFile)))

	def recognize(self, card):
		imageData = card.image
		if self.useValueOnly:
			imageData = self.cropImageToValue(imageData)

		imageData = self.preprocess(imageData)
		bestMatch = sorted(self.trainSet, key=lambda x:self.imgdiff(x.imageData, imageData))[0]


		imageData = cv2.GaussianBlur(imageData,(5,5),5)
		bestMatch.imageData = cv2.GaussianBlur(bestMatch.imageData,(5,5),5)    
		diff = cv2.absdiff(imageData,bestMatch.imageData)  
		diff = cv2.GaussianBlur(diff,(5,5),5)    
		flag, diff = cv2.threshold(diff, 200, 255, cv2.THRESH_BINARY)
		cv2.startWindowThread()
		cv2.namedWindow("Difference Image")
		cv2.imshow("Difference Image", diff)
		cv2.waitKey(1)

		card.value = bestMatch.value
		return True

	def preprocess(self, img):
		blur = cv2.GaussianBlur(img,(5,5),6 )
		thresh, o = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)#.adaptiveThreshold(blur,255,1,1,5,1)
		return o
		
	def imgdiff(self, img1, img2):
		diff = cv2.absdiff(img1,img2)  
		diff = cv2.GaussianBlur(diff,(5,5),5)    
		flag, diff = cv2.threshold(diff, 200, 255, cv2.THRESH_BINARY)
		return np.sum(diff)  


