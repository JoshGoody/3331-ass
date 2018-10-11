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
        data, addr = self.socket.recvfrom(4096)
        packet = pickle.loads(data)
        return packet, addr
        
    
    def appendData(self, data):
        with open(fileCopy, "a+b") as f:
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
    
    def receiveThread(self, receiver):
        while (connected == True):
            global segCount, packetDeque
            packet123, address = receiver.receivePacket() 
            segCount += 1
            packetDeque.append(packet123)
            if (packet123.fin == True):
                return
    
    
###main

if (len(sys.argv) != 3):
    print("incorect usage, needs two arguments")
    exit(0)
##reset the files 
f = open("Receiver_log.txt", "w")
f.close()


seqNum = 0
ackNum = 0
prevNum = 0

# different states of operation
noConnection = True
synSent = False
connected = False
fin = False
connectionFinished = False
notFound = True

#log trackers
bitErrorCount = 0
dataProgress = 0
segCount = 0
dSegCount = 0
dupCount = 0
dupACKCount = 0
untranCount = 0
dropCount = 0 
expectedSeq = 0
expectedAck = 0
dupPackRec = 0

recPort, fileCopy = sys.argv[1:]
receiver = Receiver(recPort, fileCopy)
receiver.socket.bind(('', receiver.recPort))
buff = deque()
packetDeque = deque()
addressInUse = None
###main event

while (connectionFinished == False):
    
    if (noConnection == True):
        synPacket, address = receiver.receivePacket()
        startTime = time.time()
        addressInUse = address
        segCount += 1
        if (synPacket.syn == True):
            receiver.log("rcv", 0, "S", synPacket.seqNum, 0, synPacket.ackNum)
            ackNum = synPacket.seqNum + 1
            synAckPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = True, fin = False, retran = False)
            receiver.sendPacket(synAckPacket, address)
            receiver.log("snd", time.time()-startTime, "SA", seqNum, 0, ackNum)
            noConnection = False
            synSent = True
            expectedAck = seqNum + 1
    
    if (synSent == True):
        
        ackPacket, address = receiver.receivePacket()
        segCount += 1
        if (ackPacket.ack == True and expectedAck == ackPacket.ackNum):
            receiver.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
            expectedSeq = ackPacket.seqNum
            synSent = False
            connected = True
            receiveThread = threading.Thread(target=receiver.receiveThread, args=[receiver])
            receiveThread.start()
    
    if (connected == True):
        
        while (connected == True):

            if (len(packetDeque) != 0):
                packet = packetDeque.popleft()
            else:
                continue
            

            print("waiting for packet " + str(expectedSeq))
            print(len(packet.data),packet.seqNum,packet.ackNum)
            checkSum = packet.data
            
            if (checkSum != packet.checksum and packet.fin == False):
                print("packet corrupted, discrading")
                receiver.log("rcv/Cor", time.time()-startTime, "D", packet.seqNum, len(packet.data), packet.ackNum)
                bitErrorCount += 1
            
            elif (packet.fin == False and packet.seqNum == expectedSeq):
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
                        ### if the packet has already been added discard the packet
                        seqNum = seqNum + 1
                        ackNum += len(packet1.data)
                        expectedSeq = ackNum
                        expectedAck = seqNum + 1
                    else:
                        i = 0
                        buff.append(packet1)
                        while (i < len(buff)-1):
                            checkPacket = buff.popleft()
                            if (checkPacket.seqNum == expectedSeq):
                                notFound = False 
                                receiver.appendData(checkPacket.data)
                                dataProgress += len(checkPacket.data)
                                ### if the packet has already been added discard the packet
                                seqNum = seqNum + 1
                                ackNum += len(checkPacket.data)
                                expectedSeq = ackNum
                                expectedAck = seqNum + 1
                                j = 0
                                while (j < len(buff)-i-1):
                                    packet12 = buff.popleft()
                                    buff.append(packet12)
                                    j += 1
                                break
                            else:
                                buff.append(checkPacket)
                                i += 1
                        
                        if (notFound == True):
                            break
                        else:
                            notFound = True
                            continue    
                        
                print("sending ack")
                if (packet.retran == True):
                    ackPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = False, fin = False, retran = True)
                else:
                    ackPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = False, fin = False, retran = False)
                
                print(ackPacket.seqNum,ackPacket.ackNum)
                receiver.sendPacket(ackPacket, addressInUse)
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
                receiver.sendPacket(ackPacket, addressInUse)
                print("ack sent")
                receiver.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
            
            elif (packet.seqNum < expectedSeq or packet.seqNum == prevNum):
                print("dup received")
                dupCount += 1
                dupACKCount += 1
                receiver.log("rcv/dup", time.time()-startTime, "D", packet.seqNum, len(packet.data), packet.ackNum)
                dupPackRec += 1
                ackPacket = Packet('', seqNum, expectedSeq, 0, ack = True, syn = False, fin = False, retran = True)
                print("sending ack")
                print(ackPacket.seqNum,ackPacket.ackNum)
                receiver.sendPacket(ackPacket, addressInUse)
                receiver.log("snd/DA", time.time()-startTime, "A", seqNum, 0, ackNum)
            
            else:
                print("packet out of order")
                print(packet.seqNum)
                dupACKCount += 1
                receiver.log("rcv", time.time()-startTime, "D", packet.seqNum, len(packet.data), packet.ackNum)
                buff.append(packet)
                ackPacket = Packet('', seqNum, expectedSeq, 0, ack = True, syn = False, fin = False, retran = False)
                receiver.sendPacket(ackPacket, addressInUse)
                receiver.log("snd/DA", time.time()-startTime, "A", seqNum, 0, expectedSeq)
                #packet out of order and add to buffer
            prevNum = packet.seqNum
    
    
    
    if (fin == True):
        time.sleep(0.2)
        ###more finishing logic
        finPacket = Packet('', seqNum, ackNum, 0, ack = False, syn = False, fin = True, retran = False)
        receiver.sendPacket(finPacket, addressInUse)
        print("fin sent")
        receiver.log("snd", time.time()-startTime, "F", seqNum, 0, ackNum)
        ##wait for ack for fin
        
        ######this should never happen but just in case
        try:
            receiver.socket.settimeout(3)
            packet, address = receiver.receivePacket()
        except Exception as e:
            print("shouldnt happen")
            segCount += 1
            dSegCount = dSegCount + segCount - 4
            fin = False
            connectionFinished = True
            receiver.log("rcv", time.time()-startTime, "A", packet.seqNum, 0, packet.ackNum)
            receiver.socket.close()
            print("connection closed, file received succesfully")
            break
            
        segCount += 1
        dSegCount = dSegCount + segCount - 4
        if packet.ack == True:
            print("fin acknowledged")
            fin = False
            connectionFinished = True
            receiver.log("rcv", time.time()-startTime, "A", packet.seqNum, 0, packet.ackNum)
            receiver.socket.close()
            print("connection closed, file received succesfully")
            

f = open("Receiver_log.txt", "a+")
f.write("\n")
size = "Amount of data received (in Bytes)                     {}\n".format(dataProgress)
f.write(size)
segments = "Total segments received                                {}\n".format(segCount)
f.write(segments)                
dSegments = "Data segments received                                 {}\n".format(dSegCount)
f.write(dSegments)            
error = "Data segments with Bit Errors                          {}\n".format(bitErrorCount)
f.write(error)        
dupData = "Duplicate data segments received                       {}\n".format(dupCount)
f.write(dupData)       
dupACK = "Duplicate ACKs sent                                    {}\n".format(dupACKCount)
f.write(dupACK)    
        
f.close()
    
    
    
    
    
    
    
    
