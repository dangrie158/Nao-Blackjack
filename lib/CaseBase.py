import random
import HelperFunctions as Helper
from sys import maxint
from math import ceil
from scipy import spatial

class Case:
	def __init__(self, vector, action = None):
		self.vector = vector
		self.action = action

class Action:
	Hit = 0
	Stay = 1

	@staticmethod
	def getRandomAction():
		rnd = ceil(random.random() * 2)
		if rnd == 1:
			return Action.Hit
		elif rnd == 2:
			return Action.Stay


class CaseBase:
	PERSIST_AFTER = 1000
	def __init__(self, name):
		self.cases = []
		self.name = name
		self.inpersistentCases = []

	def putCase(self, case):
		self.cases.append(case)
		self.inpersistentCases.append(case)
		if len(self.inpersistentCases) >= CaseBase.PERSIST_AFTER:
			Helper.packCasesToStruct(self.inpersistentCases, self.name)
			self.inpersistentCases = []
			print str(len(self.cases))  + " Games in " + self.name

	def getClosestCase(self, case):
		nearestCase = Case([0] * 30, Action.Stay)
		caseDistance = maxint
		for compareCase in self.cases:
			distance = self.getCosineDistance(compareCase.vector, case.vector)
			#print("Distance: " + str(distance))
			if distance < caseDistance:
				nearestCase = compareCase
				caseDistance = distance
		return caseDistance, nearestCase

	def getOwnEuclidDistance(self, case1, case2):
		sum = 0.0;
		for i in range(len(case1.vector)):
			sum += (case1.vector[i] - case2.vector[i])**2
		return math.sqrt(sum)

	def getEuclidDistance(self, case1, case2):
		return spatial.distance.euclidean(case1, case2)

	def getCosineDistance(self, case1, case2):
		return spatial.distance.cosine(case1, case2)

	@staticmethod
	def createCase(deck, player, bank):
		caseVector = [0] * 30

		for card in deck.cards:
			caseVector[card.value.index] += 1

		for card in player.cards:
			caseVector[card.value.index + 10] += 1

		for card in bank.cards:
			caseVector[card.value.index + 20] += 1

		return Case(caseVector)