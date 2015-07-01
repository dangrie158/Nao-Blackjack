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
	else:
		NAO.playLoseAnimation()
	sleep(2)
	NAO.sitdown()
	game.newDeck()
	game.resetGameState()
	NAO.sayMessage("Time for another round.")


if __name__ == '__main__':
	
	NAOTouchListener = NAOListener.startNAOListener("192.168.0.105", 9559)
	NAOTouchListener.setConnector(NAO)
	naoInitialized = NAO.setup()
	if naoInitialized == True:
		NAO.sayMessage("Hello stupid human being!")
		NAO.sayMessage("Push my huge head to start a game!")
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
				decision = game.playerDoMove()
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
					game.newDeck()
					NAO.sitdown()
					sleep(2)
					game.newDeck()
					game.resetGameState()
					NAO.sayMessage("Time for another round.")
			NAO.untouch()

		#print game.getWinner()
		if cv2.waitKey(20) & 0xFF == ord('q'):
			break