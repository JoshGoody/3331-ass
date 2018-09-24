import pickle

import sys

import time

from random import *

from socket import *





class Packet:

    def __init__(self, data, seqNum, ackNum, ack=False, syn=False, fin=False):

        self.data = data
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.ack = ack
        self.syn = syn
        self.fin = fin
	
		
	
class Sender:
    
    def __init__(self,  rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed):
        self.rHostIp = rHostIp
        self.recPort = int(recPort)
        self.sFile = sFile
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
        f = open(self.sFile, "r")
        data = f.read()
        f.close()
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
        end = dataProgress + self.MSS
        if (end < dataLength):
            load = completeData[dataProgress:end]
        
        else: 
            load = completeData[dataProgress:dataLength]
        return load
    
    
    def sendPacket(self, packet):
        self.socket.sendto(pickle.dumps(packet), (self.rHostIp, self.recPort))
    
    
    
    #def logU(self, , , ):


#### MAIN 

if (len(sys.argv) != 15):
    print("incorect usage, 14 arguments needed")
    exit(0)

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

rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed = sys.argv[1:]

###sener is initiated

sender = Sender(rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
sendFile = sender.pullFile()
fileLength = len(sendFile)
dataSent = 0

while (connectionFinished == False):
    
    
    ###send syn
    if (noConnection == True):
        print("sending syn")
        synPacket = Packet('', seqNum, ackNum, ack = False, syn = True, fin = False)
        #print(synPacket.seqNum)
        sender.sendPacket(synPacket)
        synSent = True
        noConnection = False
        
    if (synSent == True):
        print("waiting for synAck")
        synAckPacket = sender.receivePacket()
        
        if (synAckPacket.ack == True and synAckPacket.syn == True):
            
            ackNum = synAckPacket.seqNum + 1
            seqNum = seqNum + 1
            
            ackPacket = Packet('', seqNum, ackNum, ack = True, syn = False, fin = False)
            sender.sendPacket(ackPacket)
            synSent = False
            connected = True
            print("sent ack, starting file transfer")
        else:
            print("error in synSent flag stage")
            
        
    ###main bit of while loop for open connection
    if (connected == True):
    
        
        ###create the packet to be sent
        load = sender.splitDataToLoad(sendFile, dataSent)
        dataSent += len(load)
        ## maybe need to increment sequence number here?
        packet = Packet(load, seqNum, ackNum, ack = False, syn = False, fin = False)
        
        ## this is where pld module will go ventually
        
        #send packet
        print("sent packets")
        print(len(packet.data), packet.seqNum)
        sender.sendPacket(packet)
        seqNum += len(load)
        transCount = transCount + 1
        
        
        ##receive same packet
        ackPacket = sender.receivePacket()
        ackNum = ackPacket.seqNum + 1
        
        if (ackPacket.ack == True and ackPacket.ackNum == seqNum):
            print("correct acknowledgment received")
            ##do what you need to do when an ack is received from the receiver
        
        if (dataSent == fileLength):
            print("everything received, file ready, fin sent")
            finSent = True
            connected = False
            finPacket = Packet('', seqNum, ackNum, ack = False, syn = False, fin = True)
            sender.sendPacket(finPacket)

    if (finSent == True):
        ackPacket = sender.receivePacket()
        if (ackPacket.ack == True and ackPacket.fin == False):
            print("fin acknowledgment received")
            finPacket = sender.receivePacket() 
            ackNum = ackNum + 1
            
            if (finPacket.fin == True):
                finSent = False
                ackPacket = Packet('', ackNum, seqNum, ack = True, syn = False, fin = False)
                sender.sendPacket(ackPacket)
                print("connection terminated and fin completed")
                connectionFinished = True
    
sender.socket.close()
    
                
            
        
        
    
        
    	
		
		
		
		
		
