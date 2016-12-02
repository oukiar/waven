
'''
Waven

This is a basic download tool for videos from internet.

Tratamos de mantener la mayor cantidad posible de sitios web soportados.
Por estandar inicial, solo youtube es soportado en forma de buscador
amigable, el resto de sitios son soportados via URL.

Es responsabilidad de los usuarios respetar el contenido de los videos,
en caso de algun problema, pueden bloquear el video reportandolo en el 
siguiente enlace:

http://natorg.net/waven/copyright

Usted es responsable de lo que descarga, waven no tiene ni tendra jamas
control de contenido a menos de que sea previamente reportado en la liga
mencionada anteiormente.

En caso de disputa sobre bloqueo de algun contenido de descarga, pueden
comunicarse a admin@wavenapp.com

Esta herramienta de backup es nuestra unica salvacion para evitar el
online-jail, we love p2p free cloud communications !

Otro de los objetivos de waven es servir como base para mas herramientas
relativas al video, edicion, publicacion y sharing.

Why waven?

Es odioso tener que estar online para ver los videos que consideres deban
estar en tu biblioteca.

'''

from kivy.uix.relativelayout import RelativeLayout 
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.button import Button 
from kivy.uix.popup import Popup 
from kivy.clock import Clock

from kivy.app import App

from kivy.utils import platform

import os
import time
import json

try:
    import devslib.cloud as cloud
except:
    os.system("git clone https://github.com/oukiar/devslib")
    
    import devslib.cloud as cloud



from functools import partial

import sys

#project imports
from playlists import Playlists, PlaylistMenu
from modalsearch import ModalSearch, ModalDownloads
from song import SongItem

class Waven(RelativeLayout):

    def __init__(self, **kwargs):
        super(Waven, self).__init__(**kwargs)
        
        self.current_playlist = None
        
        self.playnext = []

        cloud.init("playlists.db")

        self.playlists.update_view()

        self.modalsearch = ModalSearch()
        self.modaldownloads = ModalDownloads()
        
        if platform == 'android':
            self.downloadpath = "/mnt/sdcard/ACTUALIZACION/Descargas"
        elif platform == 'linux' or platform == 'win' or platform == 'macosx':
            self.downloadpath = "downloads"

        return
        
        #cargar configuracion
        try:
            self.configuration = json.loads(open("configuration.json").read())
        except:
            #default configuration
            self.configuration = {"paths":["data_repository"]}
            #save configuration
            open("configuration.json", "w+").write(json.dumps(self.configuration) )
            
    def show_maximize(self):
        self.btn_maximize.opacity = 1
        Clock.unschedule(self.hide_maximize)
        Clock.schedule_once(self.hide_maximize, 3)
        
    def hide_maximize(self, dt):
        self.btn_maximize.opacity = 0
            
    def show_playlist_menu(self):
        PlaylistMenu().open()
            
    def add_songs(self):
        
        #clean previous result
        #self.modalsearch.layout.clear()
        
        self.modalsearch.searchtext.text = self.current_playlist.Title
        
        #add the loading-working-searching icon?
        
        
        #open form for search
        self.modalsearch.open()
        
    def on_video_state(self, state):
        #print(state)
        
        if state == "stop":
            song = None
            #play next?
            if len(self.playnext):
                song = self.playnext.pop(0)
            else:
                
                if self.last_played != None:
                
                    #get all songs of this playlist
                    query = cloud.Query(className="Songs")
                    
                    query.equalTo("Playlist", self.last_played.Playlist)
                    query.greaterThan("OrderIndex", self.last_played.OrderIndex)
                    
                    #query.orderby("Title")
                    query.orderby("OrderIndex")
                    
                    result = query.find()
                    #print(result)
                    if len(result):
                        song = result[0]
                    else:
                        print("End of playlist")
                        
                        #start playing the next playlist
                        query = cloud.Query(className="Playlists")
                        query.greaterThan("OrderIndex", self.current_playlist.OrderIndex)
                        
                        query.orderby("OrderIndex")
                        
                        result = query.find()
                        
                        if len(result):
                            print(result[0].Title)
                            
                            #get the first song of this playlist
                            query = cloud.Query(className="Songs")
                            
                            query.equalTo("Playlist", result[0].objectId)
                            query.greaterThan("OrderIndex", 0)
                            
                            #query.orderby("Title")
                            query.orderby("OrderIndex")
                            
                            result = query.find()
                            print(result)
                            if len(result):
                                print(result[0].Filename)
                                song = result[0]
                            
                        else:
                            print("End of content")
                            self.circle.state = "stopped"
                        
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

        #actualizar elementos en cola
        self.queuecounter.text = str(len(self.playnext))
                
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
        
    def on_videoloaded(self):
        self.update_time(0)
        
        
    def update_time(self, val):
        #print val
        self.durationcounter.text = time.strftime("%M:%S", time.gmtime(self.video.duration - val))
        
        #set the max value for the progressbar of video position ... FIXME: esto solo debe hacerse en el on_loaded del video, pero no funcionaba daba 1.0
        if self.videoprogress.max != self.video.duration:
            self.videoprogress.max = self.video.duration
        
        self.videoprogress.value = val
        
    def seek_playing(self, val):
        #print (val, self.video.position)
        #self.video.position = val
        
        #saltos solo mayores a 2 segundos
        if (self.video.position - val) < -2 or (self.video.position - val) > 2:
            self.video.seek(val / self.video.duration)
        
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
       
    def show_playlists(self):
        App.get_running_app().root.screens.transition.direction = "right"
        App.get_running_app().root.screens.current = "playlists"
    
    def show_playing(self):
        App.get_running_app().root.screens.transition.direction = "left"
        App.get_running_app().root.screens.current = "playing"
        
    def show_songs(self, direction="left"):
        
        self.screens.transition.direction = direction
        self.screens.current = "songs"
        
    def update_tracklist(self):
        
        #update songs of this playlist
        query = cloud.Query(className="Songs")
        query.equalTo("Playlist", self.current_playlist.objectId)
        query.orderby("OrderIndex")
        result = query.find()
        
        
        self.songs.clear()
        
        for i in result:
            item = SongItem()
            item.title.text = i.Title
            item.song_id = i.objectId
            item.song_object = i
            self.songs.add_widget(item)
            
        #title of the playlist at the top of songs
        self.playlisttitle.text = self.current_playlist.Title
            
        #show songs screen
        self.show_songs()
        
    def set_volume(self, vol):
        #print(vol)
        
        if self.video.state == "play":
            self.video.volume = vol
