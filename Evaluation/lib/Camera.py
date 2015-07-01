import cv2
import CardDetection as cd

useNAO = True

if useNAO:
	import NAOConnector
else:
	captureDevice = cv2.VideoCapture(0)

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

def getFrame():
	frame = None
	if useNAO:
		frame = NAOConnector.getNAO().getCameraImage()
	else:
		ret, frame = captureDevice.read()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	return frame