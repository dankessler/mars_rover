import os
import sys

from select import select
from copy import deepcopy

import bisect

_BYTE_COUNT_KEY_  = 'numBytes'
_LATENCY_KEY_     = 'latency'
_BANDWIDTH_KEY_   = 'bandwidth'
_CHUNK_COUNT_KEY_ = 'numChunks'

class ConnInfo(object):
    def __init__(self, paramDict):
        self.paramInfo = paramDict

    # context params are in order of expected input
    _CONTEXT_PARAMS_ = (_BYTE_COUNT_KEY_, _LATENCY_KEY_,
                        _BANDWIDTH_KEY_, _CHUNK_COUNT_KEY_)

    @staticmethod
    def fromStdIn():
        connParams = {}

        for param in ConnInfo._CONTEXT_PARAMS_:
            connParams[param] = int(raw_input())

        return ConnInfo(connParams)

    def __str__(self):
        print(self.paramsToStr())

    def imageSize(self):
        return self.paramInfo[_BYTE_COUNT_KEY_]

    def latency(self):
        return self.paramInfo[_LATENCY_KEY_]

    def bandwidth(self):
        return self.paramInfo[_BANDWIDTH_KEY_]

    def numChunks(self):
        return self.paramInfo[_CHUNK_COUNT_KEY_]

    def getDlTime(self, numBytes):
        return float((2 * self.paramInfo[_LATENCY_KEY_]) +
                     (numBytes / self.paramInfo[_BANDWIDTH_KEY_]))

    def paramsToStr(self):
        paramsAsStr = ''

        for (param, value) in self.paramInfo.items():
            paramsAsStr += ('%s: %d\n' % (param, value))

        return paramsAsStr

    def __str__(self):
        return self.paramsToStr()

class RoverImageSolver(object):
    def __init__(self, graphNodeQueue):
        self.graphNodeQueue = graphNodeQueue

    @staticmethod
    def addNodeToGraph(newNode, graphNodes):
        insertNdx = 0

        for nodeNdx in range(len(graphNodes)):

            if (newNode > graphNodes[nodeNdx]):
                if graphNodes[nodeNdx].overlapsWith(newNode):
                    graphNodes[nodeNdx].addEdgeTo(newNode)

                insertNdx += 1

            elif (newNode < graphNodes[nodeNdx]):
                if (newNode.overlapsWith(graphNodes[nodeNdx])):
                    newNode.addEdgeTo(graphNodes[nodeNdx])

            elif not (newNode.chunk.isOverlapping(graphNodes[nodeNdx].chunk) or
                      graphNodes[nodeNdx].chunk.isOverlapping(newNode.chunk)):
                break

        graphNodes.insert(insertNdx, newNode)

    @staticmethod
    def fromStdIn(connInfo):
        '''
        - create node from chunk info with download cost
        - if node is initial node; then edge from 0,0 to node
        - add node to node_list in sorted order (this is to ensure that edges
          are made between internal nodes)
        - seed node queue with startNode
        - return node queue for processing
        '''
        startNode = Node()
        graphNodes = []

        for chunkNum in range(connInfo.numChunks()):
            # get chunk info
            (startByte, endByte) = (int(x) for x in str(raw_input()).split(','))
            dlTime = connInfo.getDlTime(endByte - startByte)

            newNode = Node(Chunk(startByte, endByte), dlTime)

            if (newNode.chunk.isStartChunk()):
                startNode.addEdgeTo(newNode)

            elif (endByte == connInfo.imageSize()):
                newNode.chunk.isEnd = True

            RoverImageSolver.addNodeToGraph(newNode, graphNodes)

        print('graph nodes:\n%s' % '\n'.join([str(node) for node in graphNodes]))
        return RoverImageSolver([startNode])

    def calcOptimalDownloadTime(self):
        optimalDlTime = None

        while (len(self.graphNodeQueue) > 0):
            graphNode = self.graphNodeQueue.pop(0)
            print('processing node [%s]' % graphNode.chunk)

            if graphNode.isExplored():
                print('paths to node [%s] have been explored!' % graphNode.chunk)

            elif not graphNode.isExplored():
                print('paths to node [%s] have not been explored...' % graphNode.chunk)

            if not graphNode.isExplored():
                self.graphNodeQueue.append(graphNode)

            if graphNode.chunk.isEnd:
                optimalDlTime = min(optimalDlTime, graphNode.getWeight())

            else:
                self.walkToNeighbor(graphNode)

        return optimalDlTime

    def walkToNeighbor(self, graphNode):
        if len(graphNode.neighbors) > 0:
            neighbor = graphNode.neighbors.pop(0)

            print('walking to neighbor [%s]' % neighbor)

            # the weight method returns the node weight plus the weight of the
            # optimal path leading to it, considerPathWeight tells the next node to
            # compare the given weight to its other path weights so that it can
            # maintain it's own optimal path weight
            neighbor.considerPathWeight(graphNode.getWeight())

            print('neighbor path weight is now [%.03f]' % neighbor.getWeight())

            # this node may now be processed. Note that when it's processed, if
            # paths leading to it have not all been considered, it will be sent to
            # the end of the queue so that later nodes do not need to have paths
            # re-calculated
            print('queue length before adding neighbor: %d' % len(self.graphNodeQueue))
            self.graphNodeQueue.append(neighbor)
            print('queue length after adding neighbor: %d' % len(self.graphNodeQueue))

