from CardDeck import CardDeck
from RecognitionEngine import Value
from Player import Player
from VirtualTable import VirtualTable
import CardDetection as cd
import cv2
import Camera

RISK_TAKING_PROPENSITY = 0.5

class Game:
	def __init__(self, player, bank):
		self.player = player
		self.bank = bank
		self.table = VirtualTable("Game Table")
		self.table.setPlayer1(player)
		self.table.setPlayer2(bank)

	def newDeck(self):
		self.deck = CardDeck()

	def resetGameState(self):
		self.player.reset()
		self.bank.reset()

	def playerDoMove(self):
		newCards, frame = Game.recognizeCards()

		Camera.drawBoundingBoxes(frame, newCards)
		Camera.drawCenteroids(frame, newCards)
		Camera.drawCenter(frame)
		cv2.imshow("LatestFrame", frame)

		print "Recognized Cards: " + str(len(newCards))

		centerY = frame.shape[0] / 2
		Game.divideOutCards(newCards, self.player, self.bank, centerY)
		self.table.render()

		playerNewValue = self.player.getHandValue()
		print "Player Hand Value is now: " + str(playerNewValue)
		if playerNewValue > 21:
			self.resetGameState();
			print "Bank has won, player was over 21"
			return self.bank
		elif playerNewValue == 21:
			self.resetGameState();
			print "Player has won, that was a Blackjack (=21)"
			return self.player

		tempDeck = self.deck.getCopy()
		for card in newCards:
			tempDeck.pick(card.value)

		decision = False

		if tempDeck.bustPropability(self.player) < RISK_TAKING_PROPENSITY:
			decision = True

		print "Propability to win: " + str(tempDeck.bustPropability(self.player)) + ", Taking risk until: " + str(RISK_TAKING_PROPENSITY) + ", Decision => " + str(decision)

		self.resetGameState();

		return decision


	def getWinner(self):
		cards, frame = Game.recognizeCards()

		centerY = frame.shape[0] / 2
		Game.divideOutCards(cards, self.player, self.bank, centerY)
		self.table.render()

		#remove the final cards from the actual deck to save the state for next games
		for card in cards:
			self.deck.pick(card.value)

		#decide who won
		playerHandValue = self.player.getHandValue();
		bankHandValue = self.bank.getHandValue();
		if playerHandValue > 21:
			return self.bank #we lost, bevause we got bust
		elif bankHandValue > 21:
			return self.player #we won, because the bank got bust
		elif playerHandValue == 21:
			return self.player #we won, winner winner chicken dinner
		elif playerHandValue > bankHandValue:
			return self.player # close, but we won
		else:
			return self.bank # damn

	@staticmethod
	def recognizeCards(numCycles = 10):
		recognitionVector = []

		#this is a 2 step process, first capture 10 frames
		#and ensure that all recognized cards are always in the same order.
		#then get the match that happend most.
		frame = None
		for cycle in range(numCycles):
			frame = Camera.getFrame()
			cards = cd.getCards(frame)

			if(len(recognitionVector) > 0):
				orderedCards = [None] * len(recognitionVector[0])
				#sort the cards in the same 
				#order as they were in first vector
				for i, oldCard in enumerate(recognitionVector[0]):
					for currentCard in cards:
						if currentCard.overlaps(oldCard):
							orderedCards[i] = currentCard

				recognitionVector.append(orderedCards)
			else:
				recognitionVector.append(cards)
		#count the card indices for each card
		cardCounts = []
		for i in range(len(recognitionVector[0])):
			cardCounts.append([0] * 13)

		for cycle in recognitionVector:
			for cardNum, card in enumerate(cycle):
				if card is not None and card.value != Value.Undefined:
					cardCounts[cardNum][card.value.index] += 1

		#finally put together an array containing only the 
		#max recognized values

		for cardNum, cardCount in enumerate(cardCounts):
			maxValue = cardCount.index(max(cardCount))
			recognitionVector[0][cardNum].value = Value.getValueFromIndex(maxValue)

		result = "Recognized: "
		for card in recognitionVector[0]:
			result += str(card.value.value) + " / "
		print result
		
		return recognitionVector[0], frame


	@staticmethod
	def divideOutCards(cards, player1, player2, threshold):
		for card in cards:
			if card.getCenteroidInFrame()[1] > threshold:
				player1.addCard(card)
			else:
				player2.addCard(card)