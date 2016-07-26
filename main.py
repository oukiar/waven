#!/usr/bin/python
# -*- coding: utf-8 -*-

from kivy.app import App

from waven import Waven

class WavenApp(App):
    def build(self):   
        self.icon = 'icon.png'     
        return Waven()
    
    def on_start(self):
        pass
        
    def on_pause(self):
        return True
        
    def on_resume(self):
        pass
        
    def on_stop(self):
        print("Quiting")


if __name__ == '__main__':
    app = WavenApp()
    app.run()
