
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


from kivy.lang import Builder
Builder.load_file('songs.kv')

class SongItem(BoxLayout):
    pass

class Songs(BoxLayout):
    pass
