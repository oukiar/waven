
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class SongItem(BoxLayout):
    def do_play(self):
        App.get_running_app().root.do_play(filename=self.song_object.Filename, song=self.song_object)
        
        App.get_running_app().root.show_playing()
        
    def do_playnext(self):
        playnext = App.get_running_app().root.playnext
        playnext.append(self.song_object)
        
        #actualizar cantidad de elementos en cola (elemento visual en playing)
        App.get_running_app().root.queuecounter.text = str(len(playnext))
