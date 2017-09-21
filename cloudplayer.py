from kivy.app import App
from kivy.uix.floatlayout import FloatLayout


class CloudPlayer(FloatLayout):
    pass

if __name__ == "__main__":
    class CloudPlayerApp(App):
        def build(self):
            return CloudPlayer()

    CloudPlayerApp().run()
