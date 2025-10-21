import struct


class Response:
    def __init__(self, version, code, payload_size):
        self.version = version
        self.code = code
        self.payload_size = payload_size

    def data(self):
        ver = struct.pack('B', self.version)
        code = struct.pack('<H', self.code)
        payload_size = struct.pack('<I', self.payload_size)
        return ver + code + payload_size
