import kivy
kivy.require('1.0.7')
from kivy.app import App
from kivy.uix.scatter import Scatter
from kivy.uix.gridlayout import GridLayout

class ScatterTextWidget(GridLayout):
	pass 
	
#el nombre de la app esta por decidir.
class NameApp(App):
	def build(self):
		return ScatterTextWidget()

if __name__ == "__main__":
	NameApp().run()