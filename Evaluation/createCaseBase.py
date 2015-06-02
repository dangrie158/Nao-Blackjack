from lib.CardDeck import CardDeck
from lib.Card import Value
from lib.Player import Player
from lib.CaseBase import CaseBase

bank = Player()
player = Player()

winBase = CaseBase()
lossBase = CaseBase()

while True:
	deck = CardDeck()
	deck.shuffle()

	player.addCard(deck.pick())
	player.addCard(deck.pick())

	bank.addCard(deck.pick())
	bank.addCard(deck.pick())

	currentCase = CaseBase.createCase(deck, player, bank)

	#check win / loss
	#while not won or lost

	winDistance, winCase = winBase.getClosestCase(currentCase)
	lossDistance, lossCase = lossBase.getClosestCase(currentCase)

	if winDistance > lossDistance:
		pass #TODO player do action from last case
	else:
		pass #TODO pass





	bank.reset()
	player.reset()