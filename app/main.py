from kivy.app import App
from kivy.uix.widget import Widget


class MainWidget(Widget):
    pass


class Beancord(App):
    def build(self):
        return MainWidget()


if __name__ == "__main__":
    Beancord().run()