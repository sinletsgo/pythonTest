import hashlib
import time
import csv
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse
import threading
import cgi
import uuid
from tempfile import NamedTemporaryFile
import shutil
import requests # for sending new block to other nodes

PORT_NUMBER = 8099
g_txFileName = "txData.csv"
g_bcFileName = "blockchain.csv"
g_nodelstFileName = "nodelst.csv"
g_receiveNewBlock = "/node/receiveNewBlock"
g_nodeList = {} # server list should be checked once in a month (will be implemented asap)

class Block:

    # A basic block contains, index (blockheight), the previous hash, a timestamp, tx information, a nonce, and the current hash

    def __init__(self, index, previousHash, timestamp, data, currentHash, proof ):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.data = data
        self.currentHash = currentHash
        self.proof = proof

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

class txData:

    def __init__(self, commitYN, sender, amount, receiver, uuid):
        self.commitYN = commitYN
        self.sender = sender
        self.amount = amount
        self.receiver = receiver
        self.uuid =  uuid



def generateGenesisBlock():
    print("generateGenesisBlock is called")
    timestamp = time.time()
    print("time.time() => %f \n" % timestamp)
    tempHash = calculateHash(0, '0', timestamp, "My very first block :)", 0)
    print(tempHash)
    return Block(0, '0', timestamp, "My very first block",  tempHash,0)
    # return Block(0, '0', '1496518102.896031', "My very first block :)", 0, '02d779570304667b4c28ba1dbfd4428844a7cab89023205c66858a40937557f8')

def calculateHash(index, previousHash, timestamp, data, proof):
    value = str(index) + str(previousHash) + str(timestamp) + str(data) + str(proof)
    sha = hashlib.sha256(value.encode('utf-8'))
    return str(sha.hexdigest())

def calculateHashForBlock(block):
    return calculateHash(block.index, block.previousHash, block.timestamp, block.data, block.proof)

def getLatestBlock(blockchain):
    return blockchain[len(blockchain) - 1]

def generateNextBlock(blockchain, blockData, timestamp, proof):
    previousBlock = getLatestBlock(blockchain)
    nextIndex = int(previousBlock.index) + 1
    nextTimestamp = timestamp
    nextHash = calculateHash(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, proof)
    # index, previousHash, timestamp, data, currentHash, proof
    return Block(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, nextHash,proof)

def writeBlockchain(blockchain):
    blockchainList = []

    for block in blockchain:
        blockList = [block.index, block.previousHash, str(block.timestamp), block.data, block.currentHash,block.proof ]
        blockchainList.append(blockList)

    with open(g_bcFileName, "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(blockchainList)

    # update txData cause it has been mined.
    for block in blockchain:
        updateTx(block)

    print('Blockchain written to blockchain.csv.')
    print('Broadcasting new block to other nodes')
    broadcastNewBlock(blockchain)

def readBlockchain(blockchainFilePath, mode = 'internal'):
    print("readBlockchain")
    importedBlockchain = []

    try:
        with open(blockchainFilePath, 'r',  newline='') as file:
            blockReader = csv.reader(file)
            for line in blockReader:
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                importedBlockchain.append(block)

        print("Pulling blockchain from csv...")

        return importedBlockchain

    except:
        if mode == 'internal' :
            return [generateGenesisBlock()]
        else :
            return None

def updateTx(blockData) :

    phrase = re.compile(r"\w+[-]\w+[-]\w+[-]\w+[-]\w+") # [6b3b3c1e-858d-4e3b-b012-8faac98b49a8]UserID hwang sent 333 bitTokens to UserID kim.
    matchList = phrase.findall(blockData.data)

    if len(matchList) == 0 :
        print ("No Match Found! " + blockData.data + "block idx: " + blockData.index)
        return

    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)

    with open(g_txFileName, 'r') as csvfile, tempfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(tempfile)
        for row in reader:
            if row[4] in matchList:
                print('updating row : ', row[4])
                row[0] = 1
            writer.writerow(row)

    shutil.move(tempfile.name, g_txFileName)
    csvfile.close()
    tempfile.close()
    print('txData updated')

