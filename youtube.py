
#this import was neccesary when we enable the url downloading (like for xvideos)
from __future__ import unicode_literals

from kivy.clock import Clock

from threading import Thread
import youtube_dl
import os

class YoutubeDownload(Thread):
    
    def __init__(self, **kwargs):
        
        self.url = kwargs.pop('url')
        self.item = kwargs.pop('item')
        self.filename = kwargs.pop('filename')
        self.on_complete = kwargs.pop('on_complete', None)
        self.originaltitle = kwargs.pop('originaltitle', False)

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
        
        dest = self.filename + ".mp4"

        if self.originaltitle:
            #   OPCIONES DESCARGA YOUTUBE
            ydl_opts = {#"format":"18", #comentado desde que se habilito la descarga por url
                "progress_hooks":[self.item.setProgress],
                "no_color": True,
                "nopart": True,
                #"outtmpl": dest,
                "quiet": True
                    }

        else:            
            #   OPCIONES DESCARGA YOUTUBE
            ydl_opts = {"format":"18", #comentado desde que se habilito la descarga por url
                "progress_hooks":[self.item.setProgress],
                "no_color": True,
                "nopart": True,
                "outtmpl": dest,
                "quiet": True
                    }
                        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            filename = ydl.download([self.url])
        
        if self.on_complete != None:
            Clock.schedule_once(self.on_complete, 0)

        