from Card import Card
from Card import Value
import random
class CardDeck:

	def __init__(self):
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

	def shuffle(self):
		random.shuffle(self.cards)

	def pick(self):
		return self.cards.pop()

	def amount(self):
		return len(self.cards)

