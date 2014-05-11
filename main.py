# This Python file uses the following encoding: utf-8
import kivy
kivy.require('1.1.2')
from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')

from kivy.app import App
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle, Point, GraphicException, Ellipse, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.listview import ListView
from kivy.uix.listview import ListItemButton
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.core.window import Window

from math import sqrt
from random import random
import threading, socket, time, re, time, json

# esto es un comentario

Builder.load_file('touchtracer.kv')
sm = ScreenManager()
id_user = -1 			# lo inicilizamos a un indice no valido en la BD
drawer = False			# inicializamos el usuario como NO dibujador
ip_opponent = '127.0.0.1'
port_opponent = 5005

"""
	Utilities: Clase de utilidades para las demas clases
"""
class Utilities():

	TCP_IP = 'proyec3.eii.us.es'
	TCP_PORT = 5011

	"""
		Usado para el envio de cualquier mensaje al servidor.
		Devuelve el dato enviado como respuesta del servidor. Si ocurre cualquier error,
		devuelve cadena vacia.

		NOTA: Los metodos aqui escritos no deben imprimir nada por pantalla.
	"""
	def send_message(self, message):
		
		BUFFER_SIZE = 1024
		MESSAGE = message
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self.TCP_IP, self.TCP_PORT))
			s.send(MESSAGE)
			data = s.recv(BUFFER_SIZE)
			s.send('{"action":"close"}')
			# Capturamos el mensaje de respuesta del servidor para que no se quede esperando nuestra respuesta
			s.recv(BUFFER_SIZE)
			s.close()
		except:
			data = ''

		return data

	def popupCancelarAceptar(self,txt_title,txt_content):
		res = 0
		layout = BoxLayout(orientation='vertical')
		lab = Label(text=txt_content)
		btnCerrar = Button(text='Cerrar', size_hint=(.5,.2))
		btnAceptar= Button(text='Aceptar', size_hint=(.5,.2))
		
		layout.add_widget(lab)
		layout.add_widget(btnCerrar)
		layout.add_widget(btnAceptar)

		popup = Popup(title=txt_title,content=layout,size_hint=(.8, .5))

		btnCerrar.bind(on_press=popup.dismiss)
		if btnAceptar.bind(on_press=popup.dismiss):
			res = 1
		popup.open()

		return res

	def popup(self, txt_title, txt_content):
		layout = BoxLayout(orientation='vertical')
		lab = Label(text=txt_content)
		btn = Button(text='Cerrar', size_hint=(1,.2))
		
		layout.add_widget(lab)
		layout.add_widget(btn)

		popup = Popup(
			title=txt_title,
			content=layout,
			size_hint=(.8, .5)
			)

		btn.bind(on_press=popup.dismiss)
		popup.open()

"""
	Crear listado de usuarios conectados
"""
class UserListScreen(Screen):

	def __init__(self, **kwargs):
		super(UserListScreen, self).__init__(**kwargs)
		
		utilities = Utilities()
		global id_user
		js_response = json.loads(utilities.send_message('{"action":"GET_ONLINE_USER","data":{"id_user":"'+str(id_user)+'"}}'))
		
		list_item_args_converter = \
			lambda row_index, obj: {'text': '[b]'+obj+'[/b] ---- Ptos: ' + str(js_response['data'][obj]),
                                    'size_hint_y': None,
                                    'selected_color': [.5,.5,.5,1],
                                    'deselected_color': [.3,.3,.3,1],
                                    'markup': True}
		print list_item_args_converter
		
		print 'height: ' + str(self.height)
		print 'console >> Connected users', js_response['data']
		
		self.list_adapter = \
			ListAdapter(data=js_response['data'],
						args_converter=list_item_args_converter,
						selection_mode='single',
						propagate_selection_to_data=False,
						allow_empty_selection=False,
						cls=ListItemButton)
		
		list_view = ListView(adapter=self.list_adapter)
		layout = self.ids.lst_user
		layout.add_widget(list_view)

	def play(self):
		#print 'console >> Starting the game',self.list_adapter.selection  # como saber quien esta seleccionado
		#self.manager.current = 'playDrawer'
		#print "hola mundo"
		self.manager.current = 'playDrawer'
		#self.manager.current = 'playViewer'

	def back(self):
		self.manager.current = 'login'


class LoginScreen(Screen):
	def __init__(self, **kwargs):
		super(LoginScreen, self).__init__(**kwargs)

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Gestiona el nombre de usuario al loguearse
	def user_login(self):
		username = self.ids.txt_userLogin.text
		utilities = Utilities()
		if len(username) != 0:
			server_response = utilities.send_message('{"action":"INIT_SESSION", "data":{"username":"'+str(username)+'"}}')
			if server_response != '':
				js_response = json.loads(server_response)
				if js_response != '' and js_response["status"] == 'OK':
					global id_user
					id_user = js_response["data"]["id_user"]
					print 'console >> Usuario con id',id_user,'conectado'
					
					sm.add_widget(UserListScreen(name='userList'))
					self.manager.current = 'userList'
				else:
					# Mostrar popup
					utilities.popup('Error', 'Elija otro nombre de usuario')
			else:
				print 'console >> Connection problem'
				utilities.popup('Error', 'Error de conexion')
		else:
			print 'console >> No username written'
			utilities.popup('Error', 'Escriba su nombre de usuario')
			

