
from kivy.uix.relativelayout import RelativeLayout 
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.button import Button 
from kivy.uix.popup import Popup 
from kivy.clock import Clock

from kivy.app import App

import os
import json
import cloud

from functools import partial
from threading import Thread

#for search directly on youtube.com
from pitube import YoutubeList

#for download with youtube-dl
import youtube_dl

import sys

#stderr_backup = sys.stderr

try:
    from devslib.utils import RotativeImage
except:
    os.system("git clone https://github.com/oukiar/devslib")
    from devslib.utils import RotativeImage


class Desktop(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(Desktop, self).__init__(**kwargs)
        
        self.current_playlist = None
        
        self.playnext = []

        cloud.init("playlists.db")

        self.playlists.update_view()

        self.modalsearch = ModalSearch()
        

        return
        
        #cargar configuracion
        try:
            self.configuration = json.loads(open("configuration.json").read())
        except:
            #default configuration
            self.configuration = {"paths":["data_repository"]}
            #save configuration
            open("configuration.json", "w+").write(json.dumps(self.configuration) )
            
    def add_songs(self):
        
        #clean previous result
        self.modalsearch.layout.clear()
        
        #add the loading-working-searching icon?
        
        
        #open form for search
        self.modalsearch.open()
        
    def on_video_state(self, state):
        #print(state)
        
        if state == "stop":
            song = None
            #play next?
            if len(self.playnext):
                songfile = self.playnext[0]
            else:
                
                if self.last_played != None:
                
                    #get all songs of this playlist
                    query = cloud.Query(className="Songs")
                    
                    query.equalTo("Playlist", self.last_played.Playlist)
                    query.greaterThan("OrderIndex", self.last_played.OrderIndex)
                    
                    #query.orderby("Title")
                    query.orderby("OrderIndex")
                    
                    result = query.find()
                    print(result)
                    if len(result):
                        song = result[0]
                    else:
                        print("End of playlist")
                else:
                    print("No last played?")
                    self.circle.state = "stopped"
                
                '''
                for i in self.songs.layout.children:
                    print(i.title.text)
                '''
            
            if song != None:
                #execute on the next video frame (because we are on the state function, we dont want recursive propierties assignement)
                Clock.schedule_once(partial(self.do_play, filename=song.Filename, song=song), 0)

                
    def do_play(self, dt=None, **kwargs):
        
        filename = kwargs.get("filename")
        
        self.last_played = kwargs.get("song", None)
        
        print("Playing: " + filename)
        
        #update playing widget
        self.txt_playing.text = self.last_played.Title
                
        self.circle.state = "rotating"
                
        try:
            self.video.source = filename.encode('utf8')
        except:
            self.video.source = filename
        
        self.video.state = "play"
        
    def playpause(self, img):
        print("Play pause: " + img.source)
        
        if img.source == "images/circlepause.png":
            self.video.state = "pause"
            img.source = "images/circleplay.png"
            self.circle.state = "stopped"
        else:
            self.video.state = "play"
            img.source = "images/circlepause.png"
            self.circle.state = "rotating"
       
class SongItem(BoxLayout):
    def do_play(self):
        App.get_running_app().root.do_play(filename=self.song_object.Filename, song=self.song_object)
        
    def do_playnext(self):
        playnext = App.get_running_app().root.playnext

        playnext.append(self.song_object.Filename)

class ResultItem(BoxLayout):
    def do_download(self):
        print("Downloading " + self.title.text)
        
        #remove download button
        self.layout_download.remove_widget(self.btn_download)
        
        #downloading image
        self.img_loading = RotativeImage(source="images/loading.png", size_hint_x=None)
        self.img_loading.state = "rotating"
        self.layout_download.add_widget(self.img_loading)
        
        #sys.stderr = stderr_backup
        YoutubeDownload(item=self, url=self.url, filename=self.title.text, on_complete=self.on_complete)
        
        
    def on_complete(self, dt):
        #self.btn_download.source = "images/saved.png"
        print("Descarga completa")
        
        self.progress.value = 100
        
        #remove loading icon
        self.layout_download.remove_widget(self.img_loading)
        
        #add play button
        self.btn_play = Button(text="Play",  size_hint_x=None, background_color=(0,1,0,1))
        self.layout_download.add_widget(self.btn_play)
        
        #almacenar en la base de datos
        song = cloud.create("Songs")
        
        song.Title = self.title.text
        song.Duration = 185 #in seconds
        song.Filename = self.filename

        #link to the playlist ... like a pointer in parse
        song.Playlist = App.get_running_app().root.current_playlist.objectId
        
        #song.OrderIndex = cloud.get_max("Songs", "OrderIndex") + 1
                
        #get the next index for this playlist
        query = cloud.Query(className="Songs")
        query.equalTo("Playlist", song.Playlist)
        query.orderby("OrderIndex", order="DESC")
        res = query.find()

        if len(res):
            song.OrderIndex = getattr(res[0], "OrderIndex") + 1
        else:
            song.OrderIndex = 1
        
        if song.save():
            print("Almacenado en la BD: " + song.Title)
            print("--- Playlist: " + song.Playlist)
            print("--- OrderIndex: " + str(song.OrderIndex) )
            
            #renombrar archivo recien descargado a nombre de objectId?
            
        else:
            print("Error al guardar")

    def setProgress(self, val):
        #print val
        if "_percent_str" in val:
            
            percent = float(val["_percent_str"][:-1])
            
            self.progress.value = percent
            
            print("percent: ", percent)
            
        
        if "filename" in val:
            self.filename = val["filename"]
        
class ModalSearch(Popup):
        
    def on_search(self):
        print("Searching: " + self.searchtext.text)
        
        self.layout.clear()
        
        #search using callback
        search = YoutubeList(searchtext=self.searchtext.text.encode('utf8'), callback=partial(self.res_search, ) )
        #search = YoutubeList(searchtext=self.searchtext.text, callback=partial(self.res_search, ) )
        
        #add loading widget
        img = RotativeImage(source="images/loading.png")
              
        img.state = "rotating"
              
        self.layout.add_widget(img)
        
    def res_search(self, result):
        #print(result)
        
        #clean working-loading widget
        self.layout.clear()
        
        for i in result:
            #print(i.name)
            
            item = ResultItem()
            item.title.text = i.name
            item.url = i.url
            
            self.layout.add_widget(item)
            
    def on_dismiss(self):
        print("Actualizando lista de canciones")
        #FIXIT
        App.get_running_app().root.playlists.update_view()
        
    def show_formats(self):
        print("Formats: ")
        
class PlayListItem(BoxLayout):
    def update_tracklist(self):
        App.get_running_app().root.current_playlist = self.playlist_object
        
        #update songs of this playlist
        query = cloud.Query(className="Songs")
        query.equalTo("Playlist", self.playlist_object.objectId)
        #query.orderby("Title")
        query.orderby("OrderIndex")
        result = query.find()
        
        
        App.get_running_app().root.songs.clear()
        
        for i in result:
            item = SongItem()
            item.title.text = i.Title
            item.song_id = i.objectId
            item.song_object = i
            App.get_running_app().root.songs.add_widget(item)
        
class Playlists(BoxLayout):
    def open_addplaylist(self):
        DlgAddPlaylist(on_dismiss=self.update_view).open()
        
    def update_view(self, w=None):
        
        query = cloud.Query(className="Playlists")
        query.orderby("Title")
        result = query.find()
        
        self.items.clear()
        
        for i in result:
            #print("Name: " + i.Title)
            
            item = PlayListItem()
            item.title.text = i.Title
            item.playlist_object = i   #the object playlist is stored in the button object as a reference for future operations
            self.items.add_widget(item)
    
class DlgAddPlaylist(Popup):
    def create_playlist(self):
        playlist = cloud.create("Playlists")
        
        playlist.Title = self.txt_title.text.capitalize()
        playlist.Year = 2016
        playlist.OrderIndex = 0
        
        if playlist.save():
            self.dismiss()
            
            #set this playlist as current selected
            App.get_running_app().root.current_playlist = playlist
            
            print("Created playlist: " + playlist.objectId)

        else:
            print("Error al guardar")
            
        

class YoutubeDownload(Thread):
    
    def __init__(self, **kwargs):
        
        self.url = kwargs.pop('url')
        self.item = kwargs.pop('item')
        self.filename = kwargs.pop('filename')
        self.on_complete = kwargs.pop('on_complete', None)

        Thread.__init__(self)
        
        self.start()
        
    def run(self):
        '''
        #DESTINO
        if platform == "android":
            dest = os.path.join(app.root.repertory, app.root.currentgenre, app.root.currentalbum, self.filename + ".mp3")

            #   OPCIONES DESCARGA YOUTUBE
            ydl_opts = {"format":"171",
                "progress_hooks":[self.item.setProgress],
                "no_color": True,
                "nopart": True,
                "outtmpl": dest,
                "quiet": True
                    }
        else:
            dest = os.path.join(app.root.repertory, app.root.currentgenre, app.root.currentalbum, self.filename + ".mp4")

            #   OPCIONES DESCARGA YOUTUBE
            ydl_opts = {"format":"18",
                "progress_hooks":[self.item.setProgress],
                "no_color": True,
                "nopart": True,
                "outtmpl": dest,
                "quiet": True
                    }
        '''
        
        '''
        if app.root.formatdownload == "171":
            dest = os.path.join(app.root.repertory, app.root.currentgenre, app.root.currentalbum, self.filename + ".mp3")
        else:
            dest = os.path.join(app.root.repertory, app.root.currentgenre, app.root.currentalbum, self.filename + ".mp4")
        '''
        
        dest = os.path.join("downloads", self.filename + ".mp3")

        #   OPCIONES DESCARGA YOUTUBE
        ydl_opts = {"format":"171",
            "progress_hooks":[self.item.setProgress],
            "no_color": True,
            "nopart": True,
            "outtmpl": dest,
            "quiet": True
                }
                    
                        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])
        
        if self.on_complete != None:
            Clock.schedule_once(self.on_complete, 0)

        
