import cv2
import numpy as np
from math import ceil
import os
import sys
import HelperFunctions as hf
from RecognitionEngine import Value

FONT = cv2.FONT_HERSHEY_SIMPLEX

class VirtualTable:
	def __init__(self, title):
		self.title = title

	def setPlayer1(self, player):
		self.player1 = player

	def setPlayer2(self, player):
		self.player2 = player

	#render a set of cards on a given start position in the frame
	def renderCards(self, frame, cards, start, margin, cardWidth, cardHeight):
		dx, dy = [0, 0]

		#writePath = os.path.join(os.getcwd(), hf.TRAINSET)

		for card in cards:
			
			cardThumbnail = card.getThumbnail((cardWidth, cardHeight))
			#cardThumbnail = card.getValueImage()

			#convert thumbnail back to RGB
			cardThumbnail = cv2.cvtColor(cardThumbnail, cv2.COLOR_GRAY2RGB)

			cardText = card.value.name
			
			#check where (x) the new card should go
			nextX = start[0] + dx * (cardWidth + margin)
			nextY = start[1] + dy * (cardHeight + margin)

			#check if we overflowed and break the line if so
			if nextX + cardThumbnail.shape[1]> frame.shape[1]:
				dy = dy + 1
				dx = 0
				nextX = start[0] + dx * (cardWidth + margin)
				nextY = start[1] + dy * (cardHeight+margin)

			frame[nextY:nextY+cardThumbnail.shape[0], nextX:nextX+cardThumbnail.shape[1]] = cardThumbnail
			color = (0,255,0) if card.value != Value.Undefined else (255,0,0)
			cv2.putText(frame, cardText, (int(nextX),int(nextY + cardThumbnail.shape[0])), FONT, 0.6, color, 1, cv2.CV_AA)
			dx = dx + 1

	def render(self, cardWidth = 70, cardHeight = 100, margin = 20, playerMargin = 50, cardPerRow = 5.0):
		
		#calculate needed height of the table to fit all cards
		player1heightOnTable = (ceil(len(self.player1.cards) / cardPerRow)) * (cardHeight + margin)
		player2heightOnTable = (ceil(len(self.player2.cards) / cardPerRow)) * (cardHeight + margin)
		frameWidth  = cardPerRow * (cardWidth + margin)
		frameHeight = player1heightOnTable + playerMargin + player2heightOnTable


		frame = np.zeros((frameHeight, frameWidth), dtype = np.uint8)
		frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
		
		self.renderCards(frame, self.player1.cards, (0, 0), margin, cardWidth, cardHeight)
		dividerY = int(player1heightOnTable + playerMargin / 2)
		cv2.line(frame, (0, dividerY), (int(frameWidth), dividerY), (255, 255, 255))
		self.renderCards(frame, self.player2.cards, (0, player1heightOnTable + playerMargin), margin, cardWidth, cardHeight)
		
		cv2.imshow(self.title, frame)
		frame.fill(0)