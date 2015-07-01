from Card import Card
from RecognitionEngine import Value
import random
class CardDeck:

	def __init__(self, cards = None):
		if cards is None:
			self.cards = [	Card(None,  None, Value.Two), Card(None, None, Value.Two), Card(None, None, Value.Two), Card(None, None, Value.Two),
						Card(None, None, Value.Three), Card(None, None, Value.Three), Card(None, None, Value.Three), Card(None, None, Value.Three), 
						Card(None, None, Value.Four), Card(None, None, Value.Four), Card(None, None, Value.Four), Card(None, None, Value.Four),
						Card(None, None, Value.Five), Card(None, None, Value.Five), Card(None, None, Value.Five), Card(None, None, Value.Five),
						Card(None, None, Value.Six), Card(None, None, Value.Six), Card(None, None, Value.Six), Card(None, None, Value.Six),
						Card(None, None, Value.Seven), Card(None, None, Value.Seven), Card(None, None, Value.Seven), Card(None, None, Value.Seven),
						Card(None, None, Value.Eight), Card(None, None, Value.Eight), Card(None, None, Value.Eight), Card(None, None, Value.Eight),
						Card(None, None, Value.Nine), Card(None, None, Value.Nine), Card(None, None, Value.Nine), Card(None, None, Value.Nine),
						Card(None, None, Value.Ten), Card(None, None, Value.Ten), Card(None, None, Value.Ten), Card(None, None, Value.Ten),
						Card(None, None, Value.Jack), Card(None, None, Value.Jack), Card(None, None, Value.Jack), Card(None, None, Value.Jack),
						Card(None, None, Value.Queen), Card(None, None, Value.Queen), Card(None, None, Value.Queen), Card(None, None, Value.Queen),
						Card(None, None, Value.King), Card(None, None, Value.King), Card(None, None, Value.King), Card(None, None, Value.King),
						Card(None, None, Value.Ace), Card(None, None, Value.Ace), Card(None, None, Value.Ace), Card(None, None, Value.Ace)
					]
		else:
			self.cards = cards

	def shuffle(self):
		random.shuffle(self.cards)

	def pick(self, value = None):
		if value is not None:
			for cardIndex, card in enumerate(self.cards):
				if card.value.index == value.index:
					return self.cards.pop(cardIndex)
		else:
			return self.cards.pop()

	def amount(self):
		return len(self.cards)

	def getCopy(self):
		return CardDeck(list(self.cards))

	def bustPropability(self, player):
		cardsToGetBust = 0.0
		for card in self.cards:
			copy = player.getCopy()
			copy.addCard(card)
			if copy.getHandValue() > 21:
				cardsToGetBust += 1
		#print "Cards to get bust are: " + str(cardsToGetBust) + " by cards in Deck: " + str(self.amount())
		return cardsToGetBust / self.amount()