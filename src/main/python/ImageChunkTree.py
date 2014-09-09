from RoverImage import Chunk

class SuffixTree(object):
    def __init__(self):
        self.root = SuffixNode(Chunk(0, 0, 0))

    def addChunk(self, chunk):
        self.root.addChunk(chunk)

class SuffixNode(object):
    def __init__(self, chunk):
        self.chunk = chunk

    def containsChunk(self, otherChunk):
        return (self.isContiguous(otherChunk) or
                self.containsbytePos(otherChunk))

    def isContiguous(self, otherChunk):
        return self.imageChunk.end() == otherChunk.start()

    def addChunk(self, newChunk):
        if (self.isContiguous(newChunk)):
            self.children.add(byteStart, byteEnd, downloadTime)

        elif (self.insert
