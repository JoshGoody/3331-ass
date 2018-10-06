import pickle
import sys
import time
from random import *
from socket import *
import select
import threading 
import queue
from collections import deque


class Packet:

    def __init__(self, data, seqNum, ackNum, checksum, ack = False, syn = False, fin = False, retran = False):

        self.data = data
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.checksum = checksum
        self.ack = ack
        self.syn = syn
        self.fin = fin
        self.retran = retran
        
    

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
        
    
    def log(self, event, time, pType, seqNum, bytes, ackNum):
        space = 28
        log = ""
        
        sList = [str(event), str(time), str(pType), str(seqNum), str(bytes), str(ackNum)]
        i = 0
        while (i < 6):
            length = len(sList[i])
            length = space - length
            spacing = ""
            j = 0
            while (j < length):
                spacing += " "
                j +=1
            
            log += sList[i] + spacing
            i += 1
        
        log += "\n"
        f = open("Receiver_log.txt", "a+")
        f.write(log)
        f.close()
    
    
    
    
###main

if (len(sys.argv) != 3):
    print("incorect usage, needs two arguments")
    exit(0)
##reset the files 
f = open("Receiver_log.txt", "w")
f.close()
#f = open("r_test.txt", "w")
#f.close()

seqNum = 0
ackNum = 0
#sendbase = 0
#numUnAck = 0
prevNum = 0

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
dupPackRec = 0

recPort, fileCopy = sys.argv[1:]
receiver = Receiver(recPort, fileCopy)
receiver.socket.bind(('', receiver.recPort))
buff = deque()
###main event

while (connectionFinished == False):
    
    if (noConnection == True):
        synPacket, address = receiver.receivePacket()
        startTime = time.time()
        if (synPacket.syn == True):
            receiver.log("rcv", time.time()-startTime, "S", synPacket.seqNum, 0, synPacket.ackNum)
            ackNum = synPacket.seqNum + 1
            synAckPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = True, fin = False, retran = False)
            receiver.sendPacket(synAckPacket, address)
            receiver.log("snd", time.time()-startTime, "SA", seqNum, 0, ackNum)
            noConnection = False
            synSent = True
            expectedAck = seqNum + 1
    
    if (synSent == True):
        
        ackPacket, address = receiver.receivePacket()
        
        if (ackPacket.ack == True and expectedAck == ackPacket.ackNum):
            receiver.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
            expectedSeq = ackPacket.seqNum
            synSent = False
            connected = True
    
    if (connected == True):
        
        while (connected == True):
            print("waiting for packet " + str(expectedSeq))
            packet, address = receiver.receivePacket() 
            print(len(packet.data),packet.seqNum,packet.ackNum)
            if (packet.fin == False and packet.seqNum == expectedSeq):
                receiver.log("rcv", time.time()-startTime, "D", packet.seqNum, len(packet.data), packet.ackNum)
                receiver.appendData(packet.data)
                dataProgress += len(packet.data)
                seqNum = seqNum + 1
                ackNum += len(packet.data)
                expectedSeq = ackNum
                expectedAck = seqNum + 1
                packetLen = len(packet.data)
                while (len(buff) > 0):
                    packet1 = buff.popleft()
                    if (packet1.seqNum == expectedSeq):
                        receiver.appendData(packet1.data)
                        dataProgress += len(packet1.data)
                        seqNum = seqNum + 1
                        ackNum += len(packet1.data)
                        expectedSeq = ackNum
                        expectedAck = seqNum + 1
                    else:
                        buff.appendleft(packet1)
                        break    
                        
                print("sending ack")
                if (packet.retran == True):
                    ackPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = False, fin = False, retran = True)
                else:
                    ackPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = False, fin = False, retran = False)
                
                print(ackPacket.seqNum,ackPacket.ackNum)
                receiver.sendPacket(ackPacket, address)
                receiver.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
                   

            elif (packet.fin == True):
                print("fin received")
                receiver.log("rcv", time.time()-startTime, "F", packet.seqNum, 0, packet.ackNum)
                #finish
                connected = False
                fin = True
                seqNum = seqNum + 1
                ackNum = packet.seqNum + 1
                ackPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = False, fin = False, retran = False)
                receiver.sendPacket(ackPacket, address)
                print("ack sent")
                receiver.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
            
            elif (packet.seqNum < expectedSeq or packet.seqNum == prevNum):
                print("dup received")
                receiver.log("rcv/dup", time.time()-startTime, "D", packet.seqNum, len(packet.data), packet.ackNum)
                dupPackRec += 1
                ackPacket = Packet('', seqNum, expectedSeq, 0, ack = True, syn = False, fin = False, retran = True)
                print("sending ack")
                print(ackPacket.seqNum,ackPacket.ackNum)
                receiver.sendPacket(ackPacket, address)
                receiver.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
            
            else:
                print("packet out of order")
                print(packet.seqNum)
                receiver.log("rcv", time.time()-startTime, "D", packet.seqNum, len(packet.data), packet.ackNum)
                buff.append(packet)
                ackPacket = Packet('', seqNum, expectedSeq, 0, ack = True, syn = False, fin = False, retran = False)
                receiver.sendPacket(ackPacket, address)
                receiver.log("snd", time.time()-startTime, "A", seqNum, 0, expectedSeq)
                #packet out of order and add to buffer
            prevNum = packet.seqNum
    
    
    
    if (fin == True):
        ###more finishing logic
        finPacket = Packet('', seqNum, ackNum, 0, ack = False, syn = False, fin = True, retran = False)
        receiver.sendPacket(finPacket, address)
        print("fin sent")
        receiver.log("snd", time.time()-startTime, "F", seqNum, 0, ackNum)
        ##wait for ack for fin
        
        
        packet, address = receiver.receivePacket()
        if packet.ack == True:
            print("fin acknowledged")
            fin = False
            connectionFinished = True
            receiver.log("rcv", time.time()-startTime, "A", packet.seqNum, 0, packet.ackNum)
            receiver.socket.close()
            print("connection closed, file received succesfully")
            



    
    
    
    
    
    
    
    
