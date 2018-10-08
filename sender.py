import pickle
import select
import sys
import threading
import time
import random
import queue
from collections import deque

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

    def __init__(self, data, seqNum, ackNum, checksum, ack=False, syn=False, fin=False, retran=False):

        self.data = data
        self.seqNum = seqNum
        self.ackNum = ackNum
        self.checksum = checksum
        self.ack = ack
        self.syn = syn
        self.fin = fin
        self.retran = retran
        
	
		
	
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
        self.maxOrd = int(maxOrd)
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
    
    def sendLogic(self, sender, pld):
        while (connected == True):
            global dataSent, sendFile, waiting, transCount, segDrop, seqNum, ackNum, sendTime, windowSize, numUnAck, timerDeque, packetsInFlight, dupCount, corrupCount, savedPacket, reOrderFlag, countTilSend, reorderCount 
            if (numUnAck < windowSize):
               #extra reorder pld stuff
                if (reOrderFlag == True):
                    
                    if (countTilSend == pld.maxOrder):
                        sender.sendPacket(savedPacket)
                        sender.log("snd/rord", time.time()-startTime, "D", savedPacket.seqNum, len(savedPacket.data), savedPacket.ackNum)
                        #transCount +=1
                        #sendTime = time.time()*1000 
                        #timerDeque.append(sendTime)
                        savedPacket = None
                        reOrderFlag = False
                        countTilSend = 0
                    
                    countTilSend += 1
                        
                ###create the packet to be sent
                load = sender.splitDataToLoad(sendFile, dataSent)
                #if needed undo this shit
                #print(seqNum)
                #print(load)
                checkSum = bytearray(load, 'utf8')
                #~checkSum[0]
                #print(checkSum)
                #for i in range(len(checkSum)): 
                    #print(i)
                    #~checkSum[i]
                    
                #print(checkSum)
                dataSent += len(load)
                ## maybe need to increment sequence number here?
                packet = Packet(load, seqNum, ackNum, checkSum, ack = False, syn = False, fin = False, retran = False)
                #waiting = waiting + 1
                ## pld module implementation
                packetsInFlight += 1
                transCount += 1
                if (pld.drop() == True):
                    print("packet dropped first time")
                    sender.log("drop", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    #transCount += 1
                    segDrop += 1
                
                elif (pld.duplicate() == True):
                    dupCount += 1
                    packetsInFlight += 1
                    #send packet
                    print("sent packets")
                    #print(len(packet.data), packet.seqNum)
                    sender.sendPacket(packet)
                    sender.log("snd", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    #transCount +=1
                    sendTime = time.time()*1000 
                    timerDeque.append(sendTime)
                    #dup
                    print("packet dupped")
                    sender.sendPacket(packet)
                    sender.log("snd/DUP", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    sendTime = time.time()*1000 
                    timerDeque.append(sendTime)
                
                
                elif(pld.corrupt() == True):
                    print("packet corrupted")
                    manipLoad = bytearray(load, 'utf8')
                    manipLoad[0] ^= 1
                    load = manipLoad.decode('utf8')
                    corrupCount += 1
                    packet = Packet(load, seqNum, ackNum, checkSum, ack = False, syn = False, fin = False, retran = False)
                    sender.sendPacket(packet)
                    sender.log("snd/Cor", time.time()-startTime, "D", seqNum, len(load), ackNum)
                
                
                elif(pld.order() == True and reOrderFlag == False):
                    reorderCount += 1
                    reOrderFlag = True
                    savedPacket = packet
                    countTilSend = 0
                    sender.log("rord", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    sendTime = time.time()*1000 
                    timerDeque.append(sendTime)
                
                else:
                    #send packet
                    print("sent packets")
                    #print(len(packet.data), packet.seqNum)
                    sender.sendPacket(packet)
                    sender.log("snd", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    #transCount +=1
                    sendTime = time.time()*1000 
                    timerDeque.append(sendTime)
                #sendTime = time.time()*1000 
                #timerDeque.append(sendTime)
                #print("timer deque incremented")
                
                numUnAck += 1
                seqNum += len(load)
                #transCount = transCount + 1
                
                if (dataSent == len(sendFile)):
                    return
                #elif (ready == True):
                    #print("bug discovered")
                
                #else:
                    #if (pld.drop() == True):
                        #print("packet dropped second time")
                        #sender.log("drop", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                        #transCount += 1
                        #segDrop += 1
                    #else:
                        #send packet
                        #print("sent retransmitted packets")
                        #print(len(packet.data), packet.seqNum)
                        #sender.sendPacket(packet)
                        #sender.log("snd/RXT", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                        #transCount +=1
                    #sendTime = time.clock()*1000
                #time.sleep(1)
    
    def receiveLogic(self, sender):
        while (connected == True):
            exceptTranTime = 0
            global q, timeReTran, timeout, fileLength, sendFile, sendbase, timerDeque, transCount, segDrop, packetsInFlight, dupCount, corrupCount, savedPacket, reOrderFlag, countTilSend, reorderCount 
            #fix so finsh with zero
            if (packetsInFlight > 0):
                try:
                    print(timeout)
                    sender.socket.settimeout(timeout/1000)
                    #sender.socket.settimeout(2)
                    #print("i am stuck help me")
                    ackPacket = sender.receivePacket()
                    #packetsInFlight -= 1
                    q.put(ackPacket)
                    print("no need to retransmit")
                    if (ackPacket.ackNum > fileLength):
                        return
                    packetsInFlight -= 1
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
                    #need to put through pld as well
                    #print(e)
                    #dequePoper = timerDeque.popleft()       #might need to add on later
                    print("exception handled, attempting to retransmit (pending pld)")
                    timeReTran += 1
                    transCount += 1
                    #numUnAck += 1
                    #might need to add or minus a packet in flight beause of pDrop stuff
                    packetsInFlight += 1
                    newData1 = sender.splitDataToLoad(sendFile, sendbase-1)
                    checkSum = bytearray(newData1, 'utf8')
                    #for i in range(len(checkSum)): 
                        #~checkSum[i]
                    if (pld.drop() == True):
                        print("packet dropped in retransmission")
                        sender.log("TRdrop", time.time()-startTime, "D", sendbase, len(newData1), ackNum)
                        
                        segDrop += 1
                    
                    elif (pld.duplicate() == True):
                        dupCount += 1
                        packetsInFlight += 1
                        #send packet
                        packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        print("sent packets")
                        #print(len(packet.data), packet.seqNum)
                        sender.sendPacket(packet2)
                        sender.log("snd/RXTT", time.time()-startTime, "D", sendbase, len(newData1), 0)
                        exceptTranTime = time.time()*1000 
                        timerDeque.append(exceptTranTime)
                        #transCount +=1
                        #dup
                        print("packet dupped")
                        sender.sendPacket(packet2)
                        sender.log("snd/DUP", time.time()-startTime, "D", sendbase, len(newData1), 0)
                        exceptTranTime = time.time()*1000 
                        timerDeque.append(exceptTranTime)
                    
                    elif(pld.corrupt() == True):
                        print("packet corrupted")
                        manipLoad = bytearray(newData1, 'utf8')
                        manipLoad[0] ^= 1
                        load = manipLoad.decode('utf8')
                        
                        corrupCount += 1
                        packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = False)
                        sender.sendPacket(packet2)
                        sender.log("snd/Cor", time.time()-startTime, "D", sendbase, len(newData1), 0)
                        
                    elif(pld.order() == True and reOrderFlag == False):
                        reorderCount += 1
                        reOrderFlag = True
                        savedPacket = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.log("rord", time.time()-startTime, "D", sendbase, len(newData1), 0)
                        exceptTranTime = time.time()*1000
                        timerDeque.append(exceptTranTime)
                    
                    else:
                        packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.sendPacket(packet2)
                        exceptTranTime = time.time()*1000
                        timerDeque.append(exceptTranTime)
                        sender.log("snd/RXTT", time.time()-startTime, "D", sendbase, len(newData1), 0)
                        print("retransmission")
                    
                    #exceptTranTime = time.time()*1000
                    #timerDeque.append(exceptTranTime)
                    continue
            #time.sleep(1)

#### MAIN 

if (len(sys.argv) != 15):
    print("incorect usage, 14 arguments needed")
    exit(0)

f = open("Sender_log.txt", "w")
f.close()
f = open("test0_copy.pdf", "w")
f.close()
seqNum = 0
ackNum = 0
sendbase = 1
numUnAck = 0
fastReTran = 0
cumAcks = 0
#expectedAck = 0

# different states of operation
noConnection = True
synSent = False
connected = False
finSent = False
connectionFinished = False
ready = False

#reordering stuff
savedPacket = None
reOrderFlag = False
countTilSend = 0

q = queue.Queue(maxsize=0)
sendQ = queue.Queue(maxsize=0)
untranCount = 0
dropCount = 0
packetsInFlight = 0
#waiting = 0
rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed = sys.argv[1:]
###sener is initiated

sender = Sender(rHostIp, recPort, sFile, MWS, MSS, gamma,pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
sendFile = sender.pullFile()
fileLength = len(sendFile)
dataSent = 0

#log trackers
segDrop = 0
transCount = 0
timeReTran = 0
fastLogCount = 0
dupCount = 0
dupAckno = 0
corrupCount = 0
reorderCount = 0

##timing function
estimateRTT = 500
devRTT = 250
timeout = estimateRTT + (int(gamma))*devRTT

random.seed(int(seed))
pld = PLD(pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
receivable = [sender.socket]
#time stuff
timerDeque = deque()
startTime = time.time()
sendTime = 0
tripTime = 0
windowSize = int(sender.MWS/sender.MSS)
#print(windowSize)
###################################################################### to fix Change MSS to MWS if MWS < MSS 
if (sender.MWS < sender.MSS):
    sender.MSS = sender.MWS
if (windowSize == 0):
    windowSize = 1
#print(windowSize)
while (connectionFinished == False):
    
    
    ###send syn
    if (noConnection == True):
        print("sending syn")
        synPacket = Packet('', seqNum, ackNum, 0, ack = False, syn = True, fin = False, retran = False)
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
            
            ackPacket = Packet('', seqNum, ackNum, 0, ack = True, syn = False, fin = False, retran = False)
            sender.sendPacket(ackPacket)
            transCount +=1
            synSent = False
            connected = True
            sender.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
            print("sent ack, starting file transfer")
            sendThread = threading.Thread(target=sender.sendLogic, args=[sender,pld])
            receiveThread = threading.Thread(target=sender.receiveLogic, args=[sender])
            print(sender.pDrop)
            print(sender.pDup)
            print(sender.pCor)
            sendThread.start()
            receiveThread.start()
        else:
            print("error in synSent flag stage")
            
        
    ###main bit of while loop for open connection
    if (connected == True):
    
        #if (waiting == 0 and ready == False):
            ###create the packet to be sent
            #load = sender.splitDataToLoad(sendFile, dataSent)
            #dataSent += len(load)
            ## maybe need to increment sequence number here?
            #packet = Packet(load, seqNum, ackNum, ack = False, syn = False, fin = False)
            #waiting = waiting + 1
            ## this is where pld module will go ventually
            #if (pld.drop() == True):
                #print("packet dropped first time")
                #sender.log("drop", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                #transCount += 1
                #segDrop += 1
            #else:
                #send packet
                #print("sent packets")
                #print(len(packet.data), packet.seqNum)
                #sender.sendPacket(packet)
                #sender.log("snd", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                #transCount +=1
            #sendTime = time.clock()*1000 
            
            #seqNum += len(load)
            #transCount = transCount + 1
        #elif (ready == True):
            #print("bug discovered")
        
        #else:
            #if (pld.drop() == True):
                #print("packet dropped second time")
                #sender.log("drop", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                #transCount += 1
                #segDrop += 1
            #else:
                #send packet
                #print("sent retransmitted packets")
                #print(len(packet.data), packet.seqNum)
                #sender.sendPacket(packet)
                #sender.log("snd/RXT", time.time()-startTime, "D", seqNum, dataSent, ackNum)
                #transCount +=1
            #sendTime = time.clock()*1000
        
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
        #try:
            #sender.socket.settimeout(timeout/1000)
            #print("i am stuck help me")
            #ackPacket = sender.receivePacket()
            #print("no need to retransmit")
            #ackNum = ackPacket.seqNum + 1
            #sender.socket.settimeout(none)
            #currTime = time.clock()*1000
            #RTT = currTime - sendTime
            #estimateRTT = 0.875*estimateRTT + 0.125*RTT
            #devRTT = 0.75*devRTT + 0.25*abs(RTT - estimateRTT)
            #timeout = estimateRTT + (int(gamma))*devRTT
        #except socket.timeout:
        #except Exception as e:
            #retransmit
            #print("exception handled, retransmitting")
            #timeReTran += 1
            #continue
        #print(" q size " + str(q.qsize()))
        #print("timer deque soze " + str(len(timerDeque)))
        #print(packetsInFlight)
        if (q.qsize() > 0 and len(timerDeque) > 0):
            ackPacket = q.get()
            tripTime = timerDeque.popleft()
        elif (q.qsize() > 0 and len(timerDeque) == 0 and dataSent >= fileLength):
            ackPacket = q.get()
            print("finishing sequence should always initiate after this")
        else: 
            continue
        
        ackNum = ackPacket.seqNum + 1
        ##sender.socket.settimeout(none)
        #currTime = time.clock()*1000
        #RTT = currTime - sendTime
        #estimateRTT = 0.875*estimateRTT + 0.125*RTT
        #devRTT = 0.75*devRTT + 0.25*abs(RTT - estimateRTT)
        #timeout = estimateRTT + (int(gamma))*devRTT 
        #print(timeout)   
        #waiting = waiting - 1
        
        
        if (ackPacket.ackNum > fileLength):
            print("correct acknowledgment received")
            sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)           
            print("everything received, file ready, fin sent")
            #sendThread.cancel()
            #receiveThread.cancel()
            sender.socket.settimeout(None)
            finSent = True
            connected = False
            finPacket = Packet('', seqNum, ackNum, 0, ack = False, syn = False, fin = True, retran = False)
            sender.sendPacket(finPacket)
            sender.log("snd", time.time()-startTime, "F", seqNum, 0, ackNum)
            transCount +=1
        
        #nned to fix this as seqNum is changing to early
        #print(ackPacket.ackNum)
        #print(seqNum)
        #print(ackPacket.ackNum)
        #print(sendbase)
        #print(fastReTran)
        #print("timer deque")
        #print(len(timerDeque))
        #if(len(timerDeque) != 0):
        #tripTime = timerDeque.popleft()
        else :
            if (ackPacket.ack == True and ackPacket.ackNum > sendbase):
                print("correct acknowledgment received")
                
                #timer stuff
                if (ackPacket.retran == False):
                    currTime = time.time()*1000
                    
                    RTT = currTime - tripTime
                    estimateRTT = 0.875*estimateRTT + 0.125*RTT
                    devRTT = 0.75*devRTT + 0.25*abs(RTT - estimateRTT)
                    timeout = estimateRTT + (int(gamma))*devRTT 
                    #print("checking time stuff")
                    #print(ackPacket.ackNum)
                    #print(tripTime)
                    #print(RTT)
                    #print(timeout)  
                
                sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
                cumAcks = int((ackPacket.ackNum-sendbase)/sender.MSS)
                #print(cumAcks)
                numUnAck -= cumAcks
                sendbase = ackPacket.ackNum
                fastReTran = 0
                ##do what you need to do when an ack is received from the receiver
            
            elif (ackPacket.ackNum == sendbase):
                dupAckno += 1
                fastReTran += 1
                sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
                if (fastReTran == 3):
                    #maybe get rid and go back to other time method
                    #reTranPoper = timerDeque.popleft()
                    transCount += 1
                    newData = sender.splitDataToLoad(sendFile, sendbase-1)   ####(should be sendbase -1)
                    checkSum = bytearray(newData, 'utf8')
                    
                    #for i in range(len(checkSum)): 
                            #~checkSum[i]
                    #numUnAck += 1
                    packetsInFlight += 1
                    print("retransmitting pending fast retran pld")
                    if (pld.drop() == True):
                        print("packet dropped in retransmission")
                        sender.log("FRdrop", time.time()-startTime, "D", sendbase, len(newData), ackNum)
                        segDrop += 1
                    
                    elif (pld.duplicate() == True):
                        dupCount += 1
                        packetsInFlight += 1
                        #send packet
                        packet2 = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        print("sent packets")
                        #print(len(packet.data), packet.seqNum)
                        sender.sendPacket(packet2)
                        sender.log("snd/RXTF", time.time()-startTime, "D", sendbase, len(newData), 0)
                        retrantime = time.time()*1000 
                        timerDeque.append(retrantime)
                        #transCount +=1
                        #dup
                        print("packet dupped")
                        sender.sendPacket(packet2)
                        sender.log("snd/DUP", time.time()-startTime, "D", sendbase, len(newData), 0)
                        retrantime = time.time()*1000 
                        timerDeque.append(retrantime)
                    
                    elif(pld.corrupt() == True):
                        print("packet corrupted")
                        manipLoad = bytearray(newData, 'utf8')
                        manipLoad[0] ^= 1
                        load = manipLoad.decode('utf8')
                            
                        corrupCount += 1
                        packet2 = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.sendPacket(packet2)
                        sender.log("snd/R/Cor", time.time()-startTime, "D", sendbase, len(newData), 0)
                    
                    elif(pld.order() == True and reOrderFlag == False):
                        reorderCount += 1
                        reOrderFlag = True
                        savedPacket = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.log("rord", time.time()-startTime, "D", sendbase, len(newData), 0)
                        retrantime = time.time()*1000
                        timerDeque.append(retrantime)
                    
                    else: 
                    #implement pld here as well
                        
                        packet = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.sendPacket(packet)
                        retrantime = time.time()*1000
                        timerDeque.append(retrantime)
                        sender.log("snd/RXTF", time.time()-startTime, "D", sendbase, len(newData), 0)
                        print("retransmission")
                    #retrantime = time.time()*1000
                    #timerDeque.append(retrantime)
                    fastReTran = 0
                    fastLogCount += 1
                
                
        
       
        
        
            
        
    if (finSent == True):
        #sender.socket.settimeout(3)
        ackPacket1 = sender.receivePacket()
        if (ackPacket1.ack == True and ackPacket1.fin == False):
            print("fin acknowledgment received")
            sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
            finPacket = sender.receivePacket() 
            ackNum = ackNum + 1
            
            if (finPacket.fin == True):
                sender.log("rcv", time.time()-startTime, "F", finPacket.seqNum, 0, finPacket.ackNum)
                finSent = False
                ackPacket = Packet('', ackNum, seqNum, 0, ack = True, syn = False, fin = False, retran = False)
                sender.sendPacket(ackPacket)
                sender.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
                transCount +=1
                pldCount = transCount - 4
                print("connection terminated and fin completed")
                print(len(timerDeque))
                print(q.qsize())
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
corrupted = "Number of Segments Corrupted                             {}\n".format(corrupCount)
f.write(corrupted)       
order = "Number of Segments Re-ordered                            {}\n".format(reorderCount)
f.write(order)    
dup = "Number of Segments Duplicated                            {}\n".format(dupCount)
f.write(dup)        
delay = "Number of Segments Delayed                               {}\n".format(0)
f.write(delay)    	
timeout = "Number of Retransmissions due to TIMEOUT                 {}\n".format(timeReTran)
f.write(timeout)
fast = "Number of FAST RETRANSMISSION                            {}\n".format(fastLogCount)
f.write(fast)
dupAck = "Number of DUP ACKS received                              {}\n".format(dupAckno)
f.write(dupAck)		
		
f.close()		
		
		
