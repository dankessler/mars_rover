'''
Problem Description:

    Input:
        N - numBytes in original file
        L - latency of connection (s)
        B - bandwidth (bytes/second)
        C - numChunks
        A,B:
            A - start index of chunk (bytes)
            B - end index of chunk (bytes)

    Output:
        if there is a solution: min amount of time (s) to download each byte at least once
        else: no output

    Constraints:
        1 <= N, L, B < 2**32
        1 <= C <= 100000
'''
from RoverConnection import ConnectionFactory
from RoverImage import ImageFactory

from RoverImage import RoverImage
from RoverImage import Chunk
from RoverImage import Segment

if __name__ == '__main__':
    self.connInfo = ConnectionFactory.connInfoFromStdIn()
    self.imageChunks = ImageFactory.imageChunksFromStdIn(self.connInfo)

    roverImage = RoverImage(imageChunks)

    print(roverImage)

    segment = roverImage.getOptimalImageSegment(self.connInfo)
    if (segment is not None):
        print(segment.dlTime)
