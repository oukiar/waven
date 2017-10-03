
from kivy.app import App
from kivy.uix.popup import Popup

import devslib.cloud as cloud

class ModalAddPlaylist(Popup):
    def create_playlist(self):
        playlist = cloud.create("Playlists")
        
        playlist.Title = self.txt_title.text.capitalize()
        playlist.Year = 2016
        playlist.OrderIndex = cloud.get_max(className="Playlists", field="OrderIndex") + 1
        
        if playlist.save():
            self.dismiss()
            
            #set this playlist as current selected
            App.get_running_app().root.current_playlist = playlist
            
            print("Created playlist: " + playlist.objectId)

        else:
            print("Error al guardar")
