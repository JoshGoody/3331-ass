import pickle
import select
import sys
import threading
import time
import random
import queue

#from random import *

from socket import *

#print(random.random())
#print(type(random)) 
class PLD:
    
    def __init__(self, pDrop, pDuplicate, pCorrupt, pOrder, maxOrder, pDelay, maxDelay, seed):
        self.pDrop = float(pDrop)
        self.pDuplicate = float(pDuplicate)
        self.pCorrupt = float(pCorrupt)
        self.pOrder = float(pOrder)
        self.maxOrder = int(maxOrder)
        self.pDelay = float(pDelay)
        self.maxDelay = int(maxDelay)
        #self.seed = int(seed)
        
    #random = random()
    
    
    def drop(self):
        #chance random.random()
        if (random.random() < self.pDrop):
            return True
        else:
            return False 
    
    def duplicate(self):
        #chance random.random()
        if (random.random() < self.pDuplicate):
            return True
        else:
            return False
            
    def corrupt(self):
        #chance random.random()
        if (random.random() < self.pCorrupt):
            return True
        else:
            return False
    
    def order(self):
        #chance random.random()
        if (random.random() < self.pOrder):
            return True
        else:
            return False
            
    def delay(self):
        #chance random.random()
        if (random.random() < self.pDelay):
            return True
        else:
            return False

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
        f = open("Sender_log.txt", "a+")
        f.write(log)
        f.close()
    
    def sendLogic(self):
        print(" ")
    
    def receiveLogic(self):
        print(" ")

#### MAIN 

if (len(sys.argv) != 15):
    print("incorect usage, 14 arguments needed")
    exit(0)

f = open("Sender_log.txt", "w")
f.close()
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
ready = False


timeReTran = 0
segDrop = 0
transCount = 0
untranCount = 0
dropCount = 0
waiting = 0
rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed = sys.argv[1:]

###sener is initiated

