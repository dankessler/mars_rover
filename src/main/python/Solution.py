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
import RoverConnection.ConnectionFactory
import RoverImage.ImageFactory

if __name__ == '__main__':
    connInfo = ConnectionFactory.connInfoFromStdIn()
    imageChunks = ImageFactory.imageChunksFromStdIn(connInfo)

    roverImage = RoverImage(imageChunks)
    roverImage.preprocessChunks()
