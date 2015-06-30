# -*- encoding: UTF-8 -*-
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import NAOConnector

# Global variable to store the ReactToTouch module instance
NAOTouchListener = None
memory = None

class NAOTouchListener(ALModule):
    """ A simple module able to react
        to touch events.
    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Subscribe to TouchChanged event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("TouchChanged", "NAOTouchListener", "onTouched")

    def onTouched(self, strVarName, value):
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        
        try:
            memory.unsubscribeToEvent("TouchChanged", "NAOTouchListener")
        except:
            pass

        if hasattr(self, 'nao'):
            self.nao.headTouched(value)

        # Subscribe again to the event
        try:
            memory.subscribeToEvent("TouchChanged", "NAOTouchListener", "onTouched")
        except:
            pass

    def setConnector(self, connector):
        self.nao = connector


def startNAOListener(ip, port):

    myBroker = ALBroker("myBroker",
    "0.0.0.0",   # listen to anyone
    0,           # find a free port and use it
    ip,          # parent broker IP
    port)        # parent broker port

    global NAOTouchListener
    NAOTouchListener = NAOTouchListener("NAOTouchListener")
    return NAOTouchListener

if __name__ == "__main__":
    startNAOListener("192.168.0.105", 9559)
    while(1):
        pass