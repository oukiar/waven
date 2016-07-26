
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


import cloud

from modaladdplaylist import ModalAddPlaylist

class PlaylistMenu(Popup):
    pass

class PlayListItem(BoxLayout):
    def update_tracklist(self):
        App.get_running_app().root.current_playlist = self.playlist_object
        App.get_running_app().root.update_tracklist()
                
class Playlists(BoxLayout):
    def open_addplaylist(self):
        ModalAddPlaylist(on_dismiss=self.update_view).open()
        
    def update_view(self, w=None):
        
        query = cloud.Query(className="Playlists")
        #query.orderby("Title")
        query.orderby("OrderIndex")
        result = query.find()
        
        self.items.clear()
        
        for i in result:
            #print("Name: " + i.Title)
            
            item = PlayListItem()
            item.title.text = i.Title
            item.playlist_object = i   #the object playlist is stored in the button object as a reference for future operations
            self.items.add_widget(item)
    
    def show_songs(self):
        print("Mostrando canciones")
        
        App.get_running_app().root.screens.current = "songs"
    
