from Card import Value
import random
class CardDeck:

	def __init__(self):
		self.cards = [	Value.Two, Value.Two, Value.Two, Value.Two,
						Value.Three, Value.Three, Value.Three, Value.Three, 
						Value.Four, Value.Four, Value.Four, Value.Four,
						Value.Five, Value.Five, Value.Five, Value.Five,
						Value.Six, Value.Six, Value.Six, Value.Six,
						Value.Seven, Value.Seven, Value.Seven, Value.Seven,
						Value.Eight, Value.Eight, Value.Eight, Value.Eight,
						Value.Nine, Value.Nine, Value.Nine, Value.Nine,
						Value.Ten, Value.Ten, Value.Ten, Value.Ten,
						Value.Jack, Value.Jack, Value.Jack, Value.Jack,
						Value.Queen, Value.Queen, Value.Queen, Value.Queen,
						Value.King, Value.King, Value.King, Value.King,
						Value.Ace, Value.Ace, Value.Ace, Value.Ace
					]

	def shuffle(self):
		random.shuffle(self.cards)

	def pick(self):
		return self.cards.pop()