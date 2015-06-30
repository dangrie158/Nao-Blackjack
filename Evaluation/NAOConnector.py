# NAO Modules Import
from naoqi import ALProxy
from naoqi import ALModule
from naoqi import ALBroker
import almath

# Other Stuff
import numpy as np
import cv2
from datetime import datetime as dt
from sys import exit

class NAO():

	def __init__(self, IPAdress, PortNumber):
		self.IP = IPAdress
		self.PORT = PortNumber
		self.standing = False

	def setup(self):
		try:
			self.motion = ALProxy("ALMotion", self.IP, self.PORT)
		except Exception, e:
			print "Could not create Connection to NAO Motion"
			print "NAO Error: ", e
	
		try:
			self.memory = ALProxy("ALMemory", self.IP, self.PORT)
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

		try:
			self.speech = ALProxy('ALTextToSpeech', self.IP, self.PORT)
		except Exception, e:
			print "Could not create Connection to NAO Speech"
			print "NAO Error: ", e

		try:
			self.behavior = ALProxy('ALBehaviorManager', self.IP, self.PORT)
		except Exception, e:
			print "Could not create Connection to NAO Behavior"
			print "NAO Error: ", e

		if hasattr(self, 'behavior') and hasattr(self, 'memory') and hasattr(self,'motion') and hasattr(self,'posture') and hasattr(self,'video') and hasattr(self, 'speech'):
			Connector = self
			return True
		else:
			print "NAO Error: Could not initialize all modules correctly."
			exit(1)
			return False

	def headTouched(self, value):
		
		for v in value:
			if v[1] and "Head" in v[0]:
				print "Touched my Head!"

	def hasBehavior(self, name):
		if hasattr(self, 'behavior'):
			return self.behavior.isBehaviorInstalled(name)

	def playBehavior(self, name, post=False):
		if hasattr(self, 'behavior'):
			if post == True:
				taskID = self.behavior.post.runBehavior(name)
				return taskID
			else:
				self.behavior.runBehavior(name)
				return None

	def getBehaviors(self):
		if hasattr(self, 'behavior'):
			return self.behavior.getInstalledBehaviors()

	def stopBehavior(self, name):
		if hasattr(self, 'behavior'):
			self.behavior.stopBehavior(name)

	def playWinAnimation(self):
		if hasattr(self, 'behavior') and hasattr(self, 'speech'):
			taskID = self.playBehavior("animations/Stand/Emotions/Positive/Excited_2", True)
			self.sayMessage("Yeah, i think i won that game!")
			self.behavior.wait(taskID, 0)
		
	def playLooseAnimation(self):
		if hasattr(self, 'behavior') and hasattr(self, 'speech'):
			taskID = self.playBehavior("animations/Stand/Emotions/Negative/Disappointed_1", True)
			self.sayMessage("Damn I lost. A sad moment for every robot.")
			self.behavior.wait(taskID, 0)
		
	def shutdown(self):
		self.unsubscribeFromCamera()

	def standup(self):
		if hasattr(self,'posture'):
			self.posture.goToPosture("Stand", 0.65)
		self.standing = True

	def sitdown(self):
		if hasattr(self,'posture'):
			self.posture.goToPosture("Crouch", 0.65)
		self.standing = False

	def setJointPosition(self, bodyPart, angleInput, speed = 0.3):
		if hasattr(self,'motion'):
			angle = angleInput * almath.TO_RAD
			self.motion.setAngles(bodyPart, angle, speed)

	def printMotionState(self):
		if hasattr(self,'motion'):
			print self.motion.getSummary()

	def sayMessage(self, message):
		if hasattr(self, 'speech'):
				self.speech.say(message)

	# Camera Number: 0 is upper camera, 1 is lower camera
	# Resolution: 3 is 1280x960, 2 is 640x480 and so on
	def subscribeToCamera(self, cameraNumber = 1, resolutionPix = 2, colorspaceVal = 8, fps = 30):
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

			startImg = dt.now()

			try:
				result = self.video.getImageRemote(self.device);
			except BaseException, e:
				print("NAO Error: ", e)
				exit(1)

			retrImg = dt.now()
			delta1 = retrImg - startImg
			print "Milliseconds for retrieving Image: " + str(int(delta1.total_seconds()*1000))

			if result == None:
				print("NAO Error: Cannot capture Image from NAO, maybe restart.")
			else:
				values = map(ord, list(result[6]))

				image = np.reshape(values, (height, width))
				image = image.astype(np.uint8)

				chImg = dt.now()
				delta2 = chImg - retrImg
				print "Milliseconds for reformatting Image: " + str(int(delta2.total_seconds()*1000))		
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
