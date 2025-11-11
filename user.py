import secrets
import threading
from message import Message
from response import Response

class User:
    cid_counter = 0
    users = []
    usernames = []
    cid_list = []
    client_list_lock = threading.Lock()
    USERNAME_MAX_SIZE_BYTES = 255
    CID_SIZE = 16
    max_user_num = (1 << 32) / (CID_SIZE + USERNAME_MAX_SIZE_BYTES)

    def __init__(self, username, publickey):
        self.cid = None
        self.username = username
        self.publickey = publickey
        self.waiting_messages = []
        self.waiting_messages_byte_size = 0

    def save_message(self, message: Message):
        if self.get_messages_size_bytes() + message.content_size > Response.MAX_PAYLOAD_SIZE:
            print(f"no more message room")
        else:
            self.waiting_messages.append(message)

    def get_messages_size_bytes(self):
        res = 0
        for message in self.waiting_messages:
            res += message.content_size
        return res

    @staticmethod
    def add_user(user):
        with User.client_list_lock:
            if user.username not in User.usernames:
                User.cid_counter += 1
                if User.cid_counter > User.max_user_num:
                    print("max user number reached, cant add more")
                    return 0
                user.cid = secrets.token_bytes(16)
                while user.cid in User.cid_list:
                    user.cid = secrets.token_bytes(16)
                User.users.append(user)
                User.usernames.append(user.username)
                User.cid_list.append(user.cid)
                return user.cid
            else:
                return 0

    def get_cid(self):
        return self.cid

    def get_username(self):
        return self.username

    def get_public_key(self):
        return self.publickey

    @staticmethod
    def get_user(user_cid):
        with User.client_list_lock:
            for user in User.users:
                if user_cid == user.cid:
                    return user
