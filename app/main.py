import socket
from kivy.app import App
from kivy.uix.widget import Widget

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(("127.0.0.1", 8000))
# s.send(b"CodeBean")
# s.send(b"[SENDER]CodeBean[SENDER]|[CONTENT]wassup[CONTENT]")


class MainWidget(Widget):
    pass


class Beancord(App):
    def build(self):
        return MainWidget()


if __name__ == "__main__":
    Beancord().run()
    # s.send(b"QUIT")
    # s.close()