def writeTx(txRawData):
    print(g_txFileName)
    txDataList = []
    for txDatum in txRawData:
        txList = [txDatum.commitYN, txDatum.sender, txDatum.amount, txDatum.receiver, txDatum.uuid]
        txDataList.append(txList)

    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)
    try:
        with open(g_txFileName, 'r', newline='') as csvfile, tempfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(tempfile)
            for row in reader:
                if row :
                    writer.writerow(row)
            # adding new tx
            writer.writerows(txDataList)
        shutil.move(tempfile.name, g_txFileName)
        csvfile.close()
        tempfile.close()
    except:
        # this is 1st time of creating txFile
        try:
            with open(g_txFileName, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(txDataList)
        except:
            return 0
    return 1
    print('txData written to txData.csv.')

def readTx(txFilePath):
    print("readTx")
    importedTx = []

    try:
        with open(txFilePath, 'r',  newline='') as file:
            txReader = csv.reader(file)
            for row in txReader:
                if row[0] == '0': # 블록체인에 미포함된 거래만 조회
                    line = txData(row[0],row[1],row[2],row[3],row[4])
                    importedTx.append(line)
        print("Pulling txData from csv...")
        return importedTx
    except:
        return []

def getTxData():
    strTxData = ''
    importedTx = readTx(g_txFileName)
    if len(importedTx) > 0 :
        for i in importedTx:
            print(i.__dict__)
            transaction = "["+ i.uuid + "]" "UserID " + i.sender + " sent " + i.amount + " bitTokens to UserID " + i.receiver + ". " #
            print(transaction)
            strTxData += transaction

    return strTxData

def mineNewBlock(difficulty=2, blockchainPath=g_bcFileName):
    blockchain = readBlockchain(blockchainPath)
    strTxData = getTxData()
    if strTxData == '' :
        print('No TxData Found. Mining aborted')
        return

    timestamp = time.time()
    proof = 0
    newBlockFound = False

    print('Mining a block...')

    while not newBlockFound:
        newBlockAttempt = generateNextBlock(blockchain, strTxData, timestamp, proof)
        if newBlockAttempt.currentHash[0:difficulty] == '0' * difficulty:
            stopTime = time.time()
            timer = stopTime - timestamp
            print('New block found with proof', proof, 'in', round(timer, 2), 'seconds.')
            newBlockFound = True
        else:
            proof += 1

    blockchain.append(newBlockAttempt)
    writeBlockchain(blockchain)

def mine(blocksToMine=5):
    #for _ in range(blocksToMine):
    mineNewBlock()

def isSameBlock(block1, block2):
    if block1.index != block2.index:
        return False
    elif block1.previousHash != block2.previousHash:
        return False
    elif block1.timestamp != block2.timestamp:
        return False
    elif block1.data != block2.data:
        return False
    elif block1.currentHash != block2.currentHash:
        return False
    return True

def isValidNewBlock(newBlock, previousBlock):
    if int(previousBlock.index) + 1 != int(newBlock.index):
        print('Indices Do Not Match Up')
        return False
    elif previousBlock.currentHash != newBlock.previousHash:
        print("Previous hash does not match")
        return False
    elif calculateHashForBlock(newBlock) != newBlock.currentHash:
        print("Hash is invalid")
        return False
    return True

def newtx(txToMining):

    newtxData = []
    # transform given data to txData object
    for line in txToMining:
        tx = txData(0, line['sender'], line['amount'], line['receiver'], uuid.uuid4())
        newtxData.append(tx)

    # limitation check : max 5 tx
    if len(newtxData) > 5 :
        print('number of requested tx exceeds limitation')
        return -1

    if writeTx(newtxData) == 0:
        print("file write error on txData")
        return -2
    return 1

def isValidChain(bcToValidate):
    genesisBlock = []
    bcToValidateForBlock = []

    # Read GenesisBlock
    try:
        with open(g_bcFileName, 'r',  newline='') as file:
            blockReader = csv.reader(file)
            for line in blockReader:
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                genesisBlock.append(block)
                break
    except:
        print("file open error in isValidChain")
        return False

    # transform given data to Block object
    for line in bcToValidate:
        # print(type(line))
        # index, previousHash, timestamp, data, currentHash, proof
        block = Block(line['index'], line['previousHash'], line['timestamp'], line['data'], line['currentHash'], line['proof'])
        bcToValidateForBlock.append(block)

    #if it fails to read block data  from db(csv)
    if not genesisBlock:
        print("fail to read genesisBlock")
        return False

    # compare the given data with genesisBlock
    if not isSameBlock(bcToValidateForBlock[0], genesisBlock[0]):
        print('Genesis Block Incorrect')
        return False

    tempBlocks = [bcToValidateForBlock[0]]
    for i in range(1, len(bcToValidateForBlock)):
        if isValidNewBlock(bcToValidateForBlock[i], tempBlocks[i - 1]):
            tempBlocks.append(bcToValidateForBlock[i])
        else:
            return False

    return True

def addNode(queryStr):
    # save
    txDataList = []
    txDataList.append([queryStr[0],queryStr[1]]) # ip, port

    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)
    try:
        with open(g_nodelstFileName, 'r', newline='') as csvfile, tempfile:
            reader = csv.reader(csvfile)
            writer = csv.writer(tempfile)
            for row in reader:
                if row:
                    if row[0] == queryStr[0] and row[1] == queryStr[1]:
                        print("requested node is already exists")
                        csvfile.close()
                        tempfile.close()
                        return -1
                    else:
                        writer.writerow(row)
            writer.writerows(txDataList)
        shutil.move(tempfile.name, g_nodelstFileName)
        csvfile.close()
        tempfile.close()
    except:
        # this is 1st time of creating node list
        try:
            with open(g_nodelstFileName, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerows(txDataList)
        except:
            return 0
    return 1
    print('new node written to nodelist.csv.')

def readNodes(filePath):
    print("read Nodes")
    importedNodes = []

    try:
        with open(filePath, 'r',  newline='') as file:
            txReader = csv.reader(file)
            for row in txReader:
                line = [row[0],row[1]]
                importedNodes.append(line)
        print("Pulling txData from csv...")
        return importedNodes
    except:
        return []

def broadcastNewBlock(blockchain):
    #newBlock  = getLatestBlock(blockchain) # get the latest block
    importedNodes = readNodes(g_nodelstFileName) # get server node ip and port
    reqHeader = {'Content-Type': 'application/json; charset=utf-8'}
    #reqBody = newBlock.__dict__
    reqBody = []
    for i in blockchain:
        reqBody.append(i.__dict__)

    if len(importedNodes) > 0 :
        for node in importedNodes:
            try:
                URL = "http://" + node[0] + ":" + node[1] + g_receiveNewBlock  # http://ip:port/node/receiveNewBlock
                res = requests.post(URL, headers=reqHeader, data=json.dumps(reqBody))
                if res.status_code == 200:
                    print(URL + " sent ok.")
                else:
                    print(URL + " responding error " + res.status_code)
            except:
                print(URL + " is not responding.")

def row_count(filename):
    with open(filename) as in_file:
        return sum(1 for _ in in_file)

def compareMerge(bcDict):

    heldBlock = [] # 내가 가진 블록체인 정보 담겠다
    bcToValidateForBlock = [] #밖에서 들어온 변수

    # Read GenesisBlock
    try:
        with open(g_bcFileName, 'r',  newline='') as file:
            blockReader = csv.reader(file)
            last_line_number = row_count(g_bcFileName)
            for line in blockReader:
                if blockReader.line_num == 1:
                    block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                    heldBlock.append(block)
                elif blockReader.line_num == last_line_number:
                    block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                    heldBlock.append(block)
    except:
        print("file open error in compareMerge or No database exists")
        return -1

    #if it fails to read block data  from db(csv)
    if len(heldBlock) == 0 : #0이면 비어있거나, 제대로 안들어온것!. -는 부정적의미. 끝남.
        print("fail to read")
        return -2

    # transform given data to Block object
    for line in bcDict:
        # print(type(line))
        # index, previousHash, timestamp, data, currentHash, proof
        block = Block(line['index'], line['previousHash'], line['timestamp'], line['data'], line['currentHash'], line['proof'])
        bcToValidateForBlock.append(block) #밖에서 받은 데이터 append!

    # compare the given data with genesisBlock
    if not isSameBlock(bcToValidateForBlock[0], heldBlock[0]): # 0번 제네시스블락, 같아야 한다. 아니면 나가리!
        print('Genesis Block Incorrect')
        return -1

    if isValidNewBlock(bcToValidateForBlock[-1],heldBlock[-1]) == False: # -1 변수 제일 뒤에 값

        # lastest block == broadcasted last block
        if isSameBlock(heldBlock[-1], bcToValidateForBlock[-1]) == True:
            print('lastest block == broadcasted last block')
            return 2
        # n
        else:
            print("Block Information Incorrect #1")
            return -1
    else:
        tempBlocks = [bcToValidateForBlock[0]]
        for i in range(1, len(bcToValidateForBlock)):
            if isValidNewBlock(bcToValidateForBlock[i], tempBlocks[i - 1]):
                tempBlocks.append(bcToValidateForBlock[i])
            else:
                print("Block Information Incorrect #2 "+tempBlocks.__dict__)
                return -1

        print("new block good")
        # save it to csv
        blockchainList = []
        for block in bcToValidateForBlock:
            blockList = [block.index, block.previousHash, str(block.timestamp), block.data, block.currentHash, block.proof]
            blockchainList.append(blockList)
        with open(g_bcFileName, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerows(blockchainList)
        return 1


# This class will handle any incoming request from
# a browser
class myHandler(BaseHTTPRequestHandler):


    # Handler for the GET requests
    def do_GET(self):
        data = []  # response json data
        if None != re.search('/block/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if None != re.search('/block/getBlockData', self.path):
                # TODO: range return (~/block/getBlockData?from=1&to=300)
                # queryString = urlparse(self.path).query.split('&')

                block = readBlockchain(g_bcFileName, mode = 'external')

                if block == None :
                    print("No Block Exists")
                    data.append("no data exists")
                else :
                    for i in block:
                        print(i.__dict__)
                        data.append(i.__dict__)

                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            elif None != re.search('/block/generateBlock', self.path):
                #mine() # thoread 로 아래 코드와 같이 분리해야함
                t = threading.Thread(target=mine)
                t.start()
                data.append("{mining is underway:check later by calling /block/getBlockData}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))
            else:
                data.append("{info:no such api}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

        elif None != re.search('/node/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if None != re.search('/node/addNode', self.path):
                queryStr = urlparse(self.path).query.split(':')
                res = addNode(queryStr)
                if res == 1:
                    data.append("added ok")
                elif res == 0 :
                    data.append("caught exception while saving")
                elif res == -1 :
                    data.append("requested node is already exists")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/

    def do_POST(self):

        if None != re.search('/block/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            if None != re.search('/block/validateBlock/*', self.path):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                #print(ctype) #print(pdict)

                if ctype == 'application/json':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    receivedData = post_data.decode('utf-8')
                    print(type(receivedData))
                    tempDict = json.loads(receivedData)  # load your str into a list #print(type(tempDict))
                    if isValidChain(tempDict) == True :
                        tempDict.append("validationResult:normal")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    else :
                        tempDict.append("validationResult:abnormal")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
            elif None != re.search('/block/newtx', self.path):
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                if ctype == 'application/json':
                    content_length = int(self.headers['Content-Length'])
                    post_data = self.rfile.read(content_length)
                    receivedData = post_data.decode('utf-8')
                    print(type(receivedData))
                    tempDict = json.loads(receivedData)
                    res = newtx(tempDict)
                    if  res == 1 :
                        tempDict.append("accepted : it will be mined later")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    elif res == -1 :
                        tempDict.append("declined : number of request txData exceeds limitation")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    elif res == -2 :
                        tempDict.append("declined : error on data read or write")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                    else :
                        tempDict.append("error : requested data is abnormal")
                        self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))

        elif None != re.search('/node/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            if None != re.search(g_receiveNewBlock, self.path): # /node/receiveNewBlock
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                receivedData = post_data.decode('utf-8')
                tempDict = json.loads(receivedData)  # load your str into a list
                print(tempDict)
                res = compareMerge(tempDict)
                if res == -1: # internal error
                    tempDict.append("internal server error")
                elif res == -2 : # block chain info incorrect
                    tempDict.append("block chain info incorrect")
                elif res == 1: #normal
                    tempDict.append("accepted")
                elif res == 2: # identical
                    tempDict.append("already updated")
                self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

try:

    # Create a web server and define the handler to manage the
    # incoming request
    # server = HTTPServer(('', PORT_NUMBER), myHandler)
    server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ', PORT_NUMBER)

    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
