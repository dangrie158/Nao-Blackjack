from lib.Player import Player
from lib.Game import Game
import cv2

if __name__ == '__main__':
	nao = Player()
	bank = Player()
	game = Game(nao, bank)

	#start clean
	game.newDeck()
	while True:
		print game.playerDoMove()

		#print game.getWinner()
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break