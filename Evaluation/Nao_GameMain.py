from lib.Player import Player
from lib.Game import Game
import cv2
import lib.NAOConnector as NAOConnector
import lib.NAOListener as NAOListener
from time import sleep

NAO = NAOConnector.getNAO()
nao = Player()
bank = Player()
game = Game(nao, bank)

def decideWinner():
	winner = game.getWinner()
	if winner is nao:
		NAO.playWinAnimation()
	elif winner is bank:
		NAO.playLoseAnimation()
	elif winner is None:
		NAO.playDrawAnimation()
	else:
		raise ValueError('unexpected win value')
	sleep(2)
	NAO.sitdown()
	game.resetGameState()
	NAO.sayMessage("Time for another round.")


if __name__ == '__main__':
	
	NAOTouchListener = NAOListener.startNAOListener("192.168.0.105", 9559)
	NAOTouchListener.setConnector(NAO)
	naoInitialized = NAO.setup()
	if naoInitialized == True:
		NAO.sayMessage("Lets play some Blackjack")
		NAO.sayMessage("Push my head to start a game!")
		NAO.subscribeToCamera()
		NAO.untouch()

	#start clean
	game.newDeck()
	game.resetGameState()
	decideForWinner = False

	while True:

		if NAO.touched == True:
			
			if decideForWinner == True:
				NAO.playDecideAnimation()
				decideWinner()
				decideForWinner = False
			else:
				NAO.playDecideAnimation()
				decision = game.playerDoFastMove()
				if decision == True:
					NAO.sayMessage("I want another card")
					NAO.sitdown()
					sleep(2)
				elif decision == False:
					NAO.sayMessage("Thats enough, let the bank play.")
					NAO.sitdown()
					sleep(2)
					decideForWinner = True
				else:
					if decision is nao:
						NAO.playWinAnimation()
					else:
						NAO.playLoseAnimation()
					NAO.sitdown()
					sleep(2)
					game.resetGameState()
					NAO.sayMessage("Time for another round.")
			NAO.untouch()

		#print game.getWinner()
		if cv2.waitKey(20) & 0xFF == ord('q'):
			break
		if cv2.waitKey(20) & 0xFF == ord('n'):
			game.newDeck()
			print "shuffled a new deck"
