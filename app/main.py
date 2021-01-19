from kivy.app import App
from kivy.uix.label import Label


class Beancord(App):
    def build(self):
        return Label(text="hi")


if __name__ == "__main__":
    Beancord().run()