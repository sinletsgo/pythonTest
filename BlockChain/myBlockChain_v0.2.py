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

PORT_NUMBER = 8060

# 300줄밖에 안된다. 다른 기업 code는 몇만줄 된다.
# 외워도 외운다!
# 함수 추적이 가능한 code다 . 보기 쉬운 code다. 추적이 안되는 code도 많다

# code가 어려운게 아니고, 거래데이터를 어떻게 보호할것인가가 더 중요. 필요하면 암호화까지 해야한다.
# 데모 code다. 다른 code도 이 정도에서 더이상 못나간다
# code 라인 수.. 5천줄 넘어가면 분리한다고 함.

class Block:

    # A basic block contains, index (blockheight), the previous hash, a timestamp, tx information, a nonce, and the current hash

    # self ? 선언시 self 넣으라고 해놓은것. 문법이다. 자기 자신 객체! . 없으면 부모로 올라감
    def __init__(self, index, previousHash, timestamp, data, currentHash, proof ): #self 로 먼저 들어옴, 6개 매개변수 정해놓음. 무조건 호출 되는 함수
        self.index = index  #Index - 몇번째 블락이냐?
        self.previousHash = previousHash #Previous – 이전블록 주민번호. 고유한값을 현재블록이 기억!
        self.timestamp = timestamp # Timestamp – 블록 생성 시점. 서버 시간!
        self.data = data  # 블록안에 어떤 데이터 다룰거냐?.   거래데이터. post로 만들어야
        # Data – 각 블록안에 어떤 데이터 다룰꺼냐. 블록체인 예시로 보험 많이. 사고유발 많이내는 사람 data조회해서 더 많이 청구하고. 이런 data가 블록체인안에 구성해서 돌아다니게.
        self.currentHash = currentHash # 현블록 해쉬값
        self.proof = proof #채굴 삽질 횟수. 작업증명 값
        # - Proof 삽질횟수. 전세계에서 채굴하려고 특정값 찾기 위해 몇번 삽질했니? 난이도가 낮다면 해킹위험성

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
#-------여기까지 class---------



# ---------여기부턴 전역 함수-----------
def generateGenesisBlock():
    print("generateGenesisBlock is called")
    timestamp = time.time()
    print("time.time() => %f \n" % timestamp)
    tempHash = calculateHash(0, '0', timestamp, "My very first block :)", 0)
    print(tempHash)
    return Block(0, '0', timestamp, "My very first block",  tempHash,0)
    # return Block(0, '0', '1496518102.896031', "My very first block :)", 0, '02d779570304667b4c28ba1dbfd4428844a7cab89023205c66858a40937557f8')

def calculateHash(index, previousHash, timestamp, data, proof):

    #value 에 더한다!
    value = str(index) + str(previousHash) + str(timestamp) + str(data) + str(proof)
    # value: str = str(index) + str(previousHash) + str(timestamp) + str(data) + str(proof)
    sha = hashlib.sha256(value.encode('utf-8')) #sha256 hash!  비트코인처럼 hash나온다. 웹에서 hash 하는 거랑 같이. hashlib 라이브러리 사용
    return str(sha.hexdigest()) #hash 계산된것 보기 편하라고 16진수로 변환해서 리턴

def calculateHashForBlock(block):
    return calculateHash(block.index, block.previousHash, block.timestamp, block.data, block.proof)

def getLatestBlock(blockchain):
    return blockchain[len(blockchain) - 1] # 가장 마지막 가져와서, return. -1이면 맨 마지막. 이미 0~5번 데이터가 존재하면 즉 6번째

def generateNextBlock(blockchain, blockData, timestamp, proof):
    previousBlock = getLatestBlock(blockchain)
    nextIndex = int(previousBlock.index) + 1 #generateNextBlock을 생성하기 위해 마지막 previousBlock data의 index 에서 +1해서 다음 index값을 찾기
    nextTimestamp = timestamp
    nextHash = calculateHash(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, proof)
    # index, previousHash, timestamp, data, currentHash, proof
    # nextIndex 6번
    # 거래를 포함한 데이터
    return Block(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, nextHash, proof)

