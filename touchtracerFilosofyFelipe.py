import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException, Ellipse, Line
from random import random
from kivy.uix.widget import Widget
from math import sqrt
from kivy.properties import ObjectProperty
import threading, socket, time, re

Builder.load_string("""
<Touchtracer>:
	canvas:
		Color:
			rgb: 1, 1, 1
		Rectangle:
			source: 'data/images/background.jpg'
			size: self.size

	BoxLayout:
		padding: '10dp'
		spacing: '10dp'
		size_hint: 1, None
		pos_hint: {'top': 1}
		height: '44dp'
		Image:
			size_hint: None, None
			size: '24dp', '24dp'
			source: 'data/logo/kivy-icon-64.png'
			mipmap: True
		Label:
			height: '24dp'
			text_size: self.width, None
			color: (1, 1, 1, .8)
			text: 'Kivy - Touchtracer'
			valign: 'middle'
""")



class Touchtracer(Widget):

	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	server_port = 5006
	
	def __init__(self, **kwargs):
		super(Touchtracer, self).__init__(**kwargs)
		# Ejecutamos el servidor
		thread = threading.Thread(target=self.receive_points)
		thread.start()


	def on_touch_down(self, touch):
		with self.canvas:
			touch.ud['line'] = Line(points=[touch.x, touch.y])

	def on_touch_move(self, touch):
		touch.ud['line'].points += [touch.x, touch.y]

	def on_touch_up(self, touch):
		self.send_points('127.0.0.1', 5005, str(touch.ud['line'].points))

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Parar el servidor de escucha
	def stop_server(self):
		self.sock_server.close()
		# Es necesario despues de cerrar el socket intentar realizar un envio
		self.send_points('127.0.0.1', self.server_port, '')

	# Arrancar servidor
	def run_server(self):
		self.sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		thread = threading.Thread(target=self.receive_points)
		thread.start()
	
	# Envio de puntos al servidor
	def send_points(self, ip, port, data):
		sock = socket.socket(socket.AF_INET, # Internet
				socket.SOCK_DGRAM) # UDP
		sock.sendto(data, (ip, port))

	# Recepcion de puntos del servidor
	def receive_points(self):
		print "console >> Running server..."
		self.sock_server.bind(('127.0.0.1', self.server_port))
		while 1:
			try:
				data, addr = self.sock_server.recvfrom(10240)
				if len(data) != 0:
					print "console >> Data received from",addr
					self.draw_points(data)
				else:
					print "console >> Stopping server"
			except:
				break

	def draw_points(self, data):
		p = re.compile('\d+\.\d*')
		d = p.findall(data)

		# Aseguramos que vamos a recorrer el array esperado y no otro dato
		#if len(d >= 2):
		d_float = [float(item) for item in d]
		print "console >> Drawing points"
		with self.canvas:
			Line(points=d_float)
	

class TouchtracerApp(App):

	ttracer = Touchtracer()

	def build(self):
		return self.ttracer

	def on_stop(self):
		self.ttracer.stop_server()

if __name__ == '__main__':
	TouchtracerApp().run()