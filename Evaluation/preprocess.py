import cv2
import numpy as np
import tkSimpleDialog

cap = cv2.VideoCapture(0)

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
	blur = cv2.GaussianBlur(gray,(1,1),1000)
	flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)   
	contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
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

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    contours = getContours(gray)
    cv2.drawContours(gray, contours, -1, (0,255,0), 3)
    cv2.imshow("image", gray)

    for card in getCards(contours, gray):
    	cv2.imshow("getCards", card)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        saveCard(card)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