def writeBlockchain(blockchain):
    blockchainList = []


    # 이곳에 뭔가 비효율적인것 아닌가 의문이 생길수도.
    # blockchain list 내에 class객체들이 있다.
    for block in blockchain: #block은 임의로 준건데, blockchain에 하나 하나 class에 접근하는 변수다.
        # index, previousHash, timestamp, data, currentHash, proof

        #아래 [] 해주니까, class형식이 list형식으로 바뀐다
        blockList = [block.index, block.previousHash, str(block.timestamp), block.data, block.currentHash,block.proof ] #bug fix 20180511 by hwy
        blockchainList.append(blockList) # csv 엑셀 파일에 한 행 마다 있는 data같이 여기서 blockList를 행마다 붙이는거다!

    # for 문 전체 데이터 다 돌린다음에! 아래로 내려감
    with open("blockchain.csv", "w", newline='') as file: # w write mode로! csv file 생성!
        writer = csv.writer(file)
        writer.writerows(blockchainList)

    print('Blockchain written to blockchain.csv.')

#처음 readBlockchain() 호출할때가 internal모드다. 그래서 데이터가 없으면 밑에 internal러긴다
# external 호출하는 곳이  getBlockData 데이터 조회할 때 있다.
def readBlockchain(blockchainFilePath, mode = 'internal'):
    print("readBlockchain")
    importedBlockchain = []

    try: #
        #internal mode일때, with open 시 읽을 file이 없으면 except 로 빠져서 블록 생성
        with open(blockchainFilePath, 'r',  newline='') as file: # r. read모드로 file 읽고
            blockReader = csv.reader(file)  # csv로 읽혀진다
            for line in blockReader: #file안에 내용 본격적으로 한 줄씩 읽는다 행만큼 반복
                # 여기서 무조건 실행되는 함수인 def __init__ 호출해서 생성자 초기화
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5]) #6개 class 생성자 통해서 . block 객체로 들어감

                importedBlockchain.append(block) # 위 block들 0~5개 총6개 list로 importedBlockchain 이곳에 append해서 들어간다

        print("Pulling blockchain from csv...")

        return importedBlockchain

    except:  # 블록체인 db가 존재하지 않으면 except 이곳으로 와서
        if mode == 'internal': # generateGenesisBlock 호출해서 최초 블럭 생성!
            return [generateGenesisBlock()]
        else :
            return None # 블록체인 db가 존재하지 않고, internal 이면 빈 데이터 return ?

def getTxData():
    txData = ''


    # 한블락에 5개 트랙잭션 데이터!
    for _ in range(5):
        txTo, txFrom, amount = random.randrange(0, 1000), random.randrange(0, 1000), random.randrange(0, 100)

        # bitTokens
        #이 부분에 아이디어를 넣어야 한다. 나만의 아이디어!
        # 자동차, 숙박,음원 등....
        # bitTokens이 아니라 고민해보면 문자열이 아니라, 클래스 블락 생성한것처럼 생성해서, 컨트롤하도록 뭔가를 만드는것
        # transaction도 db로 저장해서. 한 블락 1000개. 10분에 1000개. 수수료 많은것부터 포함 다른건 나중에.
        # transaction도 이걸 고려해야. 사이즈를 정해야. 갑자기 1만개x.
        # 쌓아두고 채굴할때 10~100개든 포함하도록.
        # 거래데이터 만들고 예외처리 어떻게 하고.. 이부분이 하이라이트.
        transaction = 'UserID ' + str(txFrom) + " sent " + str(amount) + ' bitTokens to UserID ' + str(txTo) + ". "
        txData += transaction

    return txData


def mineNewBlock(difficulty=2, blockchainPath='blockchain.csv'):
    blockchain = readBlockchain(blockchainPath) # 5개 data 읽어온다!
    txData = getTxData() # 트랜잭션 데이터 만든다. 6번 블락. 새로운 트랜잭션 데이터 만들려고 콜!
    timestamp = time.time() #컴퓨터의 현재 시각을 구하는 함수. 이걸로 현재 날짜 구하는 함수도 있다
    proof: int = 0  # 현재는 0이지만 시도에 따라 몇번이 될지 모름.
    newBlockFound = False

    print('Mining a block...')

    #new Block 생성! hash값을 찾으면 생성되는것!
    while not newBlockFound: # newBlockFound not 이면 계속 반복, true면 멈춤.

        # newBlockAttempt 새로운 블락 만든다. (하지만 밑에 hash를 맞춰야 새롭게 블록 생성되어 체인에 엮여서 블록체인으로 완성된다)
        newBlockAttempt = generateNextBlock(blockchain, txData, timestamp, proof)

        # difficulty 2로 정해놓았다. 그러니 0- > 2까지 0,1 번째가 00 ('0' * difficulty= '00')으로 시작해야한다
        if newBlockAttempt.currentHash[0:difficulty] == '0' * difficulty:  # currentHash는  class block 가진놈. currentHash가 0~ 2번째 전까지 맞다면. 00
            stopTime = time.time()
            timer = stopTime - timestamp
            print('New block found with proof', proof, 'in', round(timer, 2), 'seconds.')
            newBlockFound = True # true가 되야 while문 종료
        else:
            proof += 1 #계속 바껴서 hash를 다시 하는것 값 찾을때까지 수십 수십만~!

    blockchain.append(newBlockAttempt) #6번째 데이터를 붙인다.
    writeBlockchain(blockchain) #blockchain data 전체를 기록한다

