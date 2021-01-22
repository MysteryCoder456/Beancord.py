import datetime
import threading
import socket
import random
import sqlite3
import time

ADDR, PORT = "0.0.0.0", 8000
MSG_LENGTH = 2048
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ADDR, PORT))
s.listen()

clients = {}

db_file = "db.sqlite3"
conn = sqlite3.connect(db_file, check_same_thread=False)
c = conn.cursor()


def create_db_tables():
    c.execute("""
    CREATE TABLE IF NOT EXISTS "messages" (
	    "sender"	TEXT,
	    "content"	TEXT,
	    "datetime"	TEXT
    )
    """)
    conn.commit()


def generate_uuid():
    while True:
        uuid = ''.join([str(random.choice(range(10))) for i in range(5)])
        if uuid not in clients.keys():
            return uuid


def accept_new_clients():
    while True:
        client_socket, addr = s.accept()
        new_client_username = client_socket.recv(MSG_LENGTH).decode("utf8")

        if len([key for key in clients if clients[key][1] == new_client_username]) > 0:
            client_socket.send(b"[DUPLICATE NAME]")
            client_socket.close()
            continue

        client_socket.send(b"[CONNECTION SUCCESS]")

        new_uuid = generate_uuid()
        clients[new_uuid] = (client_socket, new_client_username)

        new_client_listen_thread = threading.Thread(target=listen_for_messages, args=(client_socket, new_uuid), daemon=True)
        new_client_listen_thread.start()

        print(f"New Connection from {addr}.\nUsername: {new_client_username}, UUID: {new_uuid}")

        join_msg = f"[SENDER]{new_client_username}[SENDER]|[JOIN]".encode("utf8")
        for key in clients:
            if clients[new_uuid] is not clients[key]:
                clients[key][0].send(join_msg)

        c.execute("SELECT * FROM messages")
        messages = c.fetchall()
        messages.sort(key=lambda x: datetime.datetime.strptime(x[2], DATETIME_FORMAT))

        for message in messages:
            encoded_msg = f"[SENDER]{message[0]}[SENDER]|[CONTENT]{message[1]}[CONTENT]".encode("utf8")
            client_socket.send(encoded_msg)
            time.sleep(0.02)  # time delay to not overwhelm client


def listen_for_messages(client_socket, uuid):
    while True:
        msg = client_socket.recv(MSG_LENGTH)
        msg_split = msg.decode("utf8").split("|", 1)
        msg_sender = msg_split[0].replace("[SENDER]", "")

        if msg_split[1] == "[QUIT]":
            client_socket.close()
            del clients[uuid]
            print(f"{msg_sender} has left the chat...")

            for key in clients:
                clients[key][0].send(msg)

            return

        msg_content = msg_split[1].replace("[CONTENT]", "")
        print(f"{msg_sender} says: {msg_content}")

        for key in clients:
            if clients[uuid] is not clients[key]:
                clients[key][0].send(msg)

        current_datetime = datetime.datetime.now().strftime(DATETIME_FORMAT)

        c.execute(
            "INSERT INTO messages VALUES (:sender, :content, :datetime)",
            {
                "sender": msg_sender,
                "content": msg_content,
                "datetime": current_datetime
            }
        )

        conn.commit()


def main():
    print("Creating Database Tables...")
    create_db_tables()

    print("Listening for connections...")
    accept_new_clients()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        s.close()
