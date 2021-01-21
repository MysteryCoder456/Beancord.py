import socket
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class LoginWindow(Screen, FloatLayout):
    username_entry = ObjectProperty(None)
    ip_entry = ObjectProperty(None)
    port_entry = ObjectProperty(None)

    def connect(self):
        username = self.username_entry.text
        ip_addr = self.ip_entry.text
        port = self.port_entry.text

        print(f"Connecting to {ip_addr} at port {port} as {username}...")


class MainWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class Beancord(App):
    def build(self):
        wm.add_widget(LoginWindow(name='login'))
        wm.add_widget(MainWindow(name='main'))
        wm.current = "login"
        return wm


if __name__ == "__main__":
    wm = WindowManager()
    Beancord().run()

    try:
        s.send(b"QUIT")
    except Exception as e:
        print(e)

    s.close()
