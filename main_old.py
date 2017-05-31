#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.app import App

from kivy.config import Config
Config.set('kivy', 'window_icon', 'icon.png')

try:
    import devslib.cloud as cloud
except:
    import os
    os.system("git clone https://github.com/oukiar/devslib")
    
    import devslib.cloud as cloud
    
from waven import Waven

class WavenApp(App):
    #icon = 'icon.png'
    def build(self):   
        #self.icon = './icon.png'
        return Waven()
    
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
