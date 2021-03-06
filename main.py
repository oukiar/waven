
'''
Waven

This is a basic download tool for videos from internet.

Tratamos de mantener la mayor cantidad posible de sitios web soportados.
Por estandar inicial, solo youtube es soportado en forma de buscador
amigable, el resto de sitios son soportados via URL.

Es responsabilidad de los usuarios respetar el contenido de los videos,
en caso de algun problema, pueden bloquear el video reportandolo en el 
siguiente enlace:

http://waven.org/copyright

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


# Monkey patch to ssl certificate verification error
try:
    import ssl
    from functools import wraps

    print(('APPLYING MONKEY PATCH TO FORCE SSL '
          'PROTOCOL V1 [SSL VERSION: {}]'.format(
        ssl.OPENSSL_VERSION)))

    def sslwrap(func):
        @wraps(func)
        def bar(*args, **kw):
            kw['ssl_version'] = ssl.PROTOCOL_TLSv1
            return func(*args, **kw)
        return bar

    # This line below is to avoid error (detected in python-2.7.12 in linux platform):
    # URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590)>
    # NOTE: This error causes that the tvshow's poster not to be shown/download when trying to load with kivy loader
    ssl._create_default_https_context = ssl._create_unverified_context

    ssl.wrap_socket = sslwrap(ssl.wrap_socket)
except Exception as e:
    print(('ERROR ON MONKEY PATCH SSL PROTOCOL V1: {}'.format(e)))

'''
#YOUTUBE DOWNLOAD TEST
import youtube_dl

dest =  "videodesc.mp4"
    
