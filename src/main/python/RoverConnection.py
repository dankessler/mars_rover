_BYTE_COUNT_KEY_  = 'numBytes'
_LATENCY_KEY_     = 'latency'
_BANDWIDTH_KEY_   = 'bandwidth'
_CHUNK_COUNT_KEY_ = 'numChunks'

class ConnInfo(object):
    def __init__(self, paramDict):
        self.paramInfo = paramDict

    def __str__(self):
        print(self.paramsToStr())

    def imageSize(self):
        return self.paramInfo[_BYTE_COUNT_KEY_]

    def latency(self):
        return self.paramInfo[_LATENCY_KEY_]

    def bandwidth(self):
        return self.paramInfo[_BANDWIDTH_KEY_]

    def numChunks(self):
        return self.paramInfo[_CHUNK_COUNT_KEY_]

    def getDlTime(self, chunk):
        return float((2 * self.paramInfo[_LATENCY_KEY_]) +
                     (chunk.size() / self.paramInfo[_BANDWIDTH_KEY_]))

    def paramsToStr(self):
        paramsAsStr = ''

        for (param, value) in self.paramInfo.items():
            paramsAsStr += ('%s: %d\n' % (param, value))

        return paramsAsStr

    def __str__(self):
        return self.paramsToStr()

class ConnectionFactory(object):
    # context params are in order of expected input
    _CONTEXT_PARAMS_ = (_BYTE_COUNT_KEY_, _LATENCY_KEY_,
                        _BANDWIDTH_KEY_, _CHUNK_COUNT_KEY_)

    def connInfoFromStdIn():
        connParams = {}

        for param in ConnectionFactory._CONTEXT_PARAMS_:
            connParams[param] = int(input())

        return ConnInfo(connParams)
