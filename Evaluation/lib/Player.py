import Card

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

	def getHandValue(self):
		value = 0
			#first sum up everything except the aces
		for card in self.cards:
			if card.value != Card.Value.Ace:
				value += card.value.value
		#now do the aces and try not to get over 21
		for card in self.cards:
			if card.value == Card.Value.Ace:
				if (value + 11) > 21:
					value += 1
				else:
					value += 11
		return value

	def getCards(self):
		cards = []
		for card in self.cards:
			cards.append(card.value.value)
		return cards