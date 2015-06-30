from lib.Player import Player
from lib.Game import Game
import cv2
import lib.NAOConnector as NAOConnector
import lib.NAOListener as NAOListener

NAO = NAOConnector.getNAO()
nao = Player()
bank = Player()
game = Game(nao, bank)

def decideWinner():
	winner = game.getWinner()
	if winner is nao:
		NAO.sayMessage("Player won!")
	else:
		NAO.sayMessage("Bank won!")
	game.newDeck()


if __name__ == '__main__':
	
	NAOTouchListener = NAOListener.startNAOListener("192.168.0.105", 9559)
	NAOTouchListener.setConnector(NAO)
	naoInitialized = NAO.setup()
	if naoInitialized == True:
		NAO.standup()
		NAO.sayMessage("Hello!")
		NAO.sayMessage("Push my Head to start a game!")
		NAO.setJointPosition("HeadYaw" , 0.0)
		NAO.setJointPosition("HeadPitch" , 29.5)
		NAO.subscribeToCamera()

	#start clean
	game.newDeck()
	decideForWinner = False

	while True:

		if NAO.touched == True:
			
			NAO.sayMessage("You touched me!")
			if decideForWinner == True:
				decideWinner()
				decideForWinner = False
			else:
				decision = game.playerDoMove()
				if decision == True:
					NAO.sayMessage("I want another card")
				elif decision == False:
					NAO.sayMessage("Thats enough, let the bank move.")
					decideForWinner = True
				else:
					NAO.sayMessage("Please wait!")
					decideWinner()
			NAO.untouch()

		#print game.getWinner()
		if cv2.waitKey(20) & 0xFF == ord('q'):
			break