import cv2
import CardDetection as cd
import HelperFunctions as hf
from VirtualTable import VirtualTable
from Player import Player

#TRAINSET = "trainingsset/"
DRAW_ONLY_VALUES = False
cap = cv2.VideoCapture(1)

# Draws given bounding boxes onto a image
def drawBoundingBoxes(frame, cards):
	for card in cards:
		p1, p2 = hf.boundingBox(card.getBoundingBox())
		cv2.rectangle(frame, p1, p2, (0,0,255), 3)

def drawCenteroids(frame, cards):
	for card in cards:
		cv2.circle(frame, card.getCenteroidInFrame(), 10, (0,255,0))

def drawCenter(frame):
	p1 = (0, frame.shape[0] / 2)
	p2 = (frame.shape[1], frame.shape[0] / 2)
	cv2.line(frame, p1, p2, (255,0,255))

def divideOutCards(cards, player1, player2, threshold):
	for card in cards:
		if card.getCenteroidInFrame()[1] < centerY:
			player1.addCard(cards)
		else:
			player2.addCard(cards)

# main execution method
if __name__ == '__main__':

	table = VirtualTable("Game Table")
	player1 = Player()
	player2 = Player()
	
	table.setPlayer1(player1)
	table.setPlayer2(player2)

	while(True):
	    # Capture frame-by-frame
	    ret, frame = cap.read()
	    cards = cd.getCards(frame)
	    centerY = frame.shape[0] / 2

	    divideOutCards(cards, player1, player2, centerY)

	    table.render()

	    drawBoundingBoxes(frame, cards)
	    drawCenteroids(frame, cards)
	    drawCenter(frame)
	    cv2.imshow("Capture", frame)

	    player1.reset()
	    player2.reset()
	  
	    if cv2.waitKey(1) & 0xFF == ord('q'):
	        break