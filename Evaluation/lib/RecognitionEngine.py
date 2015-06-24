import os
import cv2
from sys import maxint
from numpy import average, copy, reshape
import eigenVectorDetection as ev
import HelperFunctions as hf

SIFT = cv2.SIFT()

#very easy wrapper class to map values to
# the relative index in the case vector
class Value:
	def __init__(self, index, value, name):
		self.index = index
		self.value = value
		self.name = name

Value.Two = Value(0, 2, "Two")
Value.Three = Value(1, 3, "Three")
Value.Four = Value(2, 4, "Four")
Value.Five = Value(3, 5, "Five")
Value.Six = Value(4, 6, "Six")
Value.Seven = Value(5, 7, "Seven")
Value.Eight = Value(6, 8, "Eight")
Value.Nine = Value(7, 9, "Nine")
Value.Ten = Value(8, 10, "Ten")
Value.Jack = Value(8, 10, "Jack")
Value.Queen = Value(8, 10, "Queen")
Value.King = Value(8, 10, "King");
Value.Ace = Value(9, 0, "Ace")
Value.Undefined = Value(-1, -1, "Unknown")

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

class RecognitionEngine:
	def __init__(self):
		self.isTrained = False
		self.trainSet = []

	def train(self, trainSetPath):
		self.isTrained = True

	def recognize(self, card):
		pass

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
			self.trainSet.append(SIFTRecognitionEngine.SiftCard(cardImage, getValueFromName(cardFile)))

	def recognize(self, card):
		card.keypoints, card.descriptor = SIFT.detectAndCompute(card.image, None)
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

		def calculateEigenFace(self, eigenspace):
			self.transposedImg = ev.transformToEigenfaceSpace(eigenspace, self.avgImage, ev.NUMFEATURES)

	def train(self, trainSetPath):
		path = os.path.join(os.getcwd(), trainSetPath)
		cardPaths = os.listdir(path)
		self.trainSet = []
		for cardFile in cardPaths:
			cardImage = cv2.imread(os.path.join(path, cardFile), 0)
			self.trainSet.append(EigenRecognitionEngine.EigenCard(cardImage, getValueFromName(cardFile)))
	
		images = [card.numpyImage for card in self.trainSet]

		self.avgImage = ev.calculateAverageImg(copy(images))
		normedArrayOfFaces = ev.removeAverageImage(copy(images), self.avgImage)
		self.eigenspace = ev.calculateEigenfaces(normedArrayOfFaces.T, len(images[0]), len(images))

		self.transposedImages = [ev.transformToEigenfaceSpace(self.eigenspace, face, ev.NUMFEATURES) for face in normedArrayOfFaces]

		for card in self.trainSet:
			card.avgImage = card.numpyImage - self.avgImage
			card.calculateEigenFace(self.eigenspace)

	def recognize(self, card):
		numpyCardImage = hf.cvImageToNumpy(card.image);
		numpyCardImage -= self.avgImage
		transposedImg = ev.transformToEigenfaceSpace(self.eigenspace, numpyCardImage, ev.NUMFEATURES)
		matchIndex, distance = ev.calculateDistance(self.transposedImages, transposedImg)
		
		card.value = self.trainSet[matchIndex].value

		return True
