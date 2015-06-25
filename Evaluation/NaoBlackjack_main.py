import lib.CardDetection as cd
import lib.HelperFunctions as hf
from lib.VirtualTable import VirtualTable
from lib.Player import Player
import cv2
from NAOConnector import NAO
import sys

UseNAO = True
RenderSteps = 25
DetectSteps = 1

if(UseNAO == False):
	cap = cv2.VideoCapture(0)

# Draws given bounding boxes onto a image
def drawBoundingBoxes(frame, cards):
	for card in cards:
		p1, p2 = card.getBoundingBox()
		cv2.rectangle(frame, p1, p2, (0,0,255), 3)

# Draws given bounding boxes onto a image
def drawIntersectingBoundingBoxes(frame, card1, card2):
	p1, p2 = card1.getIntersectingBoundingBox(card2)
	cv2.rectangle(frame, p1, p2, (0,255,255), 3)

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
			player1.addCard(card)
		else:
			player2.addCard(card)

# main execution method
if __name__ == '__main__':

	if(UseNAO == True):
		nao = NAO("192.168.0.105", 9559)
		naoInitialized = nao.init()
		if naoInitialized == True:
			nao.enableStandardPosture()
			nao.setJointPosition("HeadYaw" , 0.0)
			nao.setJointPosition("HeadPitch" , 29.5)
			nao.subscribeToCamera()

	table = VirtualTable("Game Table")
	player1 = Player()
	player2 = Player()
	
	table.setPlayer1(player1)
	table.setPlayer2(player2)

	rendered = 0
	detected = 0

	while(True):

		# Capture Frame by Frame with Webcam
		if(UseNAO == False):
			ret, frame = cap.read()
			cards = cd.getCards(frame)
	
			for card in cards:
				card.detectValueEigen()
	
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

		# Capture Frame by Frame with NAO
		else:
			if naoInitialized == True:

				if(rendered % RenderSteps == 0):
					NAOImage = nao.getCameraImage()
					cards = cd.getCards(NAOImage)
					centerY = NAOImage.shape[0] / 2
	
					divideOutCards(cards, player1, player2, centerY)
					table.render(80, 160, 30)
	
					drawBoundingBoxes(NAOImage, cards)
					drawCenteroids(NAOImage, cards)
					drawCenter(NAOImage)
				
				cv2.imshow("Capture", NAOImage)

				if(detected % DetectSteps == 0):
					for card in cards:
						card.detectValueSIFT(cv2.SIFT())

				if(rendered % RenderSteps == 0):
					player1.reset()
					player2.reset()

				if cv2.waitKey(1) & 0xFF == ord('q'):
					nao.unsubscribeFromCamera()
					break

		rendered += 1
		detected += 1
	