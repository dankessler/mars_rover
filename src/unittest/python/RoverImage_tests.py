import unittest
import sys

from RoverConnection import ConnectionFactory
from RoverImage import ImageFactory
from RoverImage import RoverImage
from RoverImage import Chunk
from RoverImage import Segment

class TestRoverImage(unittest.TestCase):
    _TEST_INPUT_FILE_ = 'src/unittest/resources/full.test.input'
    _TEST_IMAGE_SIZE_ = 2000
    _TEST_LATENCY_    = 5
    _TEST_BANDWIDTH_  = 10
    _TEST_NUM_CHUNKS_ = 7
    _TEST_IMAGE_CHUNKS_ = [(0, 200), (200, 400), (400, 600), (600, 800),
                           (800, 1000), (1000, 2000), (0, 1800)]
    _TEST_SORTED_CHUNKS_ = [(0, 200), (0, 1800), (200, 400), (400, 600),
                            (600, 800), (800, 1000), (1000, 2000)]

    def setUp(self):
        self.origStdIn = sys.stdin
        sys.stdin = open(TestRoverImage._TEST_INPUT_FILE_)

        self.connInfo = ConnectionFactory.connInfoFromStdIn()
        self.imageChunks = ImageFactory.imageChunksFromStdIn(self.connInfo)

    def tearDown(self):
        assert self.origStdIn != sys.stdin

        sys.stdin.close()
        sys.stdin = self.origStdIn

    def testParseInput(self):
        self.assertEqual(self.connInfo.imageSize(), TestRoverImage._TEST_IMAGE_SIZE_)
        self.assertEqual(self.connInfo.latency(),   TestRoverImage._TEST_LATENCY_)
        self.assertEqual(self.connInfo.bandwidth(), TestRoverImage._TEST_BANDWIDTH_)
        self.assertEqual(self.connInfo.numChunks(), TestRoverImage._TEST_NUM_CHUNKS_)

        for (parsedChunk, givenChunk) in zip(self.imageChunks,
                                             TestRoverImage._TEST_SORTED_CHUNKS_):
            self.assertEqual(parsedChunk.start(), givenChunk[0])
            self.assertEqual(parsedChunk.end(), givenChunk[1])

        self.assertEqual(len(self.imageChunks), self.connInfo.numChunks())

    def testBasicChunkMethods(self):
        baseChunk = Chunk(0, 200)

        self.assertEquals(baseChunk.start(), 0)
        self.assertEquals(baseChunk.end(), 200)

        self.assertEquals(baseChunk.size(), 200)
        self.assertNotEquals(baseChunk.size(), 201)
        self.assertNotEquals(Chunk(200, 0).size(), -200)

        baseChunk.start(50)
        self.assertEquals(baseChunk.start(), 50)

        baseChunk.end(250)
        self.assertEquals(baseChunk.end(), 250)

    def testAdvancedChunkMethods(self):
        for (chunkStart, chunkEnd) in TestRoverImage._TEST_IMAGE_CHUNKS_:
            chunk = Chunk(chunkStart, chunkEnd)

            # check that *EITHER* the beginning or the end of the chunks are
            # aligned
            self.assertTrue(chunk.isAligned(Chunk(chunkStart, chunkEnd)))
            self.assertTrue(chunk.isAligned(Chunk(chunkStart, chunkEnd + 1)))
            self.assertTrue(chunk.isAligned(Chunk(chunkStart + 1, chunkEnd)))

            # check that *NEITHER* the beginning or the end of the chunks are
            # aligned
            self.assertFalse(chunk.isAligned(Chunk(chunkStart - 1, chunkEnd - 1)))
            self.assertFalse(chunk.isAligned(Chunk(chunkStart + 1, chunkEnd + 1)))
            self.assertFalse(chunk.isAligned(Chunk(chunkStart + 1, chunkEnd - 1)))
            self.assertFalse(chunk.isAligned(Chunk(chunkStart - 1, chunkEnd + 1)))

            # check that the next chunk follows the current one, so as to
            # ensure acyclic dags
            self.assertTrue(chunk.isShifted(Chunk(chunkStart + 1, chunkEnd + 1)))

            # check that we can identify when the next chunk does not follow
            # the current one
            self.assertFalse(chunk.isShifted(Chunk(chunkStart, chunkEnd + 1)))
            self.assertFalse(chunk.isShifted(Chunk(chunkStart + 1, chunkEnd)))
            self.assertFalse(chunk.isShifted(Chunk(chunkStart - 1, chunkEnd - 1)))
            self.assertFalse(chunk.isShifted(Chunk(chunkStart, chunkEnd - 1)))
            self.assertFalse(chunk.isShifted(Chunk(chunkStart - 1, chunkEnd)))

            # check that the chunks are overlapping only when the start of the
            # second chunk is before or aligned with the end of the first chunk
            self.assertTrue(chunk.isOverlapping(Chunk(chunkEnd, chunkEnd + 200)))
            self.assertTrue(chunk.isOverlapping(Chunk(chunkEnd - 1, chunkEnd + 200)))
            self.assertFalse(chunk.isOverlapping(Chunk(chunkEnd + 1, chunkEnd + 200)))

    def testSegmentMethods(self):
        chunkOne   = Chunk(0, 200)
        chunkTwo   = Chunk(250, 500)
        chunkThree = Chunk(500, 800)

        dlOne   = self.connInfo.getDlTime(chunkOne)
        dlTwo   = self.connInfo.getDlTime(chunkTwo)
        dlThree = self.connInfo.getDlTime(chunkThree)

        segmentOne   = Segment()
        segmentTwo   = Segment.extend(segmentOne, chunkOne, dlOne)
        segmentThree = Segment.extend(segmentTwo, chunkTwo, dlTwo)
        segmentFour  = Segment.extend(segmentThree, chunkThree, dlThree)

        self.assertEquals(segmentTwo.addTime(10),   dlOne + 10)
        self.assertEquals(segmentThree.addTime(12), dlOne + dlTwo + 12)
        self.assertEquals(segmentFour.addTime(6.7), dlOne + dlTwo + dlThree + 6.7)

        self.assertTrue(segmentOne.isDiscoverable(chunkOne))
        self.assertTrue(segmentThree.isDiscoverable(chunkThree))
        self.assertFalse(segmentTwo.isDiscoverable(chunkTwo))

        self.assertFalse(segmentFour.isDiscoverable(chunkThree))
        self.assertFalse(segmentOne.isDiscoverable(chunkTwo))
        self.assertFalse(segmentTwo.isDiscoverable(chunkThree))

    def testImageReconstruction(self):
        roverImage = RoverImage(self.imageChunks)

        segment = roverImage.getOptimalImageSegment(self.connInfo)
        if (segment is not None):
            print(segment.dlTime)
