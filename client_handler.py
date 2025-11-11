import struct
from user import User
from response import Response
from message import Message


class ClientHandler:
    REGISTER = 600
    CLIENT_LIST = 601
    PUBLIC_KEY = 602
    MESSAGE_REQ = 603
    GET_MESSAGES = 604
    ERROR_RESPONSE_CODE = 9000
    MAX_REQUEST_SIZE_BYTES = 4096

    def __init__(self, client_socket):
        self.buffer = b""
        self.curr_cid = b""
        self.client_version = b""
        self.request_code = b""
        self.payload_size = b""
        self.payload = b""
        self.client_socket = client_socket

    def run(self):
        if not self._receive():
            return False
        self._parse_request()
        self._handle_request()
        self._clean_up()
        return True

    def _receive(self):
        try:
            data = self.client_socket.recv(ClientHandler.MAX_REQUEST_SIZE_BYTES)
            if not data:
                print("client disconnected")
                return False
            self.buffer += data
            return True
        except ConnectionResetError:
            print("client disconnected")
            return False

    def _parse_request(self):
        self.curr_cid = self.buffer[:User.CID_SIZE]
        self.client_version = self.buffer[User.CID_SIZE]
        self.request_code = self.buffer[17:19]
        self.request_code = struct.unpack('<h', self.request_code)[0]
        self.payload_size = self.buffer[19:23]
        self.payload_size = struct.unpack('<i', self.payload_size)[0]
        self.payload = self.buffer[23:]

    def _handle_request(self):
        if self.request_code != self.REGISTER and self.curr_cid not in User.cid_list:
            print("unregistered user asked something else then register")
            response = Response(ClientHandler.ERROR_RESPONSE_CODE, 0)
            self.client_socket.sendall(response.data())
            return

        match self.request_code:
            case ClientHandler.REGISTER:
                self._register()
            case ClientHandler.CLIENT_LIST:
                self._client_list()
            case ClientHandler.PUBLIC_KEY:
                self._public_key()
            case ClientHandler.MESSAGE_REQ:
                self._message_req()
            case ClientHandler.GET_MESSAGES:
                self._get_messages()
            case _:
                print("request code none existent ")
                response = Response(ClientHandler.ERROR_RESPONSE_CODE, 0)
                self.client_socket.sendall(response.data())

    def _register(self):
        username = self.payload[0:255]
        publickey = self.payload[255:]
        user1 = User(username, publickey)
        uuid = User.add_user(user1)
        if uuid == 0:
            response = Response(ClientHandler.ERROR_RESPONSE_CODE, 0)
            self.client_socket.sendall(response.data())
        else:
            response = Response(Response.REGISTER_CODE, User.CID_SIZE)
            response = response.data() + uuid
            print("adding user")
            self.client_socket.sendall(response)

    def _client_list(self):
        payload_size = (User.USERNAME_MAX_SIZE_BYTES + User.CID_SIZE) * (len(User.users) - 1)
        response = Response(Response.CLIENT_LIST,  payload_size)
        response = response.data()
        for user in User.users:
            if user.get_cid() != self.curr_cid:
                response += user.get_username()
                response += user.get_cid()
                print(f"user.get_cid {user.get_cid().hex()} ")
                print(user.get_username()[254])

        print(f"sending user list ")
        self.client_socket.sendall(response)

    def _public_key(self):
        target_uuid = self.payload
        response = Response(2102, (16 + 160))
        response = response.data()
        for user in User.users:
            if user.get_cid() == target_uuid:
                response += target_uuid
                response += user.get_public_key()
                break
        self.client_socket.sendall(response)

    def _message_req(self):
        target_client_id = self.payload[0:16]
        message_type = self.payload[16]
        content_size = int.from_bytes(self.payload[17:21], byteorder='little')
        content = self.payload[21:21 + content_size]
        print(f"content is: {content.decode('utf-8', errors='replace')}")
        message = Message(self.curr_cid, message_type, content_size, content)
        User.get_user(target_client_id).save_message(message)
        response = Response(2103, 16 + 4)
        response = response.data()
        response += target_client_id
        response += message.messageID.to_bytes(4, byteorder='little')
        print(message.messageID)
        self.client_socket.sendall(response)

    def _get_messages(self):
        print("u are in 604 handler case")
        message_header_size = 16 + 4 + 1 + 4
        user = User.get_user(self.curr_cid)
        print(len(user.waiting_messages))
        print(message_header_size)
        print(user.get_messages_size_bytes())
        response = Response(2104, len(user.waiting_messages)
                            * message_header_size + user.get_messages_size_bytes())
        response = response.data()
        for message in user.waiting_messages:
            print(f"user.get_cid {message.from_cid.hex()} ")
            response += message.from_cid
            response += message.messageID.to_bytes(4, byteorder="little")
            response += message.message_type.to_bytes(1, byteorder="little")
            response += message.content_size.to_bytes(4, byteorder="little")
            response += message.content

        user.waiting_messages.clear()
        print(f"response size {len(response)}")
        self.client_socket.sendall(response)

    def _clean_up(self):
        self.buffer = b""
        self.curr_cid = b""
        self.client_version = b""
        self.request_code = b""
        self.payload_size = b""
        self.payload = b""
