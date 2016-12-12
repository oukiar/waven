
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


from kivy.lang import Builder
Builder.load_file('songs.kv')

import devslib.cloud as cloud

class SongItem(BoxLayout):
    pass

class Songs(BoxLayout):
    def update_songs(self):
        
        self.items.clear()
        
        query = cloud.Query(className="Songs")
        
        result = query.find()

        for i in result:
            item = SongItem()
            item.pista.text = i.Title[:60]
            
            playlist = cloud.create("Playlists", i.Playlist)
            
            if hasattr(playlist, "Title"):
                item.artista.text = playlist.Title
            else:
                item.artista.text = "ERROR"
                
            item.duracion.text = str(i.Duration)

            self.items.add_widget(item)
