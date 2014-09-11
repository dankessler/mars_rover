import os
import sys

from RoverConnection import ConnectionFactory
from RoverImage import ImageFactory

from RoverImage import RoverImage
from RoverImage import Chunk
from RoverImage import Segment

from select import select

class Solver(object):
    _DEFAULT_INPUT_DIR_    = 'inputs'
    _DEFAULT_INPUT_SUFFIX_ = '.input'

    def parseInput():
        connInfo = ConnectionFactory.connInfoFromStdIn()
        imageChunks = ImageFactory.imageChunksFromStdIn(connInfo)

        return (connInfo, imageChunks)

    def getOptimalImageSegment(connInfo, imageChunks):
        roverImage = RoverImage(imageChunks)
        return roverImage.getOptimalImageSegment(connInfo)

    def filesFromDir(inputDir, inputSuffix):
        inputFilePaths = []

        for fileName in os.listdir(inputDir):
            if (fileName.endswith(inputSuffix)):
                inputFilePaths.append(os.path.join(inputDir, fileName))

        return inputFilePaths

    def getValidPaths(inputPaths=[]):
        validFilePaths = []

        for inputPath in inputPaths:
            if (os.path.exists(inputPath) and os.path.isfile(inputPath)):
                validFilePaths.append(inputPath)

        return validFilePaths


    def getInputFiles(inputDir=None, inputSuffix=None):
        # apparently the class name can't be resolved when used as defaults for
        # parameters
        inputDir = inputDir or Solver._DEFAULT_INPUT_DIR_
        inputSuffix = inputSuffix or Solver._DEFAULT_INPUT_SUFFIX_

        inputFilePaths = Solver.filesFromDir(inputDir, inputSuffix)
        return Solver.getValidPaths(inputFilePaths)

    def debugPrint(message):
        if ('debug' in sys.argv or 'DEBUG' in sys.argv):
            print(message)

if __name__ == '__main__':
    (connInfo, imageChunks) = Solver.parseInput()
    optimalSegment = Solver.getOptimalImageSegment(connInfo, imageChunks)

    if (optimalSegment is not None):
        print(optimalSegment.dlTime)
