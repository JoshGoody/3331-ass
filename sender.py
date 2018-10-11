import pickle
import select
import sys
import threading
import time
import random
import queue
from collections import deque



from socket import *


class PLD:
    
    def __init__(self, pDrop, pDuplicate, pCorrupt, pOrder, maxOrder, pDelay, maxDelay, seed):
        self.pDrop = float(pDrop)
        self.pDuplicate = float(pDuplicate)
        self.pCorrupt = float(pCorrupt)
        self.pOrder = float(pOrder)
        self.maxOrder = int(maxOrder)
        self.pDelay = float(pDelay)
        self.maxDelay = int(maxDelay)

        

    
    
    def drop(self):

        if (random.random() < self.pDrop):
            return True
        else:
            return False 
    
    def duplicate(self):

        if (random.random() < self.pDuplicate):
            return True
        else:
            return False
            
    def corrupt(self):

        if (random.random() < self.pCorrupt):
            return True
        else:
            return False
    
    def order(self):

        if (random.random() < self.pOrder):
            return True
        else:
            return False
            
    def delay(self):

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
        with open(self.sFile, 'rb') as f:
            data = f.read()
            f.close
            return data

    
    def receivePacket(self):
        data, addr = self.socket.recvfrom(4096)
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
    
    def createCheckSum(self, data):
        checkSum = data
        return checkSum
    
    def corruptData(self, data):
        manipLoad = bytearray(data)
        manipLoad[0] ^= 1
        corruptedData = bytes(manipLoad)
        return corruptedData
    
    
    def sendDelayedPacketLogic(self, sender, pld):
        global timeToDelay, delayedPacket, procTime, packetsInFlight, countTilSend, savedPacket, reOrderFlag, countTilSend
        while (connected == True):

            
            if (countTilSend == pld.maxOrder):
                print("sending re-ordered packet")
                sender.sendPacket(savedPacket)
                sender.log("snd/rord", time.time()-startTime, "D", savedPacket.seqNum, len(savedPacket.data), savedPacket.ackNum)
                savedPacket = None
                reOrderFlag = False
                countTilSend = 0
                #packetsInFlight += 1
            
            if (len(delayPacketDeque)!= 0):

                timeToDelay = delayTimerDeque.popleft()
                delayedPacket = delayPacketDeque.popleft()
                procTime = pTimeDeque.popleft()
                if ((time.time()-procTime)*1000 >= timeToDelay):
                    print("sent packets")
                    sender.sendPacket(delayedPacket)
                    sender.log("snd/delay", time.time()-startTime, "D", delayedPacket.seqNum, len(delayedPacket.data), delayedPacket.ackNum)
                    packetsInFlight += 1

                else:
                    delayTimerDeque.append(timeToDelay)
                    delayPacketDeque.append(delayedPacket)
                    pTimeDeque.append(procTime) 
                        
    
    def sendLogic(self, sender, pld):
        global dataSent, sendFile, waiting, transCount, segDrop, seqNum, ackNum, sendTime, windowSize, numUnAck, timerDeque, packetsInFlight, dupCount, corrupCount, savedPacket, reOrderFlag, countTilSend, reorderCount, delayCount, sleepTime, calcRTTFlag, expectedRTTNum
        while (connected == True):
           
            
            if (numUnAck < windowSize):
               #extra reorder pld stuff
                if (reOrderFlag == True):                
                    countTilSend += 1
                        
                ###create the packet to be sent
                load = sender.splitDataToLoad(sendFile, dataSent)
                checkSum = sender.createCheckSum(load)
                dataSent += len(load)
                packet = Packet(load, seqNum, ackNum, checkSum, ack = False, syn = False, fin = False, retran = False)                
                transCount += 1
                #print(packet.seqNum)
                
                
                if (calcRTTFlag == False):
                    calcRTTFlag = True
                    expectedRTTNum = seqNum
                    sendTime = time.time()*1000    
                
                ## pld module implementation, this sits seperate and does not give information to sender to figure out what has been affected by this pld scenario
                if (pld.drop() == True):
                    print("packet dropped first time")
                    sender.log("drop", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    segDrop += 1
                
                elif (pld.duplicate() == True):
                    dupCount += 1
                    packetsInFlight += 2
                    print("sent packets")
                    sender.sendPacket(packet)
                    sender.log("snd", time.time()-startTime, "D", seqNum, len(load), ackNum)
                    #dup
                    transCount += 1
                    print("packet dupped")
                    sender.sendPacket(packet)
                    sender.log("snd/DUP", time.time()-startTime, "D", seqNum, len(load), ackNum)
                
                
                elif(pld.corrupt() == True):
                    print("packet corrupted")
                    load = sender.corruptData(load)
                    corrupCount += 1
                    packet = Packet(load, seqNum, ackNum, checkSum, ack = False, syn = False, fin = False, retran = False)
                    sender.sendPacket(packet)
                    sender.log("snd/Cor", time.time()-startTime, "D", seqNum, len(load), ackNum)
                
                
                elif(pld.order() == True and reOrderFlag == False):
                    print("re-ordering")
                    reorderCount += 1
                    reOrderFlag = True
                    savedPacket = packet
                    countTilSend = 0
                    #sender.log("re-ord", time.time()-startTime, "D", seqNum, len(load), ackNum)

                    
                
                elif (pld.delay() == True):
                    print("delaying")
                    delayCount += 1
                    delayTime = random.random()*pld.maxDelay
                    delayTimerDeque.append(delayTime)
                    delayPacketDeque.append(packet)
                    procDelayTime = time.time()
                    pTimeDeque.append(procDelayTime)
                    #sender.log("delay", time.time()-startTime, "D", seqNum, len(load), ackNum)
                
                else:
                    #send packet
                    print("sent packets")
                    packetsInFlight += 1
                    sender.sendPacket(packet)
                    sender.log("snd", time.time()-startTime, "D", seqNum, len(load), ackNum)
                
                numUnAck += 1
                seqNum += len(load)
                
                if (dataSent == len(sendFile)):
                    return

    
    def receiveLogic(self, sender):
        global q, timeReTran, timeout, fileLength, sendFile, sendbase, timerDeque, transCount, segDrop, packetsInFlight, dupCount, corrupCount, savedPacket, reOrderFlag, countTilSend, reorderCount, delayCount, fastReTran, sleepTime, sendTime, calcRTTFlag, expectedRTTNum, currTime, RTT, estimateRTT, devRTT, timeout, countTilSend
        while (connected == True):

            exceptTranTime = 0

            
            try:
                print(timeout)#need to put stuff for the proper timeout implementation here
                sender.socket.settimeout(timeout/1000)
                ackPacket = sender.receivePacket()
                q.put(ackPacket)
                print("no need to retransmit")
                if (ackPacket.ackNum > fileLength):
                    return

                    

            except Exception as e:
                print("exception handled, attempting to retransmit (pending pld)")
                print(e)
                expectedRTTNum = 0
                calcRTTFlag = False
                fastReTran = 0
                timeReTran += 1
                transCount += 1
                if (reOrderFlag == True):
                    countTilSend += 1
                #timeout=timeout*2
                
                newData1 = sender.splitDataToLoad(sendFile, sendbase-1)
                checkSum = sender.createCheckSum(newData1)

                
                
                
                #pld implementation
                if (pld.drop() == True):
                    print("packet dropped in retransmission")
                    sender.log("drop", time.time()-startTime, "D", sendbase, len(newData1), ackNum)
                    
                    segDrop += 1
                
                elif (pld.duplicate() == True):
                    dupCount += 1
                    packetsInFlight += 2
                    #send packet
                    packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                    print("sent packets")
                    sender.sendPacket(packet2)
                    sender.log("snd/RXT", time.time()-startTime, "D", sendbase, len(newData1), 0)

                    #dup
                    transCount += 1
                    print("packet dupped")
                    sender.sendPacket(packet2)
                    sender.log("snd/DUP", time.time()-startTime, "D", sendbase, len(newData1), 0)

                
                elif(pld.corrupt() == True):
                    print("packet corrupted")
                    
                    newData1 = sender.corruptData(newData1)
                    
                    corrupCount += 1
                    packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = False)
                    sender.sendPacket(packet2)
                    sender.log("snd/Cor", time.time()-startTime, "D", sendbase, len(newData1), 0)
                    
                elif(pld.order() == True and reOrderFlag == False):
                    reorderCount += 1
                    reOrderFlag = True
                    savedPacket = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                    #sender.log("rord", time.time()-startTime, "D", sendbase, len(newData1), 0)

                
                elif (pld.delay() == True):
                    print("delaying")
                    delayCount += 1
                    delayTime = random.random()*pld.maxDelay
                    delayTimerDeque.append(delayTime)
                    packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                    delayPacketDeque.append(packet2)
                    procDelayTime = time.time()
                    pTimeDeque.append(procDelayTime)

                    #sender.log("del", time.time()-startTime, "D", packet2.seqNum, len(packet2.data), packet2.ackNum)
                
                else:
                    packet2 = Packet(newData1, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                    sender.sendPacket(packet2)
                    packetsInFlight += 1

                    sender.log("snd/RXT", time.time()-startTime, "D", sendbase, len(newData1), 0)
                    print("retransmission")
                

                continue


#### MAIN 

if (len(sys.argv) != 15):
    print("incorect usage, 14 arguments needed")
    exit(0)

f = open("Sender_log.txt", "w")
f.close()
seqNum = 0
ackNum = 0
sendbase = 1
numUnAck = 0
fastReTran = 0
cumAcks = 0


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
if (int(maxOrd) == 0):
    maxOrd = 1
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
delayCount = 0

##timing function
sendTime = 0
tripTime = 0
sleepTime = 20
estimateRTT = 500
devRTT = 250
timeout = estimateRTT + (int(gamma))*devRTT
delayTimer = 0
delayTimerDeque = deque()
delayPacketDeque = deque()
pTimeDeque = deque()
expectedRTTNum = 0
calcRTTFlag = False

random.seed(int(seed))
pld = PLD(pDrop, pDup, pCor, pOrd, maxOrd, pDel, maxDel, seed)
receivable = [sender.socket]
#time stuff
timerDeque = deque()
windowSize = int(sender.MWS/sender.MSS)
timesReCalculated = 0 #######################################remove

#This is incase mws is smaller than mss 
if (sender.MWS < sender.MSS):
    sender.MSS = sender.MWS
if (windowSize == 0):
    windowSize = 1

while (connectionFinished == False):
    
    
    ###send syn
    if (noConnection == True):
        #print(len(sendFile))
        print("sending syn")
        synPacket = Packet('', seqNum, ackNum, 0, ack = False, syn = True, fin = False, retran = False)
        startTime = time.time()
        sender.sendPacket(synPacket)
        transCount +=1
        synSent = True
        noConnection = False
        sender.log("snd", 0, "S", seqNum, 0, ackNum)
        
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
            delayThread = threading.Thread(target=sender.sendDelayedPacketLogic, args=[sender, pld])
            sendThread.start()
            receiveThread.start()
            delayThread.start()
        else:
            print("error in synSent flag stage")
            
        
    ###main bit of while loop for open connection
    if (connected == True):
    

        #if (q.qsize() > 0 and len(timerDeque) > 0):
        if (q.qsize() > 0):
            ackPacket = q.get()
        else: 
            continue
        
        ackNum = ackPacket.seqNum + 1

        
        
        if (ackPacket.ackNum > fileLength):
            print("correct acknowledgment received")
            sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)           
            print("everything received, file ready, fin sent")
            sender.socket.settimeout(None)
            connected = False
            finSent = True           
            finPacket = Packet('', seqNum, ackNum, 0, ack = False, syn = False, fin = True, retran = False)
            sender.sendPacket(finPacket)
            sender.log("snd", time.time()-startTime, "F", seqNum, 0, ackNum)
            transCount +=1
            time.sleep(0.1)
            continue
        

        else :
            if (ackPacket.ack == True and ackPacket.ackNum > sendbase):
                print("correct acknowledgment received")
                #####################################################################maybe make better
                #timer stuff

                if (calcRTTFlag == True and ackPacket.ackNum > expectedRTTNum):
                    expectedRTTNum = 0
                    calcRTTFlag = False
                    if (ackPacket.retran == False):
                        timesReCalculated += 1
                        currTime = time.time()*1000
                    
                        RTT = currTime - sendTime
                        estimateRTT = 0.875*estimateRTT + 0.125*RTT
                        devRTT = 0.75*devRTT + 0.25*abs(RTT - estimateRTT)
                        timeout = estimateRTT + (int(gamma))*devRTT
                        if (timeout < 145):
                            timeout = 145
  
                ###cumack updates the unacknowledged number to the sender can send more packets (i.e dont ack 1 ack cum ack amount)
                sender.log("rcv", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
                cumAcks = int((ackPacket.ackNum-sendbase)/sender.MSS)
                numUnAck -= cumAcks
                sendbase = ackPacket.ackNum
                fastReTran = 0
                ##do what you need to do when an ack is received from the receiver
            
            elif (ackPacket.ackNum == sendbase):
                dupAckno += 1
                fastReTran += 1
                sender.log("rcv/DA", time.time()-startTime, "A", ackPacket.seqNum, 0, ackPacket.ackNum)
                if (fastReTran == 3):
                    expectedRTTNum = 0
                    calcRTTFlag = False
                    transCount += 1
                    if (reOrderFlag == True):
                        countTilSend += 1
                    #sendbase-1 because the ack is next expected data, not the last data point
                    newData = sender.splitDataToLoad(sendFile, sendbase-1)   
                    checkSum = sender.createCheckSum(newData)
                    
                    
                    print("retransmitting pending fast retran pld")
                    
                    #pld implemntation 
                    if (pld.drop() == True):
                        print("packet dropped in retransmission")
                        sender.log("FRdrop", time.time()-startTime, "D", sendbase, len(newData), ackNum)
                        segDrop += 1
                    
                    elif (pld.duplicate() == True):
                        dupCount += 1
                        packetsInFlight += 2
                        #send packet
                        packet2 = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        print("sent packets")
                        sender.sendPacket(packet2)
                        sender.log("snd/RXT", time.time()-startTime, "D", sendbase, len(newData), 0)
                        #dup
                        transCount += 1
                        print("packet dupped")
                        sender.sendPacket(packet2)
                        sender.log("snd/DUP", time.time()-startTime, "D", sendbase, len(newData), 0)

                    
                    elif(pld.corrupt() == True):
                        print("packet corrupted")
                        newData = sender.corruptData(newData)
                            
                        corrupCount += 1
                        packet2 = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.sendPacket(packet2)
                        sender.log("snd/R/Cor", time.time()-startTime, "D", sendbase, len(newData), 0)
                    
                    elif(pld.order() == True and reOrderFlag == False):
                        reorderCount += 1
                        reOrderFlag = True
                        savedPacket = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        #sender.log("rord", time.time()-startTime, "D", sendbase, len(newData), 0)

                    
                    elif (pld.delay() == True):
                        print("delaying")
                        delayCount += 1
                        delayTime = random.random()*pld.maxDelay
                        delayTimerDeque.append(delayTime)
                        packet2 = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        delayPacketDeque.append(packet2)
                        procDelayTime = time.time()
                        pTimeDeque.append(procDelayTime)

                        #sender.log("del", time.time()-startTime, "D", packet2.seqNum, len(packet2.data), packet2.ackNum)
                    
                    else: 
                        packetsInFlight += 1
                        packet = Packet(newData, sendbase, 0, checkSum, ack = False, syn = False, fin = False, retran = True)
                        sender.sendPacket(packet)

                        sender.log("snd/RXT", time.time()-startTime, "D", sendbase, len(newData), 0)
                        print("retransmission")
                    fastReTran = 0
                    fastLogCount += 1
                
                
        
       
        
        
            
        
    if (finSent == True):
        sender.socket.settimeout(1.2)
        
        try:
            ackPacket3 = sender.receivePacket()
        except Exception as e:
        #############################################shouldnt happen
            print("shouldnt happen")
            sender.log("rcv", time.time()-startTime, "F", finPacket.seqNum, 0, finPacket.ackNum)
            finSent = False
            ackPacket = Packet('', ackNum, seqNum, 0, ack = True, syn = False, fin = False, retran = False)
            sender.sendPacket(ackPacket)
            sender.log("snd", time.time()-startTime, "A", seqNum, 0, ackNum)
            transCount +=1
            pldCount = transCount - 4
            print("connection terminated and fin completed")
            #print(len(timerDeque))
            #print(q.qsize())
            #print(timesReCalculated)
            connectionFinished = True
            break
            
            
        time.sleep(0.1)
        if (ackPacket3.ack == True and ackPacket3.fin == False):
            print("fin acknowledgment received")
            sender.log("rcv", time.time()-startTime, "A", ackPacket3.seqNum, 0, ackPacket3.ackNum)
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
                #print(len(timerDeque))
                #print(q.qsize())
                #print(timesReCalculated)
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
delay = "Number of Segments Delayed                               {}\n".format(delayCount)
f.write(delay)    	
timeout = "Number of Retransmissions due to TIMEOUT                 {}\n".format(timeReTran)
f.write(timeout)
fast = "Number of FAST RETRANSMISSION                            {}\n".format(fastLogCount)
f.write(fast)
dupAck = "Number of DUP ACKS received                              {}\n".format(dupAckno)
f.write(dupAck)		
		
f.close()		
		
		
