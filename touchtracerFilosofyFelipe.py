#!/usr/bin/kivy
import kivy
kivy.require('1.0.6')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Point, GraphicException, Ellipse, Line
from random import random
from kivy.uix.widget import Widget
from math import sqrt
import asyncore
import socket

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

def calculate_points(x1, y1, x2, y2, steps=5):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    if dist < steps:
        return None
    o = []
    m = dist / steps
    for i in range(1, int(m)):
        mi = i / m
        lastx = x1 + dx * mi
        lasty = y1 + dy * mi
        o.extend([lastx, lasty])
    return o

class Touchtracer(FloatLayout):

	def on_touch_down(self, touch):
		color = (random(), random(), random())
		with self.canvas:
			Color(*color)
			touch.ud['line'] = Line(points=(touch.x, touch.y))

	def on_touch_move(self, touch):
		touch.ud['line'].points += [touch.x, touch.y]
		# Anadimos los puntos al vector
		#UDP_toSend.append(touch.ud['line'].points)
		self.send_points(str(touch.ud['line'].points))

	def on_touch_up(self, touch):
		# Enviamos los puntos
		return

	def send_points(self, data):
		UDP_IP = "10.100.9.253"
		UDP_PORT = 5005

		sock = socket.socket(socket.AF_INET, # Internet
				socket.SOCK_DGRAM) # UDP
		sock.sendto(data, (UDP_IP, UDP_PORT))

	def receive_points(self):
		UDP_IP = "127.0.0.1"
		UDP_PORT = 5006

		sock = socket.socket(socket.AF_INET, # Internet
							socket.SOCK_DGRAM) # UDP
		sock.bind((UDP_IP, UDP_PORT))
		data, addr = sock.recvfrom(10240)

	def draw_points(self, data):
		pass

class TouchtracerApp(App):
    title = 'Touchtracer'
    icon = 'icon.png'

    def build(self):
        return Touchtracer()

    '''
    Si vamos a tener el servidor de escucha corriendo
    todo el momento, podemos ejecutar on_start
    '''
    def on_start(self):
        return

   	'''
   	Paramos el servidor de escucha, si lo tenemos
   	corriendo
   	'''
    def on_pause(self):
    	return True

    def on_resume(self):
    	# No se garantiza que se ejecute despues de
    	# on_pause
    	return

    def on_stop(self):
    	return

class AsyncoreServerUDP(asyncore.dispatcher):
	def __init__(self):
		asyncore.dispatcher.__init__(self)

		# Bind to port 5005 on all interfaces
		self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.bind(('', 5006))

	# Even though UDP is connectionless this is called when it binds to a port
	def handle_connect(self):
		print "Server Started...  estoy escuchando"
		if __name__ == '__main__':
			TouchtracerApp().run()

	# This is called everytime there is something to read
	def handle_read(self):
		data, addr = self.recvfrom(10240)
		Touchtracer.draw_points(data)
		print str(addr)+" >> "+data

	# This is called all the time and causes errors if you leave it out.
	def handle_write(self):
		pass

AsyncoreServerUDP()
asyncore.loop()
