
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup


import devslib.cloud as cloud

import os

from modaladdplaylist import ModalAddPlaylist

class ModalPlaylistEdit(Popup):
    def do_save(self):
        print("Rename to " + self.txt_newname.text)
        
        App.get_running_app().root.current_playlist.Title = self.txt_newname.text
        App.get_running_app().root.current_playlist.save()

class PlaylistMenu(Popup):
    def do_delete(self):
        print("Deleting playlist: " + App.get_running_app().root.current_playlist.Title)
        
        #TODO: pedir confirmacion
        
        #delete files
        query = cloud.Query(className="Songs")
        query.equalTo("Playlist", App.get_running_app().root.current_playlist.objectId)
        result = query.find()
        
        for i in result:
            print (i.Filename)
            os.remove(i.Filename)
        
        #delete
        App.get_running_app().root.current_playlist.delete()
        
        self.dismiss()
        
        App.get_running_app().root.playlists.update_view()
        App.get_running_app().root.show_playlists()
        
        
    def do_rename(self):
        ModalPlaylistEdit().open()

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
        
    def show_menu(self):
        print (self.items.scroll_distance)
        print (self.items.scroll_timeout)
    
