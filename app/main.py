import socket
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ObjectProperty

MSG_LENGTH = 2048
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
username = None


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
