import socket
import threading
from client_handler import ClientHandler

HOST = '127.0.0.1'
PORT = 1357
VERSION = 1

try:
    with open("myport.info", "r", encoding="utf-8") as file:
        PORT = int(file.read())
except FileNotFoundError:
    print(f"Error, port file doesnt exist, working in default port {PORT}")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print("starting server")


def client_thread(c_socket):
    cl_handler = ClientHandler(c_socket)
    while True:
        if not cl_handler.run():
            break
    c_socket.close()


while True:
    client_socket, client_address = server_socket.accept()
    print("client connected")
    threading.Thread(target=client_thread, args=(client_socket,), daemon=True).start()





        # try:
        #     data = client_socket.recv(1024)
        #     if not data:
        #         print("client disconnected")
        #         break
        #     hex_data = binascii.hexlify(data)
        #     curr_cid = data[:16]
        #     clientVersion = data[16]
        #     print(clientVersion)
        #     requestCode = data[17:19]
        #     requestCode = struct.unpack('<h', requestCode)[0]
        #     print(requestCode)
        #     payloadSize = data[19:23]
        #     payloadSize = struct.unpack('<i', payloadSize)[0]
        #     print(payloadSize)
        #     payload = data[23:]
        #     hex_payload = binascii.hexlify(payload)
        #     print(f"{hex_payload.decode('utf-8')}")
        #
        #     if requestCode != 600 and curr_cid not in User.cid_list:
        #         response = Response(9000, 0)
        #         print("unregistered user asked something else then _register")
        #         client_socket.send(response.data())
        #         continue
        #
        #     match requestCode:
        #         case 600:
        #             username = payload[0:255]
        #             username_string = username.decode("utf-8")
        #             for i, char in enumerate(username_string):
        #                 if not char.isalnum():
        #                     username_string = username_string[:i]
        #                     print("username is: " + username_string)
        #                     break
        #             if username not in User.usernames:
        #                 publickey = payload[255:]
        #                 print("adding user")
        #                 user1 = User(username, publickey)
        #                 uuid = User.add_user(user1)
        #                 response = Response(2100, 16)
        #                 response = response.data() + uuid
        #                 client_socket.send(response)
        #             else:
        #                 response = Response(9000, 0)
        #                 client_socket.send(response.data())
        #         case 601:
        #             response = Response(2101, (255 + 16) * (len(User.users) - 1))
        #             response = response.data()
        #             for user in User.users:
        #                 if user.get_cid() != curr_cid:
        #                     response += user.get_username()
        #                     response += user.get_cid()
        #                     print(f"user.get_cid {user.get_cid().hex()} ")
        #                     print(user.get_username()[254])
        #
        #             hex_response = binascii.hexlify(response)
        #             print(f"sending user list ")
        #             client_socket.send(response)
        #         case 602:
        #             target_uuid = payload
        #             print(" request for publickey")
        #             print(f" target uuid is :  {payload.hex()}")
        #             response = Response(2102, (16 + 160))
        #             response = response.data()
        #             for user in User.users:
        #                 if user.get_cid() == target_uuid:
        #                     response += target_uuid
        #                     response += user.get_public_key()
        #                     break
        #             client_socket.send(response)
        #         case 603:
        #             target_client_ID = payload[0:16]
        #             message_type = payload[16]
        #             print(f"message type is: {message_type}")
        #             content_size = int.from_bytes(payload[17:21], byteorder='little')
        #             content = payload[21:21 + content_size]
        #             print(f"content is: {content.decode('utf-8',errors='replace')}")
        #             message = Message(curr_cid, message_type, content_size, content)
        #             User.get_user(target_client_ID).save_message(message)
        #             response = Response(2103, 16 + 4)
        #             response = response.data()
        #             response += target_client_ID
        #             response += message.messageID.to_bytes(4, byteorder='little')
        #             print(message.messageID)
        #             client_socket.send(response)
        #         case 604:
        #             print("u are in 604 handler case")
        #             message_header_size = 16 + 4 + 1 + 4
        #             user = User.get_user(curr_cid)
        #             print(len(user.waiting_messages))
        #             print(message_header_size)
        #             print(user.get_messages_size_bytes())
        #             response = Response(2104, len(user.waiting_messages)
        #                                 * message_header_size + user.get_messages_size_bytes())
        #             response = response.data()
        #             for message in user.waiting_messages:
        #                 print(f"user.get_cid {message.from_cid.hex()} ")
        #                 response += message.from_cid
        #                 response += message.messageID.to_bytes(4, byteorder="little")
        #                 response += message.message_type.to_bytes(1, byteorder="little")
        #                 response += message.content_size.to_bytes(4, byteorder="little")
        #                 response += message.content
        #
        #             user.waiting_messages.clear()
        #             print(f"response size {len(response)}")
        #             client_socket.send(response)
        #         case _:
        #             print("request code none existent ")
        #             response = Response(9000, 0)
        #             client_socket.send(response.data())
        #
        # except ConnectionResetError:
        #     print("client disconnected")
        #     break



