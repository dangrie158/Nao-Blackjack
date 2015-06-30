import cv2
import HelperFunctions as hf
from Card import Card

MAX_NUMCARDS = 15

def loadCards(path):
	cardPaths = os.listdir(path)
	trainset = {}
	for card in cardPaths:
		cardImage = cv2.imread(os.path.join(hf.TRAINSET, card), flags=cv2.CV_LOAD_IMAGE_GRAYSCALE)
		trainset[card] = cardImage
	return trainset

# Returns contours of a Image
def getContours(im):
	contours, hierarchy = cv2.findContours(im,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea,reverse=True)[:MAX_NUMCARDS * 2]
	return contours

def getCards(frame, minArea=150):
	cards = []
	#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = frame
	edges = cv2.Canny(gray,100,200)
	contours = getContours(edges)
	for c in contours:
		rect = hf.rectify(c)
		if rect is not None and cv2.contourArea(c) >= minArea:
			cardImg = hf.imageRerverseProjection(rect, gray)
			cardCandidate = Card(cardImg, rect)
			#detect possible duplicates of the detected card already in the list
			if not any(cardCandidate.overlaps(card) for card in cards):
				cards.append(cardCandidate)
	return cards