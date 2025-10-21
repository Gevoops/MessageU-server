import socket
import struct
import binascii

from user import User
from response import Response
from message import Message

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

server_socket.listen(5)

print("starting server")

while True:
    client_socket, client_address = server_socket.accept()
    print("client connected")
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("client disconnected")
                break
            hex_data = binascii.hexlify(data)
            print(f"received from client: {hex_data.decode('utf-8')}")
            clientID = data[:16]
            clientVersion = data[16]
            print(clientVersion)
            requestCode = data[17:19]
            requestCode = struct.unpack('<h', requestCode)[0]
            print(requestCode)
            payloadSize = data[19:23]
            payloadSize = struct.unpack('<i', payloadSize)[0]
            print(payloadSize)
            payload = data[23:]
            hex_payload = binascii.hexlify(payload)
            print(f"{hex_payload.decode('utf-8')}")

            if requestCode != 600 and clientID not in User.user_uuids:
                response = Response(VERSION, 9000, 0)
                print("sent 900 from here!")
                client_socket.send(response.data())
                continue

            match requestCode:
                case 600:
                    username = payload[0:255]
                    username_string = username.decode("utf-8")
                    for i, char in enumerate(username_string):
                        if not char.isalnum():
                            username_string = username_string[:i]
                            print("username is: " + username_string)
                            break
                    if username not in User.usernames:
                        publickey = payload[255:]
                        print("adding user")
                        user1 = User(username, publickey)
                        uuid = User.add_user(user1)
                        response = Response(VERSION, 2100, 16)
                        payload = uuid
                        response = response.data() + payload
                        hex_response = binascii.hexlify(response)
                        print(f"sent to client {hex_response.decode('utf-8')} ")
                        client_socket.send(response)
                case 601:
                    response = Response(VERSION, 2101, (255 + 16) * (len(User.users) - 1))
                    response = response.data()
                    for user in User.users:
                        if user.get_uuid() != clientID:
                            response += user.get_username()
                            response += user.get_uuid()
                            print(f"user.get_uuid {user.get_uuid().hex()} ")
                            print(user.get_username()[254])

                    hex_response = binascii.hexlify(response)
                    print(f"sending to list {hex_response.decode('utf-8')} ")
                    client_socket.send(response)
                case 602:
                    target_uuid = payload
                    print(" request for publickey")
                    print(f" target uuid is :  {payload.hex()}")
                    response = Response(VERSION, 2102, (16 + 160))
                    response = response.data()
                    for user in User.users:
                        if user.get_uuid() == target_uuid:
                            response += target_uuid
                            response += user.get_public_key()
                            break
                    client_socket.send(response)
                case 603:
                    target_client_ID = payload[0:16]
                    message_type = payload[16]
                    print(f"message type is: {message_type}")
                    content_size = int.from_bytes(payload[17:21], byteorder='big')
                    content = payload[21:21 + content_size]
                    print(f"content is: {content.decode('utf-8',errors='replace')}")
                    message = Message(content, message_type, content_size)
                    for user in User.users:
                        if user.get_uuid() == target_client_ID:
                            user.save_message(message)

                case _:
                    print("request code none existent ")
                    response = Response(VERSION, 9000, 0)
                    client_socket.send(response.data())

        except ConnectionResetError:
            print("client disconnected")
            break
    client_socket.close()
