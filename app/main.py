import socket
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

MSG_LENGTH = 2048
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None


class LoginWindow(Screen, FloatLayout):
    username_entry = ObjectProperty(None)
    ip_entry = ObjectProperty(None)
    port_entry = ObjectProperty(None)

    def connect(self):
        global username

        username = self.username_entry.text
        ip_addr = self.ip_entry.text
        port = self.port_entry.text

        if username.strip() == "":
            print("Please give a username!")
            return

        if ip_addr.strip() == "":
            print("Please give an address!")
            return

        if port.strip() == "":
            port = 8000

        print(f"Connecting to {ip_addr} at port {port} as {username}...")

        s.settimeout(10)

        try:
            s.connect((ip_addr, int(port)))
        except socket.gaierror:
            print("Invalid address!")
            return
        except ValueError:
            print("Invalid port!")
            return
        except ConnectionRefusedError:
            print("Server not started!")
            return
        except socket.timeout:
            print("Server took too long to respond!")
            return

        s.send(username.encode("utf8"))
        response = s.recv(MSG_LENGTH).decode("utf8")

        if response == "[DUPLICATE NAME]":
            #TODO: Show this message on a label
            print(f"The username {username} is already taken!")
            return

        if response == "[CONNECTION SUCCESS]":
            print("Connection successfully established!")
            self.manager.current = "main"


class MainWindow(Screen):
    pass


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
