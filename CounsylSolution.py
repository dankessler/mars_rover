'''
################################################################################
#
# Initial attempts/ideas
#
################################################################################

There were a couple different approaches I tried to apply to the given problem
but that very quickly did not pan out.

Reading the problem statement I immediately though dynamic programming, but had
difficulty trying to think of how to phrase the problem in such a way as
to have a sub problem that could be optimized.

Given that a dynamic programming approach wasn't applicable, my fallback
approach was a simple greedy solution. Typically my assumption is such that
challenges such as these are much simpler than it seems. After thinking about
the different possibilities and realizing that at any given time a
non-suboptimal choice could not be made, I figured that this problem was more
complex than a greedy approach could tackle. That is, if I consider decisions
to be about image chunks from the mars rover, if I choose a particular image
and disregard another that spans a similar byte range, it's possible that I
have now chosen a suboptimal image chunk to download. I even attempted to think
of trying to "fill" the range of my image initially and then make some
decisions as to replacing chunks I had chosen with better ones not yet seen
(more or less as I'm parsing).

Given a lot of time considering the above two approaches, I finally settled on
a graph-based approach. In some ways this problem reminded me of minimal
spanning trees (MST). I decided that an MST isn't applicable because MSTs are
more concerned with every node being connected to the graph, not with having an
optimal path from specific nodes to others.

I finally settled on a branch and bound approach. From my experience, branch
and bound is applicable to problems that require consideration of nearly every
possibility but any given consideration could be halted if it seemed clearly
suboptimal. My submitted code attempted this approach, though my bounding
(pruning) step was broken at best (Also, I'm not sure why test #4 was incorrect
yet).

################################################################################
#
# The primary analysis
#
################################################################################

My submitted code (not here and was uncommitted so I've lost it, personally)
and the code written here are very similar in most approaches so an algorithmic
analysis of this code should yield fairly similar algorithmic analysis of my
submitted code via hackerrank.

First, to construct a graph from the list of image chunks, I build a sorted
list using insertion sort (O(n log n)--ascending by first index then second
index. The main purpose of this list is so that as image chunks are parsed its
possible to create connections to other image chunks without comparing every
image chunk to every other image chunk (O(n^2)). While building this list, I
also point a dummy node (image chunk of 0,0) to image chunks that start
with 0, and mark final chunks that have an ending byte index equal to the size of
the mars rover image. This simplifies starting the traversal across the
graph. Marking chunks as final, or end, chunks allows me to more easily know
when the cost to download a chunk is something that should be considered a
possible answer.

The algorithmic analysis of the graph traversal is a bit tricky. Because every
node maintains the cost of the optimal path leading to it, it makes pruning
clearly suboptimal paths much easier. In this way, traversal appears to be O(n)
with respect to the number of edges, not the number of nodes. To consider a
conservative upper bound of the number of edges, we observe that a fully
connected undirected graph may have (n(n - 1) / 2) edges. We compare our graph
to an undirected graph although ours is directed because there is no way to
have a back edge (an edge represents going to the next chunk in sequence, and
so there are no edges going to the previous chunk in sequence). But also, in
many cases, the number of edges will be much lower than (n (n - 1) / 2). Notice
that to have a fully connected graph means that it would be possible to go from
one node (say, the dummy node 0,0) to every other node. This would mean that
every image chunk we are considering starts at 0, and since we are guaranteed
that the whole image is downloadable, that means that at least one such chunk
also has the last byte of the image. Thus, it's impossible to have a fully
connected graph. Of course, it's very difficult to reason about a more
reasonable estimation than (n(n - 1)/2), so for now we will assume
O(n(n-1)/2)--approximately O(n^2).

Additionally, regarding graph traversal, an efficient traversal relies on
computing the cost of each path leading to a particular node, A, before the
cost of paths leading to nodes after A are computed. For example, let's say we
have 3 image chunks: A(0, 300), B(250, 400), C(300, 500). While it seems clear
that A->C is better than A->B->C, we must still compute each path to be sure.
Now if we let C be an internal node for some graph G, then it's reasonable to
assume that C has edges to other nodes D, E, etc. that span image chunks past
500. If we employ a DFS traversal to our graph, then we would possibly explore
the path A->B->C->D->etc. Then, when computing A->C afterwards, we realize that
A->B->C is a suboptimal path and so the cost from C->D->etc must then be
recomputed given the cost of the path A->C. In a case such as this, the
complexity of traversal actually increases beyond O(n^2). To prevent this (and
so I don't have to provide the analysis of a worst case DFS traversal) we use a
BFS traversal and maintain information on whether the cost of each path to a
node has been computed in order to prevent re-computations. In the code here, I
use a queue and if all paths to a node have not been calculated then I simply
move the node to the end of the queue so that it will be ready for traversal
after another pass through the queue. A way to improve this, though likely only
by a constant, would be to use a priority queue that prioritizes node order
based on number of paths leading to the node left to compute.

################################################################################
#
# The determined algorithmic complexity
#
################################################################################

Given the above analysis, I believe the complexity of my approach is O(n log n)
+ O(n^2). Determining the time complexity T(n) would be more difficult and will
perhaps be included later for thoroughness and fun.


The problem with my
submitted version is that the pruning does not work until a path has been
completed, which means that every possible internal path is computed, a *lot*
of which is duplicate effort, particularly in cases of highly connected graphs.
The approach coded and analyzed here in some ways is a dynamic programming
approach, if you consider that the subproblem to optimize is the path between a
subset of nodes (or rather, constructing a subset of the original image). But
with the way that the traversal works, it's difficult for me to say whether it
actually is dynamic programming.
'''

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
