# NAO Modules Import
from naoqi import ALProxy
import almath

# Other Stuff
import numpy as np
import cv2


class NAO:
	def __init__(self, IPAdress, PortNumber):
		self.IP = IPAdress
		self.PORT = PortNumber


	def init(self):
		try:
			self.motion = ALProxy("ALMotion", self.IP, self.PORT)
		except Exception, e:
			print "Could not create Connection to NAO Motion"
			print "NAO Error: ", e
	
		try:
			self.video = ALProxy('ALVideoDevice', self.IP, self.PORT)
		except Exception, e:
			print "Could not create Connection to NAO Video"
			print "NAO Error: ", e
	
		try:
			self.posture = ALProxy('ALRobotPosture', self.IP, self.PORT)
		except Exception, e:
			print "Could not create Connection to NAO Posture"
			print "NAO Error: ", e

		if hasattr(self,'motion') and hasattr(self,'posture') and hasattr(self,'video'):
			return True
		else:
			return False

	def enableStandardPosture(self):
		if hasattr(self,'posture'):
			self.posture.goToPosture("Crouch", 0.5)
			print "NAO going into Crouch Posture"
		if hasattr(self,'motion'):
			self.motion.setIdlePostureEnabled("Head", False)

	def setJointPosition(self, bodyPart, angleInput):
		if hasattr(self,'motion'):
			self.motion.setStiffnesses("Body", 1.0)
			angle = angleInput * almath.TO_RAD
			fractionSpeed = 0.4
			self.motion.setAngles(bodyPart, angle, fractionSpeed)
			self.motion.setStiffnesses("Body", 0.0)

	def printMotionState(self):
		if hasattr(self,'motion'):
			print self.motion.getSummary()

	def subscribeToCamera(self, cameraNumber = 1, resolutionPix = 3, colorspaceVal = 13, fps = 2):
		self.camera = cameraNumber
		self.resolution = resolutionPix
		self.colorspace = colorspaceVal
		self.framerate = fps
		if hasattr(self,'video'):
			self.device = self.video.subscribeCamera("Blackjack", self.camera, self.resolution, self.colorspace, self.framerate)

	def unsubscribeFromCamera(self):
		if hasattr(self,'video') and hasattr(self,'device'):
			self.video.unsubscribe(self.device)

	def getCameraImage(self):
		if hasattr(self,'video') and hasattr(self,'device'):
			width, height = self.getWidthHeight()
			image = np.zeros((height, width, 3), np.uint8)

			try:
				result = self.video.getImageRemote(self.device);
			except BaseException, e:
				print("NAO Error: ", e)

			if result == None:
				print("NAO Error: Cannot capture Image from NAO, maybe restart.")
				sys.exit(1)
			else:
				values = map(ord, list(result[6]))
				i = 0
				for y in range(0, height):
					for x in range(0, width):
						image.itemset((y, x, 0), values[i + 0])
						image.itemset((y, x, 1), values[i + 1])
						image.itemset((y, x, 2), values[i + 2])
						i += 3
				return image

	def getWidthHeight(self):
		if hasattr(self,'resolution'):
			if(self.resolution == 3):
				return 1280, 960
			elif(self.resolution == 2):
				return 640, 480
			elif(self.resolution == 1):
				return 320, 240
			elif(self.resolution == 0):
				return 160, 120
		else:
			print "NAO Error: You have to set a resolution first."