class PlayViewerScreen(Screen):
	uxSeconds = NumericProperty(0)
	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	server_port = 5005
	#uxSecondsStr = StringProperty('')
	def __init__(self, **kwargs):
		super(PlayViewerScreen, self).__init__(**kwargs)
		Clock.schedule_interval(self.update_timer, 1)
		# Creamos el hilo del servidor
		thread = threading.Thread(target=self.receive_points)
		thread.start()

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Recepcion de puntos del servidor
	def receive_points(self):
		print "console >> Running server..."
		self.sock_server.bind(('', self.server_port))
		while 1:
			try:
				data, addr = self.sock_server.recvfrom(10240)
				if len(data) != 0:
					print "console >> Data received from",addr
					self.draw_points(data)
				else:
					print "console >> Stopping server"
			except:
				print "console >> ERROR receiving data"
				break

	# Parar el servidor de escucha
	def stop_server(self):
		self.sock_server.close()
		# Es necesario despues de cerrar el socket intentar realizar un envio
		self.send_points('127.0.0.1', self.server_port, '')

	# Envio de puntos al servidor
	def send_points(self, ip, port, data):
		sock = socket.socket(socket.AF_INET, # Internet
				socket.SOCK_DGRAM) # UDP
		sock.sendto(data, (ip, port))

	# Arrancar servidor
	def run_server(self):
		self.sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		thread = threading.Thread(target=self.receive_points)
		thread.start()

	def draw_points(self, data):
		p = re.compile('\d+\.\d*')
		d = p.findall(data)

		# Aseguramos que vamos a recorrer el array esperado y no otro dato
		#if len(d >= 2):
		d_float = [float(item) for item in d]
		print "console >> Drawing points"
		with self.canvas:
			Line(points=d_float)

	def update_timer(self, second):
		if self.uxSeconds <= 29:
			self.uxSeconds += 1
		#self.uxSecondsStr = str(self.uxSeconds)

	def salir(self):
		Utilities().popupCancelarAceptar('Warning', '    ¿seguro que desea salir? \n se contará como una perdida')

#	def on_touch_down(self, touch):
#		pass

	def on_touch_move(self, touch):
		pass

	def on_touch_up(self, touch):
		pass

class PlayDrawerScreen(Screen):
	uxSeconds = NumericProperty(0)
	#uxSecondsStr = StringProperty('')
	def __init__(self, **kwargs):
		super(PlayDrawerScreen, self).__init__(**kwargs)
		Clock.schedule_interval(self.update_timer, 1)

	def on_touch_down(self, touch):
		w, h = Window.system_size
		h_layout = self.ids.layout_barra_titulo.height

		#Si presionamos dentro de los límites del botón Salir => Salimos
		#if (touch.y > h-h_layout) and touch.x < (w*0.20):
		#	self.salir()
		#Si presionamos dentro de los límites del Borrar => Borramos
		#elif (touch.y > h-h_layout) and touch.x > (w*0.80):
		#	pass

		#else:
		if touch.y > h-h_layout: 
			touch.y = h-h_layout
		with self.ids.layout_dibujo.canvas:
			touch.ud['line'] = Line(points=[touch.x, touch.y])
			

	def on_touch_move(self, touch):
		w, h = Window.system_size
		h_layout = self.ids.layout_barra_titulo.height
		if touch.y > h-h_layout: touch.y = h-h_layout

		touch.ud['line'].points += [touch.x, touch.y]

	def on_touch_up(self, touch):
		w, h = Window.system_size
		h_layout = self.ids.layout_barra_titulo.height
		if (touch.y > h-h_layout) and touch.x < (w*0.20):
			self.salir()
		elif (touch.y > h-h_layout) and touch.x > (w*0.80):
			self.borrarPantalla()
		elif len(touch.ud['line'].points) > 0:
			global ip_opponent
			global port_opponent
			self.send_points(ip_opponent, port_opponent, str(touch.ud['line'].points))

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Envio de puntos al servidor
	def send_points(self, ip, port, data):
		sock = socket.socket(socket.AF_INET, # Internet
				socket.SOCK_DGRAM) # UDP
		sock.sendto(data, (ip, port))
	
	def update_timer(self, second):
		if self.uxSeconds <= 29:
			self.uxSeconds += 1
		#self.uxSecondsStr = str(self.uxSeconds)

	def salir(self):
		utility = Utilities()
		res = utility.popupCancelarAceptar('Warning', '    ¿seguro que desea salir? \n se contará como una perdida')
		self.manager.current = 'userList'
		#self.remove_screen(self)

	def borrarPantalla(self):
		#Window.clear()
		print "console >> Erasing drawing"
		self.ids.layout_dibujo.canvas.clear()
		

sm = ScreenManager()
sm.add_widget(LoginScreen(name='login'))
sm.add_widget(PlayDrawerScreen(name='playDrawer'))
sm.add_widget(PlayViewerScreen(name='playViewer'))
#sm.add_widget(StatisticsScreen(name='statisticsScreen'))

class TouchtracerApp(App):

	title = 'Touchtracer'
	icon = 'icon.png'

	def build(self):
		return sm

	def on_stop(self):
		# Paramos el servidor si no somos dibujantes
		global drawer
		if not drawer: sm.get_screen('playViewer').stop_server()

if __name__ == '__main__':
	TouchtracerApp().run()