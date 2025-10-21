import secrets
from message import Message


class User:
    uuid_counter = 0
    users = []
    usernames = []
    user_uuids = []

    def __init__(self, username, publickey):
        self.uuid = None
        self.username = username
        self.publickey = publickey
        self.waiting_messages = []

    def save_message(self, message: Message):
        self.waiting_messages.append(message)

    @staticmethod
    def add_user(user):
        if user.username not in User.usernames:
            User.uuid_counter += 1
            user.uuid = secrets.token_bytes(16)
            while user.uuid in User.user_uuids:
                user.uuid = secrets.token_bytes(16)
            User.users.append(user)
            User.usernames.append(user.username)
            User.user_uuids.append(user.uuid)
            return user.uuid
        else:
            return 0

    def get_uuid(self):
        return self.uuid

    def get_username(self):
        return self.username

    def get_public_key(self):
        return self.publickey
