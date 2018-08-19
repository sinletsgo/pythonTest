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

PORT_NUMBER = 8060
g_txFileName = "txData.csv"
g_bcFileName = "blockchain.csv"
g_nodeList = {}

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
    # 추가된 transction data
    def __init__(self, commitYN, sender, amount, receiver, uuid):
        self.commitYN = commitYN # 블록 포함여부(채굴)
        self.sender = sender # 송신자
        self.amount = amount #금액
        self.receiver = receiver # 수신자
        self.uuid =  uuid # 고유식별값



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
    return blockchain[len(blockchain) - 1] #-1 마지막 데이터. 즉 가장 최신 데이터

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
        updateTx(block) # 기존에서 이것 추가!

    print('Blockchain written to blockchain.csv.')
    print('Broadcasting founded block to other nodes')

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
    # 블록에 포함된 고유아이디 가져와서 파일열고

    phrase = re.compile(r"\w+[-]\w+[-]\w+[-]\w+[-]\w+") # [6b3b3c1e-858d-4e3b-b012-8faac98b49a8]UserID hwang sent 333 bitTokens to UserID kim.
    matchList = phrase.findall(blockData.data) # 정규표현식. re. 레귤러익스프레션 약자. 다 알 수 없다. 필요한것만 (예로 주민번호, 이메일 검출할때 사용) 안쓰고 split로 하면 복잡.
    # w = word,  즉 word  - 4개  - 있는곳까지 구분된 문자열을 찾아라
    # 구문 findall  트랙잭션데이터만 가져온다. 어떤 포맷? 위에 있는 .
    # 주석처리 처럼 데이터 들어온다.  [6b3b3c1e-858d-4e3b-b012-8faac98b49a8] 이부분 찾아야 비교해서 마킹
    # 주피터로 해볼수 있다. ppt 74
    # 채굴되고 포함되었으면 블록체인 data는 유지해야 하지만 ,
    # txdata 가지고 있을 필요가 없다. 로직이 더 필요. 1로 되있는 상위 몇개 1주일에 한번은 전체 30% 제거한다고 crotab 돌려도 좋지. 아이디어 내보자.

    if len(matchList) == 0 : #하나도 없다? 유니크 id가 없네. 그럼 제네시스 block 이라는것!
        print ("No Match Found! " + blockData.data + "block idx: " + blockData.index)
        return

    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)

    with open(g_txFileName, 'r') as csvfile, tempfile:
        reader = csv.reader(csvfile)
        writer = csv.writer(tempfile)
        for row in reader:
            if row[4] in matchList: # matchList 고유아이디 포함되있다. 고유아이디가 key값이고, 이걸로 찾아서 row를 0에서 1로 바꾸는것
                print('updating row : ', row[4])
                row[0] = 1  # 0을 1로 바꾸겠다
            writer.writerow(row) # wrtier 덮어쓰고

    shutil.move(tempfile.name, g_txFileName) # file 바꿔치기, shutil은 파일을 복사해 주는 파이썬 모듈이다.
    csvfile.close()
    tempfile.close()
    print('txData updated')

def writeTx(txRawData):
    # 기존대로 모든 데이터읽고 항상 처음으로 새로 다시 write 하는게 아니라,
    # data가 기존 2줄 있고, 1줄만 들어오면  사본에 3줄을 옮겨쓰고, 원본에 덮어써버린다.
    # 왜 똑같이 새로 write 안하고, 사본에 쓴다음 덮어쓰는가?
    # 1. file 쓰는 동안은 접근을 못함. 쓰고 있기 때문에 체인길어지면 길어질수록 대기시간이 길어진다. 몇초가 걸릴수도.
    # 그동안 원장에 접근해야 하는데, 기다리다.. 에러가 날수도
    # 2. 비효율적
    # db 쓰면 해결된다. 아니면 위와 같이 하거나.
    # file은 교육용, 사실 db로 바꿔치기하는게 맞다. mysql이든 sqlite 든.
    # db사용하면 버전도 맞춰야하고, 개발환경 설정이 힘듬.
    # 나중에 포트폴리오할떄,  db로 바꾸도록. 팀으로 할떄, 형상관리 전략으로 마스터, 브랜치. 브랜치로 만들어서 서로 소스.
    # 브랜치 전략 검색해서 함보라.


    txDataList = []
    # file쓰려면 객체 형태로 변환해야하니까.  과정임.
    for txDatum in txRawData:
        txList = [txDatum.commitYN, txDatum.sender, txDatum.amount, txDatum.receiver, txDatum.uuid]
        txDataList.append(txList)

    tempfile = NamedTemporaryFile(mode='w', newline='', delete=False)
    try:
        # file 열다 오류나거나 할때 with를 안쓰면 리소스 잡고있는다.with 써야 파일없거나 문제 생기면 리소스에 반납한다.
        with open(g_txFileName, 'r', newline='') as csvfile, tempfile: #open(g_txFileName, 'r', newline='') as csvfile 원본읽고, tempfile 임시읽고 둘이 분리해서 봐야
            reader = csv.reader(csvfile) # 원본읽는놈
            writer = csv.writer(tempfile)  #임시파일쓰는놈
            for row in reader:
                if row :
                    writer.writerow(row) # row가 존재하면 한줄씩 쓰는거다
            # adding new tx
            writer.writerows(txDataList) # txDataList 를 덮어쓴다!
        shutil.move(tempfile.name, g_txFileName) # tempfile.name으로 임시파일 찾아가는듯함.
        csvfile.close()
        tempfile.close()
    except:# 한번도 txdata 써보지 않은상황. 한번도 생성안했을때 걸린다. 그때 생성하겠다고 except 처리
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
                if row[0] == '0': # 블록체인에 미포함된 거래만 조회. 0은 채굴 안된걸 의미
                    line = txData(row[0],row[1],row[2],row[3],row[4]) #class 객체로 변환
                    importedTx.append(line)
        print("Pulling txData from csv...")
        return importedTx
    except:
        return []