sender = Sender(rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
sendFile = sender.pullFile()
fileLength = len(sendFile)
dataSent = 0

##timing function
estimateRTT = 500
devRTT = 250
timeout = estimateRTT + (int(gamma))*devRTT

random.seed(int(seed))
pld = PLD(pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
receivable = [sender.socket]
startTime = time.time()
while (connectionFinished == False):
    
    
    ###send syn
    if (noConnection == True):
        print("sending syn")
        synPacket = Packet('', seqNum, ackNum, ack = False, syn = True, fin = False)
        #print(synPacket.seqNum)
        sender.sendPacket(synPacket)
        transCount +=1
        synSent = True
        noConnection = False
        sender.log("snd", time.time()-startTime, "S", seqNum, 0, ackNum)
        
    if (synSent == True):
        print("waiting for synAck")
        synAckPacket = sender.receivePacket()
        
        if (synAckPacket.ack == True and synAckPacket.syn == True):
            sender.log("rcv", time.time()-startTime, "SA", synAckPacket.seqNum, 0, synAckPacket.ackNum)
            ackNum = synAckPacket.seqNum + 1
            seqNum = seqNum + 1
            
            ackPacket = Packet('', seqNum, ackNum, ack = True, syn = False, fin = False)
            sender.sendPacket(ackPacket)
            transCount +=1
            synSent = False
            connected = True
            sender.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
            print("sent ack, starting file transfer")
        else:
            print("error in synSent flag stage")
            
        
    ###main bit of while loop for open connection
    if (connected == True):
    
        if (waiting == 0 and ready == False):
            ###create the packet to be sent
            load = sender.splitDataToLoad(sendFile, dataSent)
            dataSent += len(load)
            ## maybe need to increment sequence number here?
            packet = Packet(load, seqNum, ackNum, ack = False, syn = False, fin = False)
            waiting = waiting + 1
            ## this is where pld module will go ventually
            if (pld.drop() == True):
                print("packet dropped first time")
                sender.log("drop", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                transCount += 1
                segDrop += 1
            else:
                #send packet
                print("sent packets")
                #print(len(packet.data), packet.seqNum)
                sender.sendPacket(packet)
                sender.log("snd", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                transCount +=1
            sendTime = time.clock()*1000 
            
            seqNum += len(load)
            transCount = transCount + 1
        elif (ready == True):
            print("bug discovered")
        
        else:
            if (pld.drop() == True):
                print("packet dropped second time")
                sender.log("drop", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                transCount += 1
                segDrop += 1
            else:
                #send packet
                print("sent retransmitted packets")
                #print(len(packet.data), packet.seqNum)
                sender.sendPacket(packet)
                sender.log("snd/RXT", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                transCount +=1
            sendTime = time.clock()*1000
        
        #read,write,excep = select.select(receivable,receivable,[],0)
        #if (len(write)==0 and dataSent != fileLength):
            #ready = True
            #continue
        #print(len(receivable))
        #print(len(read))
        #for r in read:
            #print("           there is receivable data, call receivepacket function")
            #if r is sender.socket:
                #print("           there is receivable data, call receivepacket function")
        ##receive same packet
        try:
            sender.socket.settimeout(timeout/1000)
            #print("i am stuck help me")
            ackPacket = sender.receivePacket()
            print("no need to retransmit")
            #ackNum = ackPacket.seqNum + 1
            #sender.socket.settimeout(none)
            #currTime = time.clock()*1000
            #RTT = currTime - sendTime
            #estimateRTT = 0.875*estimateRTT + 0.125*RTT
            #devRTT = 0.75*devRTT + 0.25*abs(RTT - estimateRTT)
            #timeout = estimateRTT + (int(gamma))*devRTT
        #except socket.timeout:
        except Exception as e:
            #retransmit
            print("exception handled, retransmitting")
            timeReTran += 1
            continue
        
        ackNum = ackPacket.seqNum + 1
        #sender.socket.settimeout(none)
        currTime = time.clock()*1000
        RTT = currTime - sendTime
        estimateRTT = 0.875*estimateRTT + 0.125*RTT
        devRTT = 0.75*devRTT + 0.25*abs(RTT - estimateRTT)
        timeout = estimateRTT + (int(gamma))*devRTT 
        print(timeout)   
        waiting = waiting - 1
        if (ackPacket.ack == True and ackPacket.ackNum == seqNum):
            print("correct acknowledgment received")
            sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
            ##do what you need to do when an ack is received from the receiver
        
        if (dataSent == fileLength):
            print("everything received, file ready, fin sent")
            finSent = True
            connected = False
            finPacket = Packet('', seqNum, ackNum, ack = False, syn = False, fin = True)
            sender.sendPacket(finPacket)
            sender.log("snd", time.time()-startTime, "F", seqNum, 0, ackNum)
            transCount +=1

    if (finSent == True):
        ackPacket = sender.receivePacket()
        if (ackPacket.ack == True and ackPacket.fin == False):
            print("fin acknowledgment received")
            sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
            finPacket = sender.receivePacket() 
            ackNum = ackNum + 1
            
            if (finPacket.fin == True):
                sender.log("rcv", time.time()-startTime, "F", finPacket.seqNum, 0, finPacket.ackNum)
                finSent = False
                ackPacket = Packet('', ackNum, seqNum, ack = True, syn = False, fin = False)
                sender.sendPacket(ackPacket)
                sender.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
                transCount +=1
                pldCount = transCount - 4
                print("connection terminated and fin completed")
                connectionFinished = True
    
sender.socket.close()
    
f = open("Sender_log.txt", "a+")
f.write("\n")
size = "Size of the file (in Bytes)                            {}\n".format(fileLength)
f.write(size)
segments = "Segments transmitted (including drop & RXT)             {}\n".format(transCount)
f.write(segments)                
pld = "Number of Segments handled by PLD                       {}\n".format(pldCount)
f.write(pld)            
dropped = "Number of Segments dropped                               {}\n".format(segDrop)
f.write(dropped)        
corrupted = "Number of Segments Corrupted                             {}\n".format(0)
f.write(corrupted)       
order = "Number of Segments Re-ordered                            {}\n".format(0)
f.write(order)    
dup = "Number of Segments Duplicated                            {}\n".format(0)
f.write(dup)        
delay = "Number of Segments Delayed                               {}\n".format(0)
f.write(delay)    	
timeout = "Number of Retransmissions due to TIMEOUT                 {}\n".format(timeReTran)
f.write(timeout)
fast = "Number of FAST RETRANSMISSION                            {}\n".format(0)
f.write(fast)
dupAck = "Number of DUP ACKS received                              {}\n".format(0)
f.write(dupAck)		
		
		
		
		
