from lib.CardDeck import CardDeck
from lib.Card import Value
from lib.Player import Player
from lib.CaseBase import CaseBase
from lib.CaseBase import Action
import lib.HelperFunctions as Helper

MAX_DISTANCE = 1.5 #TODO check value after a measure of distance is set

bank = Player()
player = Player()

winBase = CaseBase("Win_Base")
lossBase = CaseBase("Loss_Base")

def performAction(action, player, deck):
	if action == Action.Hit:
		player.addCard(deck.pick())
	elif action == Action.Stay:
		pass #do nothing
	else:
		raise Exception('invalid action passed' + str(action))

def getRandomActionForCase(case):
	return True, Action.getRandomAction()

def getBestActionForCase(case):

	#get the best matches from each base
	winDistance, winCase = winBase.getClosestCase(case)
	lossDistance, lossCase = lossBase.getClosestCase(case)

	#check if either base has a case close enough to consider
	if winDistance > MAX_DISTANCE and lossDistance > MAX_DISTANCE:
		return True, Action.getRandomAction()

	#use the better case as  a base for our decision
	if winDistance > lossDistance:
		#last time we won after doing winCase.action in 
		#a similar situation. do it again
		return False, winCase.action
	else:
		#last time we lost doing this in a similar situation,
		#do anyting except what we did last time
		randomAction = None
		while True:
			randomAction = Action.getRandomAction()
			if randomAction != lossCase.action:
				return True, randomAction
	raise Exception("Invalid Action returned")

deck = CardDeck()
deck.shuffle()
lostGames = 1
wonGames = 1
playedGames = 0
printGames = 1
MAX_GAMES = 100000

winBase = Helper.readCasesFromStruct("Win_Base")
lostBase = Helper.readCasesFromStruct("Loss_Base")
print("Loading files finished.")

while True:

	if(deck.amount() < 14):
		deck = CardDeck()
		deck.shuffle()

	#the bank gets the first card of the deck
	bank.addCard(deck.pick())

	#after this, each player gets 2 cards
	player.addCard(deck.pick())
	player.addCard(deck.pick())

	casesInThisGame = []


	#crate a case to compare with others (from the players view)
	currentCase = CaseBase.createCase(deck, player, bank)

	#get the best action for the case and
	#save the performed action to the case
	isRandom = False
	if playedGames < MAX_GAMES:
		isRandom, currentCase.action = getRandomActionForCase(currentCase)
	else:
		isRandom, currentCase.action = getBestActionForCase(currentCase)
	
	#save the case in an temporary array, because 
	#we can't know yet if we need to put it in the
	#winbase or lossbase. but onyl append random bases, or we 
	#end up with a lot of duplicates in the base 
	if isRandom:
		casesInThisGame.append(currentCase)

	while currentCase.action != Action.Stay:
		performAction(currentCase.action, player, deck)
		
		#create a new case for the new situation
		currentCase = CaseBase.createCase(deck, player, bank)

		isfixedValue = False
		isRandom = False
		if player.getHandValue() >= 21:
			currentCase.action = Action.Stay
			isfixedValue = True
		else:
			if playedGames < MAX_GAMES:
				isRandom, currentCase.action = getRandomActionForCase(currentCase)
			else:
				isRandom, currentCase.action = getBestActionForCase(currentCase)
		if isRandom or isfixedValue:
			casesInThisGame.append(currentCase)

	
	#after all players have drawn their cards, the bank
	#draws its second card.
	bank.addCard(deck.pick())

	#if the bank has 16 or less, it has to pick another card
	while bank.getHandValue() <= 16:
		bank.addCard(deck.pick())

	#print "bankvalue " + str(bank.getHandValue())
	#print "ownvalue " + str(player.getHandValue())

	#check if we lost
	if player.getHandValue() > 21 or (bank.getHandValue() <= 21 and bank.getHandValue() > player.getHandValue()):
		[lossBase.putCase(case) for case in casesInThisGame]
		if playedGames % printGames == 0 and playedGames > MAX_GAMES:
			lostGames+=1
			print "Lost! Bank Value: " + str(bank.getHandValue()) + ", Player Value: " + str(player.getCards()) + " / " + str(player.getHandValue()) + ", Win to Lost: " + str(wonGames  * 1.0 / lostGames)		
	#or won
	else:
		[winBase.putCase(case) for case in casesInThisGame]
		if playedGames % printGames == 0 and playedGames > MAX_GAMES:
			wonGames+=1
			print "Win! Bank Value: " + str(bank.getHandValue()) + ", Player Value: " + str(player.getCards()) + " / " + str(player.getHandValue()) + ", Win to Lost: " + str(wonGames  * 1.0 / lostGames)

	#print "-"*30

	playedGames += 1
	bank.reset()
	player.reset()
