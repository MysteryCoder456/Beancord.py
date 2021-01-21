import socket
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class LoginScreen(Widget):
    username_entry = ObjectProperty(None)
    ip_entry = ObjectProperty(None)
    port_entry = ObjectProperty(None)


class Beancord(App):
    def build(self):
        return LoginScreen()


if __name__ == "__main__":
    Beancord().run()

    try:
        s.send(b"QUIT")
    except Exception as e:
        print(e)

    s.close()
