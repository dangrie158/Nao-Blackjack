import cv2
from math import ceil
import numpy as np
import CardDetection as cd
import HelperFunctions as hf

#TRAINSET = "trainingsset/"
DRAW_ONLY_VALUES = False
cap = cv2.VideoCapture(0)

# Draws given bounding boxes onto a image
def drawBoundingBoxes(frame, rect):
	for r in rect:
		p1, p2 = hf.getBoundingBox(r)
		cv2.rectangle(frame, p1, p2, (0,0,255), 3)

# Show Thumbnails of detected cards
def drawCardThumbnails(windowTitle, cards, cardWidth = 70, cardHeight = 100, margin = 20, epsilon = 10, cardPerRow = 5.0):
	i, y = [0, 0]
	cardCount = len(cards)
	if cardCount > 0:
		tableWidth  = cardPerRow * (cardWidth + margin)
		tableHeight = (ceil(cardCount / cardPerRow)) * (cardHeight + margin)
		table = np.zeros((tableHeight, tableWidth), dtype = np.uint8)
		for card in cards:
			# sanity check for missformed images
			if (card.shape[0] > epsilon) and (card.shape[1] > epsilon):
				cardThumbnail = cv2.resize(card, (cardWidth, cardHeight))
				if DRAW_ONLY_VALUES:
					cardThumbnail = cropPercentage(cardThumbnail)
				if i*(cardWidth + margin) + cardThumbnail.shape[1] > table.shape[1]:
					y = y + 1
					i = 0
				table[y*(cardHeight+margin):y*(cardHeight+margin)+cardThumbnail.shape[0], i*(cardWidth+margin):i*(cardWidth+margin)+cardThumbnail.shape[1]] = cardThumbnail
				i = i + 1
		cv2.imshow(windowTitle, table)


# main execution method
if __name__ == '__main__':

	while(True):
	    # Capture frame-by-frame
	    ret, frame = cap.read()
	    images, positions = cd.getCards(frame)
	    drawCardThumbnails("Detected Cards", images)
	    drawBoundingBoxes(frame, positions)
	    cv2.imshow("Table", frame)
	  
	    if cv2.waitKey(1) & 0xFF == ord('q'):
	        break