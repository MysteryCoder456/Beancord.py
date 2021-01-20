import threading
import socket
import sqlite3

ADDR, PORT = "0.0.0.0", 8000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ADDR, PORT))
s.listen()

MSG_LENGTH = 2048
clients = []


def accept_new_clients():
    while True:
        client_socket, addr = s.accept()

        new_client_username = client_socket.recv(MSG_LENGTH).decode("utf8")
        clients.append(client_socket)

        new_client_listen_thread = threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True)
        new_client_listen_thread.start()

        print(f"New Connection from {addr}.\nUsername: {new_client_username}")


def listen_for_messages(client_socket):
    while True:
        msg = client_socket.recv(MSG_LENGTH)
        msg_split = msg.decode("utf8").split("|", 1)
        msg_sender = msg_split[0].strip("[SENDER]")

        if msg_split[1] == "[QUIT]":
            client_socket.close()
            print(f"{msg_sender} has left the chat...")
        else:
            msg_content = msg_split[1].strip("[CONTENT]")
            print(f"{msg_sender} says: {msg_content}")

        for c_sock in clients:
            c_sock.send(msg)


def main():
    print("Listening for connections...")
    accept_new_clients()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        s.close()