#   OPCIONES DESCARGA YOUTUBE
ydl_opts = {"format":"18", #comentado desde que se habilito la descarga por url, debido a que original title se usa cuando se descarga por URL
#ydl_opts = {"format":"171", #comentado desde que se habilito la descarga por url, debido a que original title se usa cuando se descarga por URL
    #"progress_hooks":[self.item.setProgress],
    "no_color": True,
    "nopart": True,
    "outtmpl": dest,
    "quiet": True
    }
                
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    filename = ydl.download(["https://www.youtube.com/watch?v=aPcnL9U-yjQ"])
'''
    
import kivy
print("KIVYPATH", kivy.__path__)


from kivy.uix.relativelayout import RelativeLayout 
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.button import Button 
from kivy.uix.popup import Popup 
from kivy.uix.video import Video
from kivy.clock import Clock

from kivy.app import App

from kivy.core.audio import SoundLoader

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
from playlists import Playlists, PlaylistMenu, PlaylistSongs, PlaylistSongItem
from modalsearch import ModalSearch, ModalDownloads
from songs import SongItem, Songs
from search import Search

class Waven(RelativeLayout):
    

    def __init__(self, **kwargs):
        
        #self.bgcolor = (.2109375, .23828125, .27734375, 1)
        
        #configuracion general de color
        self.set_background_color("#111719")
        self.set_foreground_color("#444444") #in progress
        
        super(Waven, self).__init__(**kwargs)
        
        print("Despues de super")
        
        self.current_playlist = None
        
        self.playnext = []

        cloud.init(database="playlists.db", 
                    server="107.170.209.26", 
                    serverport=1235, 
                    localport=1236)


        self.modalsearch = ModalSearch()
        self.modaldownloads = ModalDownloads()
        
        
        if platform == 'android':
            self.downloadpath = "/mnt/sdcard/ACTUALIZACION/Descargas"
            
            if not os.path.exists("/mnt/sdcard/ACTUALIZACION"):
                os.mkdir("/mnt/sdcard/ACTUALIZACION")
                
                if not os.path.exists("/mnt/sdcard/ACTUALIZACION/Descargas"):
                    os.mkdir("/mnt/sdcard/ACTUALIZACION/Descargas")
                
            
        elif platform == 'linux' or platform == 'win' or platform == 'macosx':
            self.downloadpath = "downloads"
            
        Clock.schedule_once(self.initialization, 0)

        return
        
        #cargar configuracion
        try:
            self.configuration = json.loads(open("configuration.json").read())
        except:
            #default configuration
            self.configuration = {"paths":["data_repository"]}
            #save configuration
            open("configuration.json", "w+").write(json.dumps(self.configuration) )
            
    def initialization(self, dt):
        
        self.playlists.update_view()
        self.songs.update_songs()
            
    def set_background_color(self, color):
        '''
        color debe venir en formato HTML de la forma #RRGGBB
        '''
        print("Color de fondo: " + color)
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        #print(r,g,b)
        
        self.bgcolor = (r/255.0, g/255.0, b/255.0, 1)
        self.bgplaying = (r/255.0, g/255.0, b/255.0, 1)
        
        #print self.bgcolor
        
    def set_foreground_color(self, color):
        '''
        color debe venir en formato HTML de la forma #RRGGBB
        '''
        print("Color de frente: " + color)
        
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        #print(r,g,b)
        
        self.fgcolor = (r/255.0, g/255.0, b/255.0, 1)
       
    def do_fullscreen(self):
        
        if self.maingui in self.layout.children:
            
            print("Going to fullscreen")
            
            self.playing.remove_widget(self.videolayout)
            self.layout.remove_widget(self.maingui)
            
            
            self.layout.add_widget(self.videolayout)
        else:
            
            print("Releasing fullscreen")
            
            self.layout.remove_widget(self.videolayout)
            self.layout.add_widget(self.maingui)
            
            
            self.playing.add_widget(self.videolayout, index=4)
        
    def update_fs(self, texture):
        #self.videofullscreen.texture = texture
        pass
            
    def show_maximize(self):
        self.btn_maximize.opacity = 1
        self.ids.lay_controls.opacity = 1
        Clock.unschedule(self.hide_maximize)
        Clock.schedule_once(self.hide_maximize, 3)
        
    def hide_maximize(self, dt):
        self.btn_maximize.opacity = 0
        self.ids.lay_controls.opacity = 0
            
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
                        print("Reproduciendo", song)
                    else:
                        print("End of playlist")
                        
                        #start playing the next playlist
                        query = cloud.Query(className="Playlists")
                        
                        if self.current_playlist != None:
                            query.greaterThan("OrderIndex", self.current_playlist.OrderIndex)
                        else:
                            pass
                            #query.greaterThan("OrderIndex", self.current_playlist.OrderIndex)
                            
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
                for i in self.playlistsongs.items.layout.children:
                    print(i.title.text)
                '''
            
            if song != None:
                #execute on the next video frame (because we are on the state function, we dont want recursive propierties assignement)
                Clock.schedule_once(partial(self.do_play, filename=song.Filename, song=song), 0)

        #actualizar elementos en cola
        self.queuecounter.text = str(len(self.playnext))
                
    def do_play(self, dt=None, **kwargs):
        
        #remove old video widget (for fix any problem between plays)
        #self.remove_widget(self.video)
        
        #self.video = WavenVideo()
        #self.ids.videolayout.add_widget(self.video, 0)
        
        filename = kwargs.get("filename")
        
        self.last_played = kwargs.get("song", None)
    
        if not os.path.exists(filename):
            print('Does not exists')
            return
        
        print("Playing: " + filename)
        
        #update playing widget
        self.txt_playing.text = self.last_played.Title
        
                
        self.circle.state = "rotating"
         
        name, ext = os.path.splitext(filename)
                 
        try:
            if ext.lower() in [".mp4"]:
                self.video.source = filename.encode('utf8')
                self.video.state = "play"
            else:
                self.audio = SoundLoader.load(filename.encode('utf8'))
                self.audio.bind(on_stop=self.stop_sound)
                self.audio.play()
                Clock.schedule_interval(self.update_time_sound, .2)
        except:
            if ext.lower() in [".mp4"]:
                self.video.source = filename
                self.video.state = "play"
            else:
                self.audio = SoundLoader.load(filename)
                self.audio.bind(on_stop=self.stop_sound)
                self.audio.play()
                Clock.schedule_interval(self.update_time_sound, .2)
        
        
    def update_time_sound(self, dt):
        pos = self.audio.get_pos()
        #print("TIME: " + str(pos))
        self.update_time(self.audio.length - pos)
        
    def stop_sound(self, w):
        Clock.unschedule(self.update_time_sound)
        
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
        if self.video.state == "play":
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
        
    def show_search(self):
        App.get_running_app().root.screens.transition.direction = "left"
        App.get_running_app().root.screens.current = "search"
        
    def show_songs(self, direction="left"):
        
        self.screens.transition.direction = direction
        self.screens.current = "songs"
        
    def show_playlistsongs(self, direction="left"):
        
        self.screens.transition.direction = direction
        self.screens.current = "playlistsongs"
        
    def update_tracklist(self):
        
        #update songs of this playlist
        query = cloud.Query(className="Songs")
        query.equalTo("Playlist", self.current_playlist.objectId)
        query.orderby("OrderIndex")
        result = query.find()
        
        
        self.playlistsongs.items.clear()
        
        for i in result:
            item = PlaylistSongItem()
            item.title.text = i.Title
            item.song_id = i.objectId
            item.song_object = i
            self.playlistsongs.items.add_widget(item)
            
        #title of the playlist at the top of songs
        self.playlistsongs.playlisttitle.text = self.current_playlist.Title
            
        #show songs screen
        self.show_playlistsongs()
        
    def set_volume(self, vol):
        #print(vol)
        
        if self.video.state == "play":
            self.video.volume = vol

