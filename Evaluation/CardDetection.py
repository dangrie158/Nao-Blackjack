import cv2
import numpy as np
import tkSimpleDialog
import os
import math
import sys

TRAINSET = "trainingsset/"
MAX_NUMCARDS = 15
DRAW_ONLY_VALUES = False

cap = cv2.VideoCapture(0)

# load and preprocess methods for trainingsdata
def loadCards(path):
	cardPaths = os.listdir(path)
	trainset = {}
	for card in cardPaths:
		cardImage = cv2.imread(os.path.join(TRAINSET, card), flags=cv2.CV_LOAD_IMAGE_GRAYSCALE)
		trainset[card] = cardImage
	return trainset

# returns direct nearest difference image on given trainingsset
def returnDirectDiffImage(trainingSet, img):
	return sorted(trainingSet.values(), key=lambda x:imgdiff(x,img))[0]

# calculates differences between two images
def imgdiff(img1,img2):
	diff = cv2.absdiff(img1,img2)    
	return np.sum(diff)  

#
# image processing functions
#

# transform a contour to a rectangle
def rectify(contour):
	peri = cv2.arcLength(contour,True)
	if peri > 300:
		poly = cv2.approxPolyDP(contour,0.02*peri,True)
		try:
			poly = poly.reshape((4,2))
		except:
			return None
	else:
		return None
	hnew = np.zeros((4,2),dtype = np.float32)
	add = poly.sum(1)
	hnew[0] = poly[np.argmin(add)]
	hnew[2] = poly[np.argmax(add)]
	diff = np.diff(poly,axis = 1)
	hnew[1] = poly[np.argmin(diff)]
	hnew[3] = poly[np.argmax(diff)]
	return hnew

# returns the euclidian Distance between two 2D points
def euclidDist(p1, p2):
	return math.sqrt(math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2))

# Crops a given card to fit in a given rectangle
def cropCard(rectangle, im):  
	newRect = np.array([ [0,0],[449,0],[449,449],[0,449] ],np.float32)

	transform = cv2.getPerspectiveTransform(rectangle, newRect)
	warp = cv2.warpPerspective(im,transform,(450,450))
	# Rotate if necessary
	if euclidDist(rectangle[0], rectangle[1]) > euclidDist(rectangle[1], rectangle[2]):
		warp = rotateCard(warp, 450)
	return warp

# Crops a given card to a given percentage
def cropPercentage(im, percent = 18):
	xSize = im.shape[0]
	ySize = im.shape[0]
	return im[0:(xSize/100*percent), 0:(ySize/100*percent)]

# Rotate a given Image
def rotateCard(im, imSize, angle = 90):
	shape = (imSize, imSize)
	rotMat = cv2.getRotationMatrix2D((imSize / 2, imSize / 2), angle, 1.0)
	result = cv2.warpAffine(im, rotMat, shape, flags=cv2.INTER_LINEAR)
	return result
 
# Returns contours of a Image
def getContours(im):
	contours, hierarchy = cv2.findContours(im,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea,reverse=True)[:MAX_NUMCARDS * 2]
	return contours

# Returns the bounding box of a rectangle
def getBoundingBox(rect):
	xMin, yMin, = [sys.maxint, sys.maxint]
	xMax, yMax = [0, 0]
	for p in rect:
		if p[0] < xMin: xMin = p[0]
		if p[1] < yMin: yMin = p[1]
		if p[0] > xMax: xMax = p[0]
		if p[1] > yMax: yMax = p[1]
	p1 = (xMin, yMin)
	p2 = (xMax, yMax)
	return p1, p2

# Draws given bounding boxes onto a image
def drawBoundingBoxes(frame, rect):
	for r in rect:
		p1, p2 = getBoundingBox(r)
		cv2.rectangle(frame, p1, p2, (0,0,255), 3)

# Show Thumbnails of detected cards
def drawCardThumbnails(windowTitle, cards, cardWidth = 70, cardHeight = 100, margin = 20, epsilon = 10, cardPerRow = 5.0):
	i, y = [0, 0]
	cardCount = len(cards)
	if cardCount > 0:
		tableWidth  = cardPerRow * (cardWidth + margin)
		tableHeight = (math.ceil(cardCount / cardPerRow)) * (cardHeight + margin)
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

	trainSet = loadCards(TRAINSET)

	while(True):
	    # Capture frame-by-frame
	    ret, frame = cap.read()
	    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	    # Canny based edge detection
	    edges = cv2.Canny(gray,100,200)
	    # Uncomment this to show the canny edge detection image:
	    #cv2.imshow("canny", edges)

	    # Calculate Contours on canny edge detected image
	    contours = getContours(edges)
	    cv2.drawContours(frame, contours, -1, (255,0,0), 1)

	    cardImages = []
	    detectedImages = []
	    imagePositions = []

	    for c in contours:
	    	rect = rectify(c)
	    	if rect is not None:
	    		cardImg = cropCard(rect, gray)
	    		imagePositions.append(rect)
	    		cardImages.append(cardImg)
	    		detectImg = returnDirectDiffImage(trainSet, cardImg)
	    		detectedImages.append(detectImg)

	    drawBoundingBoxes(frame, imagePositions)
	    cv2.imshow("Table", frame)

	    drawCardThumbnails("Detected Cards", cardImages)
	    drawCardThumbnails("Training Cards", detectedImages)
	  
	    if cv2.waitKey(1) & 0xFF == ord('q'):
	        break
