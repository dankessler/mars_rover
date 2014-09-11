from copy import deepcopy

class RoverImage(object):
    def __init__(self, chunks):
        self.chunks = chunks 
        self.segments = [Segment()]
        self.optimalSegment = None

    '''
    the workhorse method for solving the mars rover image reconstruction
    problem
    '''
    def getOptimalImageSegment(self, connInfo):
        while (len(self.segments) > 0):
            self.extendSegments(connInfo)
            self.checkForOptimalSegment(connInfo)

        return self.optimalSegment

    def extendSegments(self, connInfo):
        extendedSegments = []

        for segment in self.segments:
            for chunk in self.chunks:
                if (segment.isDiscoverable(chunk)):
                    extendedSegments.append(Segment.extend(
                        segment, chunk, connInfo.getDlTime(chunk)
                    ))

        # once all segments have been extended, we throw away the old queue of
        # segments and continue computation with only the extended segments
        self.segments = extendedSegments

    def checkForOptimalSegment(self, connInfo):
        potentialSegments = []

        for segment in self.segments:
            if (segment.size() == connInfo.imageSize()):
                if (self.optimalSegment is None or
                    segment.dlTime < self.optimalSegment.dlTime):
                    self.optimalSegment = segment

            elif (self.optimalSegment is None or
                  segment.dlTime <= self.optimalSegment.dlTime):
                potentialSegments.append(segment)

        # all extended segments are either pruned or maintained as potentially
        # optimal segments. We throw away the old queue of segments
        self.segments = potentialSegments

class Chunk(object):
    def __init__(self, startByte, endByte):
        self.startByte = startByte
        self.endByte = endByte

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

    def isAligned(self, chunk):
        return chunk.start() == self.start() or chunk.end() == self.end()

    def isShifted(self, chunk):
        return chunk.start() > self.start() and chunk.end() > self.end()

    def isOverlapping(self, chunk):
        return chunk.start() <= self.end()

    def __str__(self):
        return '[%d, %d]' % (self.start(), self.end())

class Segment(Chunk):
    def __init__(self, startByte=0, endByte=0, dlTime=0, chunks=[]):
        super(Segment, self).__init__(startByte, endByte)

        self.dlTime = dlTime
        self.chunks = chunks

    def addTime(self, addTime):
        return self.dlTime + addTime

    def isDiscoverable(self, chunk):
        return (self.end() == chunk.start() or
               (self.isOverlapping(chunk) and self.isShifted(chunk)))

    def extend(segment, chunk, dlTime):
        chunkSeq = deepcopy(segment.chunks)
        chunkSeq.append(chunk)

        return Segment(segment.start(), chunk.end(), segment.addTime(dlTime), chunkSeq)

    def __str__(self):
        chunkStrList = []

        for chunk in self.chunks:
            chunkStrList.append(str(chunk))

        return ','.join(chunkStrList)

class ImageFactory(object):
    def imageChunksFromStdIn(connInfo):
        chunks = []

        for chunkNum in range(connInfo.numChunks()):
            (startByte, endByte) = str(input()).split(',')
            chunks.append(Chunk(int(startByte), int(endByte)))

        return sorted(sorted(chunks, key=lambda chunk: chunk.end()),
                      key=lambda chunk: chunk.start())
