import socket
import threading
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

MSG_LENGTH = 2048
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None


class SenderLabel(Label):
    pass


class MessageLabel(Label):
    pass


class LoginWindow(Screen, FloatLayout):
    username_entry = ObjectProperty(None)
    ip_entry = ObjectProperty(None)
    port_entry = ObjectProperty(None)

    def connect(self):
        global username, s

        username = self.username_entry.text
        ip_addr = self.ip_entry.text
        port = self.port_entry.text

        if username.strip() == "":
            print("Please give a username!")

            b = Button(text="Dismiss")
            popup = Popup(title="Please give a username!", content=b, auto_dismiss=False, size=(100, 100))
            b.bind(on_press=popup.dismiss)
            popup.open()

            return

        if ip_addr.strip() == "":
            print("Please give an address!")

            b = Button(text="Dismiss")
            popup = Popup(title="Please give an address!", content=b, auto_dismiss=False, size=(100, 100))
            b.bind(on_press=popup.dismiss)
            popup.open()

            return

        if port.strip() == "":
            port = 8000

        print(f"Connecting to {ip_addr} at port {port} as {username}...")

        s.settimeout(10)
        popup_title = None

        try:
            s.connect((ip_addr, int(port)))
        except socket.gaierror:
            print("Invalid address!")
            popup_title = "Invalid Address!"
        except ValueError:
            print("Invalid port!")
            popup_title = "Invalid Port"
        except ConnectionRefusedError:
            print("Server not started!")
            popup_title = "Server has not started!"
        except socket.timeout:
            print("Server took too long to respond!")
            popup_title = "Server took too long to respond!"
        except OSError:
            print("Error has occured!")
            s.close()
            popup_title = "An error has occured!"
        finally:
            s.settimeout(None)

        if popup_title is not None:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            b = Button(text="Dismiss")
            popup = Popup(title=popup_title, content=b, auto_dismiss=False, size=(100, 100))
            b.bind(on_press=popup.dismiss)
            popup.open()

            return

        s.send(username.encode("utf8"))
        response = s.recv(MSG_LENGTH).decode("utf8")

        if response == "[DUPLICATE NAME]":
            print(f"The username {username} is already taken!")

            b = Button(text="Dismiss")
            popup = Popup(title="This username is already taken!", content=b, auto_dismiss=False, size=(100, 100))
            b.bind(on_press=popup.dismiss)
            popup.open()

            s.close()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            return

        if response == "[CONNECTION SUCCESS]":
            print("Connection successfully established!")
            self.manager.current = "main"


class MainWindow(Screen, FloatLayout):
    scroll_view = ObjectProperty(None)
    messages_grid = ObjectProperty(None)
    message_entry = ObjectProperty(None)

    def on_pre_enter(self):
        msg_listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        msg_listen_thread.start()

    def listen_for_messages(self):
        while True:
            try:
                msg = s.recv(MSG_LENGTH)
            except Exception as e:
                print(e)
                return

            msg_split = msg.decode("utf8").split("|", 1)
            msg_sender = msg_split[0].strip("[SENDER]")

            sender_label = SenderLabel(text=msg_sender)

            if msg_split[1] == "[QUIT]":
                content_label = MessageLabel(text="has left the chat...", bold=True)
                print(f"{msg_sender} has left the chat...")
            else:
                msg_content = msg_split[1].strip("[CONTENT]")
                content_label = MessageLabel(text=msg_content)
                print(f"{msg_sender} says: {msg_content}")

            self.messages_grid.add_widget(sender_label)
            self.messages_grid.add_widget(content_label)

            window_size = self.get_root_window().size
            if len(self.messages_grid.children) / 2 * self.messages_grid.row_default_height > window_size[1] * 0.9:
                self.scroll_view.scroll_to(content_label, padding=self.messages_grid.row_default_height * 2)

    def send_message(self):
        msg_content = self.message_entry.text
        encoded_message  = f"[SENDER]{username}[SENDER]|[CONTENT]{msg_content}[CONTENT]".encode("utf8")

        s.send(encoded_message)
        print("Sending message:", msg_content)
        self.message_entry.text = ""


class WindowManager(ScreenManager):
    pass


class Beancord(App):
    def build(self):
        wm = WindowManager()
        wm.add_widget(LoginWindow(name='login'))
        wm.add_widget(MainWindow(name='main'))
        wm.current = "login"
        return wm


if __name__ == "__main__":
    Beancord().run()

    try:
        s.send(f"[SENDER]{username}[SENDER]|[QUIT]".encode("utf8"))
    except Exception as e:
        print(e)
    finally:
        s.close()
