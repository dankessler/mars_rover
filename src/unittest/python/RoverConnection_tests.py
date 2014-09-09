import unittest
import sys

from RoverConnection import ConnectionFactory

class TestRoverConnection(unittest.TestCase):
    _TEST_INPUT_FILE_ = 'src/unittest/resources/connection.test.input'
    _TEST_IMAGE_SIZE_ = 2000
    _TEST_LATENCY_    = 15
    _TEST_BANDWIDTH_  = 10
    _TEST_NUM_CHUNKS_ = 7

    def setUp(self):
        self.origStdIn = sys.stdin
        sys.stdin = open(TestRoverConnection._TEST_INPUT_FILE_)

    def tearDown(self):
        assert self.origStdIn != sys.stdin

        sys.stdin.close()
        sys.stdin = self.origStdIn


    def testParseConnection(self):
        connInfo = ConnectionFactory.connInfoFromStdIn()

        self.assertEqual(connInfo.imageSize(), TestRoverConnection._TEST_IMAGE_SIZE_)
        self.assertEqual(connInfo.latency(),   TestRoverConnection._TEST_LATENCY_)
        self.assertEqual(connInfo.bandwidth(), TestRoverConnection._TEST_BANDWIDTH_)
        self.assertEqual(connInfo.numChunks(), TestRoverConnection._TEST_NUM_CHUNKS_)
