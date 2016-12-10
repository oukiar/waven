
from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder
Builder.load_file('search.kv')

class Search(BoxLayout):
    def on_search(self):
        print("Searching keywords: " + self.searchtext.text)
        
        
        
        