def mine(blocksToMine=5): #blocksToMine 임의로 5개 정해줌. 5개 블록 생성하라!. 나중에 고쳐야
    for _ in range(blocksToMine):
        mineNewBlock()


# 하나라도 다르면 조작이 있는, 오류가 있는것!
# proof 값이 빠짐. 넣어야 한다.
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
    return True # 다 맞으면 true return!



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



# 허점이 있다. 찾아내보자. 뭔가 빠짐.
def isValidChain(bcToValidate):
    genesisBlock = []
    bcToValidateForBlock = []

    # Read GenesisBlock
    try:
        with open('blockchain.csv', 'r') as file:
            blockReader = csv.reader(file)
            for line in blockReader:
                block = Block(line[0], line[1], line[2], line[3], line[4], line[5])
                genesisBlock.append(block)
                break
    except:
        print("file open error in isValidChain")
        pass

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

    return True # 다 통과되면 이상없음! true!


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

            if None != re.search('/block/getBlockData', self.path): # getBlockData path는 블록체인 데이터 조회!
                # TODO: range return (~/block/getBlockData?from=1&to=300)  #한꺼번에 보낸다? 이런 code도 있는듯
                # queryString = urlparse(self.path).query.split('&')

                block = readBlockchain('blockchain.csv', mode = 'external') #readBlockchain에 전달인자 포함해서 호출

                # if~ else 문만 수정해서 바꾸면 된다. 나머지 위아래 고정.
                if block == None : # 없으면 data 안준다
                    print("No Block Exists")
                    data.append("no data exists")
                else :
                    for i in block:
                        print(i.__dict__)
                        data.append(i.__dict__) # json 형식으로 data에 append!
                        #data.append(i.toJSON()) # --> 이 방법은 안됨 리턴문자열에 '\' 문자 포함됨

                # data json dumps utf-8 형식으로 response 보낸다!
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            elif None != re.search('/block/generateBlock', self.path):
                # mine() # thread 로 아래 코드와 같이 분리해야함

                # thread 왜 썼냐? 채굴하는 시간 많이 걸릴 수 있다. 예로 요리 한다면 요리하는 동안 아무것도 못한다.
                # thread 없으면 mine() 호출하고 끝날거다.
                # 난이도가 높거나, 10분 내내 해도 채굴이 안될 수 있다.
                # 그때 다른 사용자가 내 서버 요청해도 응답 못보냄. 클라이언트는 계속 기다려야한다.
                # 서버도 계속 멈춰있어서 다른 작업 못한다.
                # thread mine 함수로 보내고, 일단 다른 일을 하는거다. 클라이언트에게 응답주면서.
                t = threading.Thread(target=mine)
                t.start() #여기서 thread 시작!

                data.append("{mining is underway:check later by calling /block/getBlockData}")
                self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))
            else:
                data.append("{info:no such api}")
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

            # 내가 가지고 있는 블록체인 맞냐? YES no 용도
            if None != re.search('/block/validateBlock/*', self.path): #검증 로직
                ctype, pdict = cgi.parse_header(self.headers['content-type'])
                print(ctype)
                print(pdict)

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
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

try:

    # Create a web server and define the handler to manage the
    # incoming request
    # server = HTTPServer(('', PORT_NUMBER), myHandler)


    #여기서 서버가 시작된다!
    server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler) # '' 안에 localhost 넣으면 local에서만 service 가능.
    print('Started httpserver on port ', PORT_NUMBER)

    # Wait forever for incoming http requests
    # get, post 받을 준비. 요청이 오면 myHandler 에서 시작됨.
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
