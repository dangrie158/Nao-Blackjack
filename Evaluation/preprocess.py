import cv2
import numpy as np
import tkSimpleDialog
import os

TRAINSET = "trainingsset/"

cap = cv2.VideoCapture(0)

def loadCards(path):
	cardPaths = os.listdir(path)
	trainset = {}
	#cv2.imshow("Erste Karte", cv2.imread(os.path.join(TRAINSET, cardPaths[0])))
	for card in cardPaths:
		cardImage = preprocess(cv2.imread(os.path.join(TRAINSET, card), flags=cv2.CV_LOAD_IMAGE_GRAYSCALE))
		trainset[card] = cardImage
	return trainset

def rectify(h):
	try:
		h = h.reshape((4,2))
	except:
		#print "Failed to rectify card"
		return False
	hnew = np.zeros((4,2),dtype = np.float32)

	add = h.sum(1)
	hnew[0] = h[np.argmin(add)]
	hnew[2] = h[np.argmax(add)]
	diff = np.diff(h,axis = 1)
	hnew[1] = h[np.argmin(diff)]
	hnew[3] = h[np.argmax(diff)]
	return hnew

def getContours(im, numcards=4):
	laplacian = cv2.Laplacian(im,cv2.CV_8U)
	#blur = cv2.GaussianBlur(laplacian,(3,3),3)
	#cv2.imshow("laplace", laplacian)
	#cv2.imshow("laplace blured", blur)
	#flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)   
	contours, hierarchy = cv2.findContours(laplacian,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key=cv2.contourArea,reverse=True)[:numcards]  
	return contours

def getCards(contours, im):
	for card in contours:
		peri = cv2.arcLength(card,True)
		poly = cv2.approxPolyDP(card,0.02*peri,True)
		approx = rectify(poly)      
		if type(approx)!=bool:
			h = np.array([ [0,0],[449,0],[449,449],[0,449] ],np.float32)
			transform = cv2.getPerspectiveTransform(approx,h)
			warp = cv2.warpPerspective(im,transform,(450,450))
			yield warp

def saveCard(img):
	cardName = raw_input("Enter Card Name: \n\t")
	cv2.imwrite(cardName + '.png', img);

def preprocess(img):
	blur = cv2.GaussianBlur(img,(5,5),2 )
	#thresh, o = cv2.threshold(blur,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)#.adaptiveThreshold(blur,255,1,1,5,1)
	return blur

def imgdiff(img1,img2):
	img1 = cv2.GaussianBlur(img1,(5,5),5)
	img2 = cv2.GaussianBlur(img2,(5,5),5)
	diff = cv2.absdiff(img1,img2)
	diff = cv2.GaussianBlur(diff,(5,5),5)    
	#flag, diff = cv2.threshold(diff, 200, 255, cv2.THRESH_BINARY)
	return np.sum(diff)  

def find_closest_card(trainingSet,img):
	features = preprocess(img)
	return sorted(trainingSet.values(), key=lambda x:imgdiff(x,img))[0]

trainSet = loadCards(TRAINSET)


while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    contours = getContours(gray)
    cv2.drawContours(gray, contours, -1, (0,255,0), 3)
    cv2.imshow("image", gray)

    for card in getCards(contours, gray):
    	detectedCard = find_closest_card(trainSet, card);
    	if(detectedCard != None):
	    	cv2.imshow("video", card)
    		cv2.imshow("detected", detectedCard)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        saveCard(card)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
