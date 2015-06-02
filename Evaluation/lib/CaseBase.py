import random
from math import ceil

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
	def __init__(self):
		self.cases = []

	def putCase(self, case):
		self.cases.append(case)
		if(len(self.cases) % CaseBase.PERSIST_AFTER) == 0:
			print str(len(self.cases))  + " Games" # TODO: persist casebase to file

	def getClosestCase(self, case):
		for case in self.cases:
			pass #TODO: add logic to get minimal distance

		return 0.0, Case([0] * 30, Action.Stay)

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