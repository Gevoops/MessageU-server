import threading


class Message:
    UINT32_MAX = (1 << 32) - 1
    id_counter = 0
    id_counter_lock = threading.Lock()

    def __init__(self, from_cid, message_type, content_size, content):
        self.from_cid = from_cid
        self.messageID = Message.id_counter
        self.message_type = message_type
        self.content_size = content_size
        self.content = content
        with Message.id_counter_lock:
            Message.id_counter += 1
            if Message.id_counter >= Message.UINT32_MAX:
                Message.id_counter = 0