class WavenVideo(Video):
    pass

class WavenApp(App):
    #icon = 'icon.png'
    def build(self):   
        #self.icon = './icon.png'
        
        return Waven()
        
        #self.video = Video(source="video1.mp4")
        
        self.but = Button(text="stop")
        self.but.bind(on_release=self.nextsong)
        
        self.but2 = Button(text="play 2")
        self.but2.bind(on_release=self.play2)
        
        self.but3 = Button(text="play 3")
        self.but3.bind(on_release=self.play3)
        
        self.lay = BoxLayout(orientation='vertical')
        
        #self.lay.add_widget(self.video)
        self.lay.add_widget(self.but)
        self.lay.add_widget(self.but2)
        self.lay.add_widget(self.but3)
        
        return self.lay
        
        
        
        
    def nextsong(self, w):
        print (w)
        
        
        
        self.lay.remove_widget(self.video)
        
        self.video.state = 'stop'
        del self.video
        
    def play2(self, w):
        
        
        from ffpyplayer.player import MediaPlayer
        
        count = 0
        print("Antes de media player")
        player = MediaPlayer("video1.mp4")
        print("Despues de media player")
        val = ''
        while val != 'eof':
            frame, val = player.get_frame()
            print (frame, count)
            if val != 'eof' and frame is not None:
                img, t = frame
                # display img
                print (img)

            if count == 300:
                break
                
            count += 1

        count = 0
        
        #del player
        
        Clock.schedule_once(self.playX, 1)
        
    def playX(self, dt):
        
        from ffpyplayer.player import MediaPlayer
        
        count =0
        
        player = MediaPlayer("video2.mp4")
        val = ''
        while val != 'eof':
            frame, val = player.get_frame()
            if val != 'eof' and frame is not None:
                img, t = frame
                # display img
                print (img)


            if count == 300:
                break
                
            count += 1
               
        print("Termina reporoduccion")
                
        return
        
        self.video = Video(source="video1.mp4")
    
        self.lay.add_widget(self.video)
        
    def play3(self, w):
        self.video.state = 'play'
    
    def on_start(self):
        pass
        
    def on_pause(self):
        return True
        
    def on_resume(self):
        pass
        
    def on_stop(self):
        print("Quiting")
        cloud.quit()

if __name__ == '__main__':
    app = WavenApp()
    app.run()

