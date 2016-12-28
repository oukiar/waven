
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


from kivy.lang import Builder
Builder.load_file('songs.kv')

import devslib.cloud as cloud

import os

class SongItem(BoxLayout):
    def do_play(self):
        print(self.object_instance.Filename)
        App.get_running_app().root.do_play(filename=self.object_instance.Filename, song=self.object_instance)

class Songs(BoxLayout):
    def update_songs(self):
        
        self.items.clear()
        
        query = cloud.Query(className="Songs")
        
        result = query.find()

        for i in result:
            
            if os.path.isfile(i.Filename):
                
                item = SongItem()
                item.pista.text = i.Title[:60]
                item.object_instance = i
                
                playlist = cloud.create("Playlists", i.Playlist)
                
                if hasattr(playlist, "Title"):
                    item.artista.text = playlist.Title
                else:
                    item.artista.text = "No album"
                    
                item.duracion.text = str(i.Duration)

                self.items.add_widget(item)
