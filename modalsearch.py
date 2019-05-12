

from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from kivy.clock import Clock

from functools import partial

#for search directly on youtube.com
from pitube import YoutubeList

#for download from youtube with thread and callback
from youtube import YoutubeDownload


import os

from devslib.utils import RotativeImage

import devslib.cloud as cloud


class ResultItem(BoxLayout):
    def do_download(self):

        print("Antes de primer downloading")
        title = self.title.text # .encode('ascii', 'replace').replace("?", "").replace(":", "")
        print("Downloading " + title )
    
        #remove download button
        self.layout_download.remove_widget(self.btn_download)
        
        #downloading image
        self.img_loading = RotativeImage(source="images/loading.png", size_hint_x=None)
        self.img_loading.state = "rotating"
        self.layout_download.add_widget(self.img_loading)
        
        if not os.path.isdir(App.get_running_app().root.downloadpath):
            os.mkdir(App.get_running_app().root.downloadpath)
            
        #sys.stderr = stderr_backup
        YoutubeDownload(item=self, 
                            url=self.url, 
                            filename=title , 
                            on_complete=self.on_complete, 
                            quality=self.modal.ids.quality.text,
                            downloadpath=os.path.join(App.get_running_app().root.downloadpath, self.playlist.Title) )
        
        
        
    def on_complete(self, dt):
        #self.btn_download.source = "images/saved.png"
        print("Descarga completa")
        
        self.progress.value = 100
        
        #remove loading icon
        self.layout_download.remove_widget(self.img_loading)
        
        #add play button
        self.btn_play = Button(text="Play",  size_hint_x=None, background_color=(0,1,0,1), on_release=self.do_play )
        self.layout_download.add_widget(self.btn_play)
        
        #almacenar en la base de datos
        song = cloud.create(className="Songs")
        
        song.Title = self.title.text #.encode('utf8')
        song.Duration = 185 #in seconds
        song.Filename = self.filename
        song.URL = self.url

        #link to the playlist ... like a pointer in parse
        song.Playlist = self.playlist.objectId #App.get_running_app().root.current_playlist.objectId
        
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
            
            self.song_object = song
            
            '''
            try:
                print("Almacenado en la BD: " + song.Title )
            except:
                print("Almacenado en la BD: " + song.Title.encode('utf8') )
            '''
            
            print("--- Playlist: " + str(song.Playlist))
            print("--- OrderIndex: " + str(song.OrderIndex) )
            
            #renombrar archivo recien descargado a nombre de objectId?
            #tomar mucho esto en cuenta, pues puede haber problemas con archivos con el mismo nombre
            
        else:
            print("Error al guardar")
            
    def do_play(self, w):
        App.get_running_app().root.modalsearch.dismiss()
        App.get_running_app().root.do_play(filename=self.song_object.Filename, song=self.song_object)
        App.get_running_app().root.show_playing()
        
    def setProgress(self, val):
        Clock.schedule_once( partial(self.real_setProgress, val) , 0)
        
    def real_setProgress(self, val, dt=None):
        #print val
        if "_percent_str" in val:
            
            percent = float(val["_percent_str"][:-1])
            
            self.progress.value = percent
            
            #print("percent: ", percent)
            
        
        if "filename" in val:
            self.filename = val["filename"]
        
class ModalDownloadByURL(Popup):
    def do_download(self):
        print("Downloading by URL: " + self.txt_url.text)
        
        item = DownloadItem()
        item.title.text = "Waiting download video title"
        item.url = self.txt_url.text
        item.playlist = App.get_running_app().root.current_playlist
        #item.modal = self
        
        App.get_running_app().root.modaldownloads.layout.add_widget(item)
        
        #start the download
        YoutubeDownload(item=item, 
                            url=item.url, 
                            filename=item.title.text, 
                            on_complete=item.on_complete, 
                            originaltitle=True, 
                            quality=self.ids.quality.text
                            )
       
        self.dismiss()
        App.get_running_app().root.modaldownloads.open()
        
       
class DownloadItem(BoxLayout):
    def on_complete(self, dt):
        print("Download complete")
        
        
        self.progress.value = 100
        
        #remove loading icon
        self.layout_download.remove_widget(self.img_downloading)
        
        #add play button
        self.btn_play = Button(text="Play",  size_hint_x=None, background_color=(0,1,0,1), on_release=self.do_play )
        self.layout_download.add_widget(self.btn_play)
        
        #almacenar en la base de datos
        song = cloud.create(className="Songs")
        
        song.Title = os.path.splitext(os.path.basename(self.filename))[0]
        song.Duration = 185 #in seconds
        song.Filename = self.filename
        song.URL = self.url

        #link to the playlist ... like a pointer in parse
        song.Playlist = self.playlist.objectId #App.get_running_app().root.current_playlist.objectId
        
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
            
            self.song_object = song
            
            print("Almacenado en la BD: " + song.Title)
            print("--- Playlist: " + song.Playlist)
            print("--- OrderIndex: " + str(song.OrderIndex) )
            
            #renombrar archivo recien descargado a nombre de objectId?
            #tomar mucho esto en cuenta, pues puede haber problemas con archivos con el mismo nombre
            
        else:
            print("Error al guardar")
        
    def setProgress(self, val):
        Clock.schedule_once( partial(self.real_setProgress, val) , 0)
        
    def real_setProgress(self, val, dt=None):
        print (val)
        if "_percent_str" in val:
            
            try:
                percent = float(val["_percent_str"][:-1])
            except:
                percent = 0.0
            
            self.progress.value = percent
            
            #print("percent: ", percent)
            
        
        if "filename" in val:
            self.filename = val["filename"]
            
            self.title.text = os.path.splitext(os.path.basename(self.filename))[0]
            
    def do_play(self, w):
        
        #close the url modal
        #self.modal.dismiss()
        
        App.get_running_app().root.modaldownloads.dismiss()
        
        App.get_running_app().root.modalsearch.dismiss()
        App.get_running_app().root.do_play(filename=self.song_object.Filename, song=self.song_object)
        App.get_running_app().root.show_playing()
        
        
class ModalDownloads(Popup):
    pass
        
class ModalSearch(Popup):
    def on_open(self):
        #if self.searchtext.text != "":
        print("Abriendo modal de busqueda")
        
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
            item.title.text = i.name.replace('/', '')
            item.url = i.url
            item.playlist = App.get_running_app().root.current_playlist
            item.filename = i.name + ".mp4"
            item.modal = self
            
            '''
            if "http" not in i.thumbnail:
                i.thumbnail = "http:" + i.thumbnail
            
            item.preview.source = i.thumbnail
            '''
            
            #print("THUMBNAIL: ", i.thumbnail)
            
            self.layout.add_widget(item)
            
    def on_dismiss(self):
        print("Actualizando lista de canciones")
        #FIXIT
        App.get_running_app().root.update_tracklist()
        
    def show_formats(self):
        print("Formats: ")
        
    def open_downloadbyURL(self):
        ModalDownloadByURL().open()
        
