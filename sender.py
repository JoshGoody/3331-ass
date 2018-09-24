import pickle

import sys

import time

from random import *

from socket import *





    class Packet:

	    def __init__(self, data, seqNum, ackNum, ack=False, syn=False, fin=False):

	        self.data = data
	        self.seq_num = seq_num
	        self.ack_num = ack_num
	        self.ack = ack
            self.syn = syn
	        self.fin = fin
		
			
		
    class Sender:
        
        def __init__(self,  rHostIp, recPort, file, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed):
            self.rHostIp = rHostIp
            self.recPort = int(recPort)
            self.file = file
            self.MWS = int(MWS)
            self.MSS = int(MSS)
            self.gamma = float(gamma)
            self.pDrop = pDrop
            self.pDup = pDup
            self.pCor = pCor
            self.pOrd = pOrd
            self.maxOrd = maxOrd
            self.pDel = pDel
            self.maxDel = maxDel
            self.seed = int(seed)
            
            
		
	    #create a UDP socket for the sender
	
	    socket = socket(AF_INET, SOCK_DGRAM) 
	
	    #store file as data to send to receiver 
	
	    def pullFile(self):
	        f = open(self.file, "r")
	        data = f.read()
	        return data
	        
        #def createAck(self, seqNum, ackNum):
            
        
        
        
        #def createFIN(self, seqNum, ackNum):
        
        #def createSYN(self, seqNum, ackNum):
        
        def receivePacket(self):
            data, addr = self.socket.recvfrom(2048)
            stpPacket = pickle.loads(data)
            return stpPacket
        
        
        #create packet of max seg size
        def splitDataToLoad(self, completeData, dataProgress):
            dataLength = len(completeData)
            end = completeData + self.MSS
            if (end < dataLength):
                load = completeData[dataProgress:dataLength]
            
            else: 
                load = completeData[dataProgress:end]
            return load
        
        
        def sendPacket(self, packet):
            self.socket.sendto(pickle.dumps(packet), (self.rHostIp, self.recPort))
        
        
        
        def logU(self, , , ):
    
    
    #### MAIN 
	
    if (len(sys.argv) != 15):
        print("incorect usage")
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
    
    rHostIp, recPort, file, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed = sys.argv[1:]
    
    ###sener is initiated
    
    sender = Sender(rHostIp, recPort, file, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
    sendFile = sender.pullFile()
    fileLength = len(sendFile)
    dataSent = 0
    
    while (connectionFinished == False):
        
        
        ###send syn
        if noConnection == True:
            synPacket = Packet('', seqNum, ackNum, ack = False, syn = True, fin = False )
            sender.sendPacket(senPacket)
            synSent = True
            noConnection = False
            
        if synSent = True
            synAckPacket = sender.receivePacket()
            
            if synAckPacket.ack == True && synAckPacket.syn == True:
                
                ackNum = synAckPacket.seqNum + 1
                seqNum = seqNum + 1
                
                ackPacket = packet('', seqNum, ackNum, ack = True, syn = False, fin = False)
                sender.sendPacket(ackPacket)
                synSent = False
                connected = True
            else:
                print("error in synSent flag stage")
                
            
        ###main bit of while loop for open connection
        if connected = True:
        
            
            ###create the packet to be sent
            load = sender.splitDataToLoad(sendFile, dataSent)
            dataSent += len(load)
            ## maybe need to increment sequence number here?
            packet = Packet(load, seqNum, ackNum, ack = False, syn = False, fin = False)
            
            ## this is where pld module will go ventually
            
            #send packet
            sender.sendPacket(packet)
            seqNumber += len(load)
            transCount++
            
            
            ##receive same packet
            ackPacket = sender.receivePacket()
            ackNum = ackPacket.seqNum + 1
            
            if ackPacket.ack == True and ackPacket.ackNum == seqNum:
                
                ##do what you need to do when an ack is received from the receiver
            
            if dataSent == fileLength:
                print("everything received, file ready, start fin")
                finSent = True
                connected = False
                finPacket = Packet('', seqNum, ackNum, ack = False, syn = False, fin = True)
                sender.sendPacket(finPacket)
    
        if finSent = True:
            ackPacket = sender.receivePacket()
            if ackPacket.ack == True and ackPacket.fin = False:
                finPacket = sender.receivePacket() 
                ackNum++
                
                if finPacket.fin == True:
                    
                    ackPacket = Packet('', ackNum, seqNum, ack = True, syn = False, Fin = False)
                    sender.sendPacket(ackPacket)
                    print("connection terminated and fin completed")
        
        
        sender.socket.close()
        
                    
                
            
            
        
        
    	
		
		
		
		
		
