class Message:
    UINT32_MAX = (1 << 32) - 1
    id_counter = 0

    def __init__(self, content, message_type, size):
        self.content = content
        self.messageID = Message.id_counter
        self.message_type = message_type
        self.size = size
        Message.id_counter += 1

        if Message.id_counter >= Message.UINT32_MAX:
            Message.id_counter = 0