class Chunk(object):
    def __init__(self, startByte, endByte):
        self.startByte = startByte
        self.endByte = endByte
        self.isEnd = False

    def size(self):
        return abs(self.endByte - self.startByte)

    def start(self, newStart=None):
        if (newStart is not None):
            self.startByte = newStart

        return self.startByte

    def end(self, newEnd=None):
        if (newEnd is not None):
            self.endByte = newEnd

        return self.endByte

    def isStartChunk(self):
        return self.start() == 0

    def isEndChunk(self, imageSize):
        return self.isEnd

    # overlapping means that the beginning of other overlaps with the end of
    # self, e.g.
    # (self)   |------|
    # (other)       |-------|
    def overlapsWith(self, other):
        otherIsShifted = self.isShifted(other)
        otherIsOverlapping = self.isOverlapping(other)

        return otherIsShifted and otherIsOverlapping

    # is shifted means that other start and end bytes are *AFTER* self start
    # and end bytes, e.g.
    # (self)  200, 550
    # (other) 350, 750
    def isShifted(self, other):
        return other.start() > self.start() and other.end() > self.end()

    # is overlapping means that other start byte is before the self end byte,
    # e.g.
    # (self)  200, 550    or   (self)  200, 550 
    # (other) 350, 750         (other) 550, 750 
    # but *NOT*
    #  (self)  200, 550   or   (self)  200, 550
    #  (other) 551, 750        (other) 150, 450
    def isOverlapping(self, other):
        return other.start() <= self.end()

    def __str__(self):
        return '[%d, %d]' % (self.start(), self.end())

    def __cmp__(self, other):
        selfVal = self.start()
        otherVal = other.start()

        if (selfVal == otherVal):
            selfVal = self.end()
            otherVal = other.end()

        #print('comparing self [%s] to other [%s]: [%d]' % (self, other, selfVal - otherVal))

        return selfVal - otherVal

class Node(object):
    def __init__(self, chunk=Chunk(0, 0), dlTime=0):
        self.chunk = chunk
        self.weight = dlTime
        self.neighbors = []

        self.numInEdges = 0
        self.pathWeight = 0
        self.numPathsConsidered = 0

    def getWeight(self):
        return self.weight + self.pathWeight

    # first we consider the given weight of a path leading to this node. If it
    # is more optimal, we save it. Also, we increment the number of paths we
    # have considered. When the same number of paths (parents) have given us
    # path weights to consider as the number of in edges we have (parents) then
    # we know that the path cost we currently maintain *IS* optimal
    def considerPathWeight(self, weight):
        self.pathWeight = min(self.pathWeight, weight)
        self.numPathsConsidered += 1

    def addEdgeTo(self, newNeighbor):
        print('adding edge from [%s] to [%s]' % (self.chunk, newNeighbor.chunk))
        self.neighbors.append(newNeighbor)
        newNeighbor.numInEdges += 1

    def isExplored(self):
        return self.numPathsConsidered == self.numInEdges

    def overlapsWith(self, other):
        return self.chunk.overlapsWith(other.chunk)

    def __cmp__(self, other):
        return self.chunk.__cmp__(other.chunk)

    def __str__(self):
        #return ('node [%s] -> weight: %.03f' % (self.chunk, self.getWeight()))
        return ('node [%s] -> %.03f\n\tneighbors:\t%s' % (
                self.chunk, self.getWeight(), ','.join(['[%s]' % node.chunk for node in self.neighbors])))

if __name__ == '__main__':
    sys.stdin = open('inputs/third.input')

    connInfo = ConnInfo.fromStdIn()
    roverImage = RoverImageSolver.fromStdIn(connInfo)

    sys.exit()

    downloadTime = roverImage.calcOptimalDownloadTime()

    if (downloadTime is not None):
        print('%.03f' % downloadTime)

    sys.stdin.close()
