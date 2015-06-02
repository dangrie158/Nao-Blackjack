class Player:
	def __init__(self):
		self.cards = []

	def addCard(self, card):
		if type(card) is list:
			for c in card:
				self.cards.append(c)
		else:
			self.cards.append(card)


	def reset(self):
		self.cards = []