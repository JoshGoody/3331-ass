import pickle

import sys

import time

from random import *

from socket import *





    class STPPacket:

	    def __init__(self, data, seqNum, ackNum, ack = False, syn = False, fin = False):

	        self.data = data
	        self.seqNum = seqNum
	        self.ackNum = ackNum
	        self.ack = ack
            self.syn = syn
	        self.fin = fin
	    

    class receiver:

        def __init__(self, recPort, fileCopy):
            self.recPort = recPort
            self.fileCopy = fileCopy
            
            
        
        socket = socket(AF_INET, SOCK_DGRAM)
        
        def receivePacket(self):
            data, addr = self.socket.recvfrom(2048)
            packet = pickle.loads(data)
            return packet, addr
            
        
        def appendData(self, data):
            f = open(fileCopy, "a+")
            f.write(data)
            f.close()

        
        def sendPacket(self, packet, address):
            self.socket.sendto(pickle.dumps(packet), address)
            
        
        #def updateLog(self , , ,)
        
        
        
        
    ###main
    
    if (len(sys.argv) != 3):
        print("incorect usage, needs two arguments")
        return
    
    
   
    seqNum = 0
    ackNum = 0
    #sendbase = 0
    #numUnAck = 0
    
    # different states of operation
    noConnection = True
    synSent = False
    connected = False
    finSent = False
    connectionFinished = False
    
    transCount = 0
    untranCount = 0
    dropCount = 0 
    expectedSeq = 0
    expectedAck = 0
    
    recPort, fileCopy = sys.argv[1:]
    receiver = Receiver(recPort, fileCopy)
    receiver.socket.bind(('', receiver.recPort))
    
    
    ###main event
    
    while (connectionFinished == False):
        
        if (noConnection == True):
            synPacket, address = receiver.receivePacket
            
            if (synPacket.syn == True):
                ackNum = synPacket.seqNum + 1
                synAckPacket = Packet('', seqNum, ackNum, ack = True, syn = True, fin = False)
                receiver.sendPacket(senAckPacket, address)
                noConnection = False
                synSent = True
                expectedAck = seqNum + 1
        
        if (synSent = True):
            
            ackPacket, address = receiver.receivePacket()
            
            if (ackPacket.ack == True and expectedAck == ackPacket.ackNum):
                expectedSeq = ackPacket.seqNum
                synSent = False
                connected = True
        
        if (connected == True):
            
            while True:
            
                packet, address = receiver.receivePacket() 
               
                if (packet.fin == False and packet.seqNum == expectedSeq):
                    receiver.appendData(packet.data)
                    dataProgress += len(packet.data)
                    seqNum++
                    ackNum += len(packet.data)
                    expectedSeq = ackNum
                    expectedAck = seqNum + 1
                    ackPacket = Packet('', seqNum, ackNum, ack = True, syn = False, fin = False)
                    receiver.sendPacket(ackPacket, address)
                       
    
                else if (packet.fin == True):
                    
                    #finish
                    connected = False
                    finSent = True
                else:
                    
                    #packet out of order and add to buffer
        
        
        if (finSent == True):
            ###more finishing logic
    
    
    
    
 
    
    
    
    
    
    
    
    
