import struct


class Response:
    ERROR_CODE = 9000
    REGISTER_CODE = 2100
    CLIENT_LIST = 2101
    PUBLIC_KEY = 2102
    MESSAGE_SENT = 2103
    WAITING_MESSAGES = 2104
    HEADER_SIZE = 7
    MAX_PAYLOAD_SIZE = HEADER_SIZE + 1 << 32

    def __init__(self, code, payload_size):
        self.version = 1
        self.code = code
        self.payload_size = payload_size

    def data(self):
        ver = struct.pack('B', self.version)
        code = struct.pack('<H', self.code)
        print(self.payload_size)
        payload_size = struct.pack('<I', self.payload_size)
        return ver + code + payload_size
