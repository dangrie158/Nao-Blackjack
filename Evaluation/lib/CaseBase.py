class CaseBase:
	persistAfter = 10000
	def __init__(self):
		self.cases = []

	def putCase(self, case):
		self.cases.append(case)
		if(len(self.cases) > pasistAfter):
			pass # TODO: persist casebase to file

	def getClosestCase(self, case):
		for case in self.cases:
			pass #TODO: add logic to get minimal distance

	@staticmethod
	def createCase(deck, player, bank):
		case = [0] * 30

		for card in deck.cards:
			case[card] += 1

		for card in player.cards:
			case[card + 10] += 1

		for card in bank.cards:
			case[card + 20] += 1

		return case