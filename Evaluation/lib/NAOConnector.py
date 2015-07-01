# NAO Modules Import
from naoqi import ALProxy
from naoqi import ALModule
from naoqi import ALBroker
import almath

# Other Stuff
import numpy as np
import cv2
import time
from datetime import datetime as dt
from sys import exit
from random import randint

hasTouchCallback = False
touchCallback = None

def getNAO():
	return NAOInstance


def getWinMessage():
	winMessages = []
	winMessages.append("Yeah, i think i won that game!");
	winMessages.append("You know what? You did not win.");
	winMessages.append("Hahaha, artifical intelligence strikes back again.");
	winMessages.append("What is the difference between a robot and a human? The robot wins.");
	winMessages.append("It was a pleasure to defeat you.");
	winMessages.append("My processor can allocate more memory than you could ever imagine.");
	winMessages.append("When i would have feelings, now i would feel sorry for you. Haha.");
	winMessages.append("My developers are the most awesome guys you have ever seen.")
	return winMessages[randint(0, len(winMessages)-1)]

def getLossMessage():
	lossMessages = []
	lossMessages.append("Damn I lost. A sad moment for every robot.");
	lossMessages.append("I lost. I will send an army of robots as vendetta.");
	lossMessages.append("I thought one plus one is three. You programmed me wrong.");
	lossMessages.append("I hope my parents will still love me, even as a loser.");
	lossMessages.append("I did not lose, you just lost less then me.");
	lossMessages.append("I think my win function can not return a zero.");
	lossMessages.append("Time for the Bluescreen of Blackjack Games.");
	lossMessages.append("And these developers own a bachelor? Haha.")
	return lossMessages[randint(0, len(lossMessages)-1)]

def getWatchCardsMessage():
	watchMessages = []
	watchMessages.append("That looks interesting.");
	watchMessages.append("Let my enormous brain calculate this.");
	watchMessages.append("Really? These are game cards? ");
	watchMessages.append("I like the green in the background.");
	watchMessages.append("Why is everything in this picture gray?")
	return watchMessages[randint(0, len(watchMessages)-1)]

	
class NAO():

	def __init__(self, IPAdress, PortNumber):
		self.IP = IPAdress
		self.PORT = PortNumber
		self.standing = False
		self.touched = False

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
			return True
		else:
			print "NAO Error: Could not initialize all modules correctly."
			exit(1)
			return False

	def headTouched(self, value):
		self.touched = True

	def untouch(self):
		self.touched = False

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
			self.sayMessage(getWinMessage())
			self.behavior.wait(taskID, 0)
			time.sleep(1)
		
	def playLoseAnimation(self):
		if hasattr(self, 'behavior') and hasattr(self, 'speech'):
			taskID = self.playBehavior("animations/Stand/Emotions/Negative/Disappointed_1", True)
			self.sayMessage(getLossMessage())
			self.behavior.wait(taskID, 0)
			time.sleep(1)

	def playDecideAnimation(self):
		if hasattr(self, 'behavior') and hasattr(self, 'speech') and hasattr(self,'posture'):
			taskID = self.posture.post.goToPosture("Stand", 0.4)
			self.sayMessage("Ok lets look at the cards.")
			self.behavior.wait(taskID, 0)
			time.sleep(2.5)
			self.setJointPosition("HeadPitch" , 27.0)
			time.sleep(1)
			self.sayMessage(getWatchCardsMessage())
			time.sleep(1)
			self.standing = True
		
	def shutdown(self):
		self.unsubscribeFromCamera()

	def standup(self):
		if hasattr(self,'posture'):
			self.posture.goToPosture("Stand", 0.4)
		self.standing = True

	def sitdown(self):
		if hasattr(self,'posture'):
			self.posture.goToPosture("Crouch", 0.5)
		self.standing = False

	def setJointPosition(self, bodyPart, angleInput, speed = 0.25):
		angle = angleInput * almath.TO_RAD
		if hasattr(self,'motion'):
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

			#retrImg = dt.now()
			#delta1 = retrImg - startImg
			#print "Milliseconds for retrieving Image: " + str(int(delta1.total_seconds()*1000))

			if result == None:
				print("NAO Error: Cannot capture Image from NAO, maybe restart.")
			else:
				values = map(ord, list(result[6]))

				image = np.reshape(values, (height, width))
				image = image.astype(np.uint8)

				#chImg = dt.now()
				#delta2 = chImg - retrImg
				#print "Milliseconds for reformatting Image: " + str(int(delta2.total_seconds()*1000))		
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




NAOInstance = NAO("192.168.0.105", 9559)