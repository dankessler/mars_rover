import unittest
import sys
import os

from Solution import Solver

from RoverConnection import ConnectionFactory

from RoverImage import ImageFactory
from RoverImage import RoverImage
from RoverImage import Chunk
from RoverImage import Segment

class TestSampleInput(unittest.TestCase):
    def setUp(self):
        self.origStdIn = sys.stdin

    def tearDown(self):
        sys.stdin = self.origStdIn

    def testInputOne(self):
        for filePath in Solver.getInputFiles():
            Solver.debugPrint('opening file [%s]...' % filePath)

            sys.stdin = open(filePath)

            Solver.debugPrint('parsing input...')
            (connInfo, imageChunks) = Solver.parseInput()

            Solver.debugPrint('retrieving optimal image segment')
            optimalSegment = Solver.getOptimalImageSegment(connInfo, imageChunks)

            Solver.debugPrint('determining optimal image segment...')
            if (optimalSegment is not None):
                Solver.debugPrint(optimalSegment)
                print(optimalSegment.dlTime)

            sys.stdin.close()
            Solver.debugPrint('closed file [%s]...' % filePath)
