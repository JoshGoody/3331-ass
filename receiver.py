import pickle

import sys

import time

from random import *

from socket import *





class Packet:

    def __init__(self, data, seqNum, ackNum, ack = False, syn = False, fin = False):

        self.data = data
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.ack = ack
        self.syn = syn
        self.fin = fin
    

class Receiver:

    def __init__(self, recPort, fileCopy):
        self.recPort = int(recPort)
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
    exit(0)



seqNum = 0
ackNum = 0
#sendbase = 0
#numUnAck = 0

# different states of operation
noConnection = True
synSent = False
connected = False
fin = False
connectionFinished = False

dataProgress = 0
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
        synPacket, address = receiver.receivePacket()
        
        if (synPacket.syn == True):
            ackNum = synPacket.seqNum + 1
            synAckPacket = Packet('', seqNum, ackNum, ack = True, syn = True, fin = False)
            receiver.sendPacket(synAckPacket, address)
            noConnection = False
            synSent = True
            expectedAck = seqNum + 1
    
    if (synSent == True):
        
        ackPacket, address = receiver.receivePacket()
        
        if (ackPacket.ack == True and expectedAck == ackPacket.ackNum):
            expectedSeq = ackPacket.seqNum
            synSent = False
            connected = True
    
    if (connected == True):
        
        while (connected == True):
            print("waiting for packets")
            packet, address = receiver.receivePacket() 
           
            if (packet.fin == False and packet.seqNum == expectedSeq):
                receiver.appendData(packet.data)
                dataProgress += len(packet.data)
                seqNum = seqNum + 1
                ackNum += len(packet.data)
                expectedSeq = ackNum
                expectedAck = seqNum + 1
                print("sending ack")
                ackPacket = Packet('', seqNum, ackNum, ack = True, syn = False, fin = False)
                receiver.sendPacket(ackPacket, address)
                   

            elif (packet.fin == True):
                print("fin received")
                #finish
                connected = False
                fin = True
                seqNum = seqNum + 1
                ackNum = packet.seqNum + 1
                ackPacket = Packet('', seqNum, ackNum, ack = True, syn = False, fin = False)
                receiver.sendPacket(ackPacket, address)
                print("ack sent")
            else:
                print("packet out of order")
                #packet out of order and add to buffer
    
    
    
    if (fin == True):
        ###more finishing logic
        finPacket = Packet('', seqNum, ackNum, ack = False, syn = False, fin = True)
        receiver.sendPacket(finPacket, address)
        print("fin sent")
        
        ##wait for ack for fin
        
        
        packet, address = receiver.receivePacket()
        if packet.ack == True:
            print("fin acknowledged")
            fin = False
            connectionFinished = True
            receiver.socket.close()
            print("connection closed, file received succesfully")
            



    
    
    
    
    
    
    
    
