import cv2
import numpy as np
import math
import os
from sys import maxint

# load and preprocess methods for trainingsdata
def loadCards(trainSet):
	cardPaths = os.listdir(trainSet)
	trainset = {}
	for card in cardPaths:
		cardImage = cv2.imread(os.path.join(trainSet, card), flags=cv2.CV_LOAD_IMAGE_GRAYSCALE)
		trainset[card] = cardImage
	return trainset

# returns direct nearest difference image on given trainingsset
def returnDirectDiffImage(trainingSet, img):
	return sorted(trainingSet.values(), key=lambda x:imgdiff(x,img))[0]

# calculates differences between two images
def imgdiff(img1,img2):
	diff = cv2.absdiff(img1,img2)    
	return np.sum(diff)  

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

# Crops a given image to fit in a given rectangle
def imageRerverseProjection(rectangle, im):  
	newRect = np.array([ [0,0],[449,0],[449,449],[0,449] ],np.float32)

	transform = cv2.getPerspectiveTransform(rectangle, newRect)
	warp = cv2.warpPerspective(im,transform,(450,450))
	# Rotate if necessary
	if euclidDist(rectangle[0], rectangle[1]) > euclidDist(rectangle[1], rectangle[2]):
		warp = rotateImage(warp, 450)
	return warp

# Crops a given image to a given percentage
def cropPercentage(im, fromPoint, toPoint):
	xSize = im.shape[0]
	ySize = im.shape[1]
	return im[xSize/100*fromPoint[0]:xSize/100*toPoint[0], ySize/100*fromPoint[1]:ySize/100*toPoint[1]]

# Rotate a given Image
def rotateImage(im, imSize, angle = 90):
	shape = (imSize, imSize)
	rotMat = cv2.getRotationMatrix2D((imSize / 2, imSize / 2), angle, 1.0)
	result = cv2.warpAffine(im, rotMat, shape, flags=cv2.INTER_LINEAR)
	return result

# Returns the bounding box of a rectangle
def getBoundingBox(rect):
	xMin, yMin, = [maxint, maxint]
	xMax, yMax = [0, 0]
	for p in rect:
		if p[0] < xMin: xMin = p[0]
		if p[1] < yMin: yMin = p[1]
		if p[0] > xMax: xMax = p[0]
		if p[1] > yMax: yMax = p[1]
	p1 = (xMin, yMin)
	p2 = (xMax, yMax)
	return p1, p2

def polygonCentroid(poly):
	#the formula from http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon
	#the signed area:
	a = 0.0
	cx = 0.0
	cy = 0.0
	for i in range(0, len(poly)):
		i1 = (i + 1) % len(poly)
		asum = poly[i][0] * poly[i1][1] - poly[i1][0] * poly[i][1]
		cx += (poly[i][0] + poly[i1][0]) * asum
		cy += (poly[i][1] + poly[i1][1]) * asum
		a += asum

	a *= 0.5
	cx /= (6 * a)
	cy /= (6 * a)
	return (int(cx), int(cy))