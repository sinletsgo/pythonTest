import hashlib

import time

import csv

import random



class Block:

    #A basic block contains, index (blockheight), the previous hash, a timestamp, tx information, a nonce, and the current hash

    def __init__(self, index, previousHash, timestamp, data, proof, currentHash):

        self.index = index

        self.previousHash = previousHash

        self.timestamp = timestamp

        self.data = data

        self.currentHash = currentHash

        self.proof = proof



def getGenesisBlock():
    print("getGenesisBlock is called")
    timestamp = time.time()
    print("# timestamp를 찍어본다.")
    print("time.time() => %f \n" % timestamp)
    tempHash = calculateHash(0,'0',timestamp,"My very first block :)",0)
    print(tempHash)
    return Block(0, '0', timestamp, "My very first block :)", 0, tempHash)
    #return Block(0, '0', '1496518102.896031', "My very first block :)", 0, '02d779570304667b4c28ba1dbfd4428844a7cab89023205c66858a40937557f8')



def calculateHash(index, previousHash, timestamp, data, proof):

    value = str(index) + str(previousHash) + str(timestamp) + str(data) + str(proof)

    sha = hashlib.sha256(value.encode('utf-8'))

    return str(sha.hexdigest())



def calculateHashForBlock(block):

    return calculateHash(block.index, block.previousHash, block.timestamp, block.data, block.proof)



def getLatestBlock(blockchain):

    return blockchain[len(blockchain)-1]



def generateNextBlock(blockchain, blockData, timestamp, proof):

    previousBlock = getLatestBlock(blockchain)

    nextIndex = int(previousBlock.index) + 1

    nextTimestamp = timestamp

    nextHash = calculateHash(nextIndex, previousBlock.currentHash, nextTimestamp, proof, blockData)

    return Block(nextIndex, previousBlock.currentHash, nextTimestamp, blockData, proof, nextHash)



def writeBlockchain(blockchain):

    blockchainList = []

    for block in blockchain:

        blockList = [block.index, block.previousHash, str(block.timestamp), block.data, block.proof, block.currentHash]

        blockchainList.append(blockList)

        

    with open("blockchain.csv", "w") as file:

        writer = csv.writer(file)

        writer.writerows(blockchainList)

    print('Blockchain written to blockchain.csv.')



def readBlockchain(blockchainFilePath):

    importedBlockchain = []

    try:

        with open(blockchainFilePath, 'r') as file:

            blockReader = csv.reader(file)

            for line in blockReader:

                block = Block(line[0], line[1], line[2], line[3], line[4], line[5])

                importedBlockchain.append(block)

        print("Pulling blockchain from csv...")

        return importedBlockchain

    except:

        print('No blockchain located. Generating new genesis block...')

        return [getGenesisBlock()]



def getTxData():

    txData = ''

    for _ in range(5):

        txTo, txFrom, amount = random.randrange(0, 1000), random.randrange(0, 1000), random.randrange(0, 100)

        transaction = 'User ' + str(txFrom) + " sent " + str(amount) + ' tokens to user ' + str(txTo) + ". "

        txData += transaction

    return txData



def mineNewBlock(difficulty = 5, blockchainPath = 'blockchain.csv'):

    blockchain = readBlockchain(blockchainPath)

    txData = getTxData()

    timestamp = time.time()

    proof = 0

    newBlockFound = False

    print('Mining a block...')

    while not newBlockFound:    

        #print("Trying new block proof...")

        newBlockAttempt = generateNextBlock(blockchain, txData, timestamp, proof)

        if newBlockAttempt.currentHash[0:difficulty] == '0'*difficulty:

            stopTime = time.time()

            timer = stopTime - timestamp

            print('New block found with proof', proof, 'in', round(timer, 2), 'seconds.')

            

            newBlockFound = True

        else:

            proof += 1

    blockchain.append(newBlockAttempt)

    writeBlockchain(blockchain)



def mine(blocksToMine = 5):

    for _ in range(blocksToMine):

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
    if previousBlock.index + 1 != newBlock.index:
        print('Indices Do Not Match Up')
        return False
    elif previousBlock.currentHash != newBlock.previousHash:
        print("Previous hash does not match")
        return False
    elif calculateHashForBlock(newBlock) != newBlock.hash:
        print("Hash is invalid")
        return False
    return True
	
def isValidChain(bcToValidate):
    if not isSameBlock(bcToValidate[0], getGenesisBlock()):
        print('Genesis Block Incorrect')
        return False
    
    tempBlocks = [bcToValidate[0]]
    for i in range(1, len(bcToValidate)):
        if isValidNewBlock(bcToValidate[i], tempBlocks[i-1]):
            tempBlocks.append(bcToValidate[i])
        else:
            return False
    return True

#getGenesisBlock()
mine()
