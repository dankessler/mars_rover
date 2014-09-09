import unittest
import sys

from RoverConnection import ConnectionFactory
from RoverImage import ImageFactory
from RoverImage import RoverImage
from RoverImage import Chunk

class TestRoverImage(unittest.TestCase):
    _TEST_INPUT_FILE_ = 'src/unittest/resources/full.test.input'
    _TEST_IMAGE_SIZE_ = 2000
    _TEST_LATENCY_    = 25
    _TEST_BANDWIDTH_  = 15
    _TEST_NUM_CHUNKS_ = 7
    _TEST_IMAGE_CHUNKS_ = [(0, 200), (200, 400), (400, 600), (600, 800),
                           (800, 1000), (1000, 2000), (0, 1800)]

    def setUp(self):
        self.origStdIn = sys.stdin
        sys.stdin = open(TestRoverImage._TEST_INPUT_FILE_)

    def tearDown(self):
        assert self.origStdIn != sys.stdin

        sys.stdin.close()
        sys.stdin = self.origStdIn

    def testParseInput(self):
        connInfo = ConnectionFactory.connInfoFromStdIn()
        imageChunks = ImageFactory.imageChunksFromStdIn(connInfo)

        self.assertEqual(connInfo.imageSize(), TestRoverImage._TEST_IMAGE_SIZE_)
        self.assertEqual(connInfo.latency(),   TestRoverImage._TEST_LATENCY_)
        self.assertEqual(connInfo.bandwidth(), TestRoverImage._TEST_BANDWIDTH_)
        self.assertEqual(connInfo.numChunks(), TestRoverImage._TEST_NUM_CHUNKS_)

        for (parsedChunk, givenChunk) in zip(imageChunks, TestRoverImage._TEST_IMAGE_CHUNKS_):
            self.assertEqual(parsedChunk.start(), givenChunk[0])
            self.assertEqual(parsedChunk.end(), givenChunk[1])

        self.assertEqual(len(imageChunks), connInfo.numChunks())

    def testBasicChunkMethods(self):
        for (chunkStart, chunkEnd) in TestRoverImage._TEST_IMAGE_CHUNKS_:
            chunk = Chunk(chunkStart, chunkEnd)

            self.assertTrue(chunk.overlapsWithChunk(Chunk(chunkStart, chunkEnd + 1)))
            self.assertTrue(chunk.overlapsWithChunk(Chunk(chunkStart + 1, chunkEnd)))
            self.assertTrue(chunk.overlapsWithChunk(Chunk(chunkStart - 1, chunkEnd - 1)))

            self.assertFalse(chunk.overlapsWithChunk(Chunk(chunkStart - 1, chunkEnd)))

    def testAdvancedChunkMethods(self):
        baseChunk = Chunk(0, 200)

        self.assertEquals(baseChunk.size(), 200)
        self.assertNotEquals(baseChunk.size(), 199)
        self.assertNotEquals(baseChunk.size(), 201)

        self.assertTrue(baseChunk.isContiguous(Chunk(200, 400)))
        self.assertTrue(baseChunk.hasSameStart(Chunk(0, 1800)))
        self.assertTrue(baseChunk.hasSameEnd(Chunk(50, 200)))

        self.assertFalse(baseChunk.isContiguous(Chunk(0, 200)))
        self.assertFalse(baseChunk.isContiguous(Chunk(201, 299)))
        self.assertFalse(baseChunk.isContiguous(Chunk(199, 299)))
        self.assertFalse(baseChunk.hasSameStart(Chunk(1, 200)))
        self.assertFalse(baseChunk.hasSameEnd(Chunk(0, 199)))

    def testImageReconstruction(self):
        connInfo = ConnectionFactory.connInfoFromStdIn()
        imageChunks = ImageFactory.imageChunksFromStdIn(connInfo)

        roverImage = RoverImage(imageChunks)
        print(roverImage.calcImageReconstructionTime(connInfo))
