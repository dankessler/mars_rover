class RoverImage(object):
    def __init__(self, chunks):
        self.chunks = chunks 

    def __str__(self):
        print('image chunks:')
        print(self.chunksToStr())

    '''
    stringify the chunks of this image
    '''
    def chunksToStr(self):
        chunksAsStr = ''

        for chunk in self.chunks:
            chunksAsStr += ('start: %d | end: %d\n' %
                            (chunk.start(), chunk.end()))

        return chunksAsStr

    '''
    the workhorse method for solving the mars rover image reconstruction
    problem
    '''
    def calcImageReconstructionTime(self, connInfo):
        segmentEnds   = {}
        segmentStarts = {}
        segmentDict   = {}

        for chunk in self.chunks:
            dlTime = connInfo.getDownloadTime(chunk.size())

            if (len(segmentDict) == 0):
                chunkSegment = Segment(chunk.start(), chunk.end(), dlTime)
                segmentDict[dlTime] = [chunkSegment]
                segmentEnds[chunk.end()] = [chunkSegment]
                segmentStarts[chunk.start()] = [chunkSegment]
                next

            if (chunk.end() not in segmentEnds):
                segmentEnds[chunk.end()] = []

            if (chunk.start() not in segmentStarts):
                segmentStarts[chunk.start()] = []

            # segment suffixes
            self.extendContigSegments(segmentDict, segmentEnds, connInfo, chunk, chunk.start())
            segmentEnds[chunk.end()].append(Segment(chunk.start(), chunk.end(), dlTime))

            # segment prefixes
            self.extendContigSegments(segmentDict, segmentStarts, connInfo, chunk, chunk.end())
            segmentStarts[chunk.start()].append(Segment(chunk.start(), chunk.end(), dlTime))

        return self.determineOptimalDownloadTime(segmentDict, connInfo)

    '''
    Search for other image segments that align with the beginning or end of
    this chunk. For all such image segments, remove any that have the same
    start and end byte indices *and* download time as this segment. Finally,
    add the new segment to the list of segments to keep track of
    '''
    def extendContigSegments(self, segmentByDownload, segmentByBoundary, connInfo, chunk, boundary):
        dlTime = connInfo.getDownloadTime(chunk.size())

        if (dlTime not in segmentByDownload):
            segmentByDownload[dlTime] = []

        print('number of contiguous segments to extend: %d' % len(self.findContiguousSegments(segmentByBoundary, boundary)))

        for contigSegment in self.findContiguousSegments(segmentByBoundary, boundary):
            # newly extended segment (previous segment with this chunk attached
            # to the beginning or end)
            segment = contigSegment.addChunk(chunk, dlTime)

            # remove redundant segments from consideration
            self.getPrunedSegmentsByDownload(segmentByDownload[dlTime], segment)

            # add this new segment for consideration
            segmentByDownload[dlTime].append(segment)
            print('added segment with download time %d to segmentDict' % dlTime)

    '''
    retrieve a list of segments that align to the given boundary (are
    contiguous)
    '''
    def findContiguousSegments(self, segmentDict, chunkBoundary):
        if (chunkBoundary in segmentDict):
            return segmentDict[chunkBoundary]
        return []

    '''
    construct a new list representing segments that are not considered
    redundant
    '''
    def getPrunedSegmentsByDownload(self, segmentsByDownload, segment):
        segments = []

        for oldSeg in segmentsByDownload:
            if (not segment.containsChunk(oldSeg)):
                segments.append(oldSeg)

        return segments

    '''
    Searches through the dictionary of downloadTime -> Segment in order to
    determine the minimum download time that retrieves the full Image from the
    rover
    '''
    def determineOptimalDownloadTime(self, segmentDict, connInfo):
        optimalDownloadTime = None
        optimalSegment = None

        print('%d entries in segment dictionary' % len(segmentDict.items()))

        for (downloadTime, segments) in segmentDict.items():
            if (optimalDownloadTime is None):
                optimalDownloadTime = downloadTime

            print('%d segments have download time %.02f' % (len(segments), downloadTime))

            for segment in segments:
                print('segment size: %d' % segment.size())
                print('image size: %d' % connInfo.imageSize())

                if (segment.size() == connInfo.imageSize()):
                    print('optimal download time: %.02f' % optimalDownloadTime)
                    print('segment download time: %.02f' % downloadTime)

                    if (downloadTime < optimalDownloadTime):
                        print('segment is optimal')

                        optimalDownloadTime = downloadTime
                        optimalSegment = segment

        if (optimalSegment is not None):
            print('start: %d end: %d' % (optimalSegment.start(), optimalSegment.end()))

        return optimalDownloadTime

class Chunk(object):
    def __init__(self, startByte, endByte):
        self.startByte = startByte
        self.endByte = endByte

    def start(self, newStart=None):
        if (newStart is not None):
            self.startByte = newStart

        return self.startByte

    def end(self, newEnd=None):
        if (newEnd is not None):
            self.endByte = newEnd

        return self.endByte

    def size(self):
        return self.endByte - self.startByte

    def isContiguous(self, otherChunk):
        return self.endByte == otherChunk.startByte

    def hasSameStart(self, otherChunk):
        return self.startByte == otherChunk.startByte

    def hasSameEnd(self, otherChunk):
        return self.endByte == otherChunk.endByte

    def overlapsWithChunk(self, otherChunk):
        return (self.containsBytePos(otherChunk.start()) or
                self.containsBytePos(otherChunk.end()))

    def containsChunk(self, otherChunk):
        return (self.containsBytePos(otherChunk.start()) and
                self.containsBytePos(otherChunk.end()))

    def containsBytePos(self, bytePos):
        return (bytePos >= self.startByte and bytePos < self.endByte)

class Segment(Chunk):
    def __init__(self, startByte, endByte, downloadTime):
        super(Segment, self).__init__(startByte, endByte)

        self.downloadTime = downloadTime

    def download(self):
        return self.downloadTime

    def addChunk(self, chunk, downloadTime):
        newStart = min(self.start(), chunk.start())
        newEnd = min(self.end(), chunk.end())

        return Segment(newStart, newEnd, self.downloadTime + downloadTime)

class ImageFactory(object):
    def imageChunksFromStdIn(connInfo):
        chunks = []

        for chunkNum in range(connInfo.numChunks()):
            (startByte, endByte) = str(input()).split(',')
            chunks.append(Chunk(int(startByte), int(endByte)))

        return chunks