def getTxData():
    strTxData = ''
    importedTx = readTx(g_txFileName) #이젠 txdata를 읽어와서 여기서 만들겠다! , 즉 거래에데이터를 채굴 될떄 포함시키려고!
    if len(importedTx) > 0 : #받아서 있으면 포함시키겠다!
        for i in importedTx:
            print(i.__dict__)
            transaction = "["+ i.uuid + "]" "UserID " + i.sender + " sent " + i.amount + " bitTokens to UserID " + i.receiver + ". " # 문자로 만들어준다
            print(transaction)
            strTxData += transaction

    return strTxData # 이제 이걸로 hash값 계산할거다.

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
    # previousBlock 처음 제네시스 블락
    if int(previousBlock.index) + 1 != int(newBlock.index): # 이전블락과 new블락의 index가 같지않으면 false ! 같아야 한다!
        print('Indices Do Not Match Up')
        return False
    elif previousBlock.currentHash != newBlock.previousHash: #마찬가지로 hash값도 이전 block 에서 왔어야 검증이 되는거다!
        # newBlock 에 현재 저장된 previousHash가 곧 이전 previousBlock 에 currentHash 가 되야 하는것! chain으로 연결되니까.
        print("Previous hash does not match")
        return False
    elif calculateHashForBlock(newBlock) != newBlock.currentHash: #block 유효성 검증. 즉 Hash값을 비교해서 무결성. 변조되지 않았다는걸 검증하는것.
        # hash값은 돌아갈 수 없지만, block 데이터를 넣고 hash한 값이랑 비교해서 같으면 같은 데이터로 hash 했음을 아는것!
        print("Hash is invalid")
        return False
    return True


def newtx(txToMining):
    newtxData = []
    # transform given data to txData object
    for line in txToMining:
        # 0 채굴포함여부(포함 1), txToMining 받은걸 그대로
        # UUID는 기본적으로 어떤 개체(데이터)를 고유하게 식별하는 데 사용되는 16바이트(128비트) 길이의 숫자입니다.
        # data 여기서 변환하고 밑에서 write 할 때 역변환하고
        tx = txData(0, line['sender'], line['amount'], line['receiver'], uuid.uuid4() ) #  uuid 고유번호 떨어진다
        newtxData.append(tx)

    # limitation check : max 5 tx
    if len(newtxData) > 5 : # 5건까지만 처리하겠다. 안넣어도되지만 일단넣으심
        print('number of requested tx exceeds limitation')
        return -1

    if writeTx(newtxData) == 0:  # csv 쓰겠다! 이것도 쓰던대로 patten, 역변환
        print("file write error on txData")
        return -2
    return 1

def isValidChain(bcToValidate):
    genesisBlock = []
    bcToValidateForBlock = []

    # Read GenesisBlock
    # 현재 저장된 GenesisBlock만 불러와서 먼저 검증! 통과되면
    # 그리고 isSameBlock에서 본격적으로 이전 block 과 현재 new block 과 검증하는거다
    try:
        with open(g_bcFileName, 'r') as file:
            blockReader = csv.reader(file)
            for line in blockReader:
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5]) # line(list)에 하나씩 접근해서 Block class 생성자 호출하면서 Block class생성
                genesisBlock.append(block)
                break
    except:
        print("file open error in isValidChain")
        pass

    # transform given data to Block object
    for line in bcToValidate: # 매개변수 통해 검증해달라고 post 로 받은 bcToValidate를 list 안에 dict 형식으로 변환
        # print(type(line))
        # index, previousHash, timestamp, data, currentHash, proof
        # line 이 dict 형식이니까, line['index'] 식으로 key 로 value 접근
        block = Block(line['index'], line['previousHash'], line['timestamp'], line['data'], line['currentHash'], line['proof'])
        bcToValidateForBlock.append(block) # 검증해달라고 받은 data list 형식으로 재구성

    #if it fails to read block data  from db(csv)
    if not genesisBlock:
        print("fail to read genesisBlock")
        return False

    # compare the given data with genesisBlock
    # 받은 데이터와, 저장된 block data의 genesisBlock 비교
    # GenesisBlock이 같으면 통과!
    # but 버그가 있음. Genesis 만 같게 해놓고 나머진 조작할 수도 있으니까.
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
                g_nodeList[queryStr[0]] = queryStr[1]
                data.append(g_nodeList)
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

                elif ctype == 'application/x-www-form-urlencoded':
                    content_length = int(self.headers['content-length'])
                    # trouble shooting, below code ref : https://github.com/aws/chalice/issues/355
                    postvars = parse_qs((self.rfile.read(content_length)).decode('utf-8'), keep_blank_values=True)
                    # print(postvars)    #print(type(postvars)) #print(postvars.keys())
                    self.wfile.write(bytes(json.dumps(postvars), "utf-8"))

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


