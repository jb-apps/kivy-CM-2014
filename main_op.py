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
port_opponent = 5005	# puerto oponente necesario en UserListScreen
port_own = 5006			# puerto propio necesario en UserListScreen

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

	def popupCancelarAceptar(self,txt_title,txt_content, orig, dest):
		layout = BoxLayout(orientation='vertical')
		lab = Label(text=txt_content)
		btnCerrar = Button(text='Cerrar', size_hint=(.5,.2))
		btnAceptar= Button(text='Aceptar', size_hint=(.5,.2))
		
		layout.add_widget(lab)
		layout.add_widget(btnCerrar)
		layout.add_widget(btnAceptar)

		popup = Popup(title=txt_title,content=layout,size_hint=(.8, .5))

		btnCerrar.bind(on_press=popup.dismiss)
		def go_dest(obj):
			orig.manager.current = dest
		btnAceptar.bind(on_press=go_dest, on_release=popup.dismiss)
		popup.open()


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

	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

	def __init__(self, **kwargs):
		super(UserListScreen, self).__init__(**kwargs)
		
		utilities = Utilities()

		thread = threading.Thread(target=self.receive_user)
		thread.start()
		print "console >> Waiting for user..."

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

	def send_user(self):
		sock = socket.socket(socket.AF_INET,	# Internet
				socket.SOCK_DGRAM)				# UDP
		sock.sendto('sending user', (ip_opponent, port_opponent))

		sock.close()
		try:
			sock.sendto('', ('127.0.0.1', port_own))
		except:
			print "console >> Stopping server"


	def receive_user(self):
		self.sock_server.bind(('', port_own))
		print "console >> Running server to receive user"
		try:
			data, addr = self.sock_server.recvfrom(1024)
			if len(data) != 0:
				print "console >> Data received from",addr
				sm.add_widget(PlayViewerScreen(name='playViewer'))
				self.manager.current = 'playViewer'
			else:
				print "console >> No data received. Stopping server"
		except:
			print "console >> ERROR connecting with user"

		print "console >> Server stopped"

	def play(self):
		print 'console >> Starting the game',self.list_adapter.selection  # como saber quien esta seleccionado
		self.send_user() # enviar mensaje al oponennte para que juegue
		global drawer
		drawer = True
		sm.add_widget(PlayDrawerScreen(name='playDrawer'))
		self.manager.current = 'playDrawer'

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
		print "console >> Running server... port:",port_own+1
		#time.sleep(5)
		self.sock_server.bind(('', port_own+1))
		while 1:
			try:
				data, addr = self.sock_server.recvfrom(10240)
				if len(data) != 0:
					if data == 'erase':
						self.ids.layout_visualizador.canvas.clear()
						print "console >> Erasing drawing"
					else:
						print "console >> Data received from",addr
						self.draw_points(data)
				else:
					print "console >> Stopping server"
					break
			except:
				print "console >> ERROR receiving data"
				break

	# Parar el servidor de escucha
	def stop_server(self):
		self.sock_server.close()
		# Es necesario despues de cerrar el socket intentar realizar un envio
		print "console >> Closing socket",port_own+1
		try:
			self.send_points('127.0.0.1', port_own+1, '')
		except:
			print "console >> Server stopped"

	# Envio de puntos al servidor
	def send_points(self, ip, port, data):
		sock = socket.socket(socket.AF_INET, # Internet
				socket.SOCK_DGRAM) # UDP
		sock.sendto(data, (ip_opponent, port_opponent))

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
		with self.ids.layout_visualizador.canvas:
			Line(points=d_float)

	def update_timer(self, second):
		if self.uxSeconds <= 29:
			self.uxSeconds += 1
		#self.uxSecondsStr = str(self.uxSeconds)

	def salir(self):
		Utilities().popupCancelarAceptar('Warning', '    ¿seguro que desea salir? \n se contará como una perdida', self, 'login')

	def on_touch_down(self, touch):
		pass

	def on_touch_move(self, touch):
		pass

	def on_touch_up(self, touch):
		w, h = Window.system_size
		layoutInput = self.ids.layout_textInput
		textInputWord = self.ids.txt_word
		h_layout = layoutInput.height

		#TextInput pressed
		# comprobamos si hemos presionado el TextInput
		if touch.y > (h-h_layout) and touch.x>w*0.20 and touch.x<w*0.7:
			#Borramos el antiguo text input
			layoutInput.clear_widgets()

			#Creamos un nuevo textInput y activamos el teclado
			textInputWord = TextInput(text='',multiline=False,id='txt_word',
										focus=True,font_size=self.height*0.05)
			# añadimos el textInput
			layoutInput.add_widget(textInputWord)

			print touch.pos, h_layout
		# salir pressed
		elif (touch.y > h-h_layout) and touch.x < (w*0.20):
			#self.salir()
			print "salir pressed"
		# Comprobar palabra pressed
		elif (touch.y > h-h_layout) and touch.x > (w*0.70):
			print "Comprobar pressed"
	
	def salir(self):
		utility = Utilities()
		utility.popupCancelarAceptar('Warning', '    ¿seguro que desea salir? \n se contará como una perdida', self, 'userList')

class PlayDrawerScreen(Screen):
	uxSeconds = NumericProperty(0)
	#uxSecondsStr = StringProperty('')
	def __init__(self, **kwargs):
		super(PlayDrawerScreen, self).__init__(**kwargs)
		Clock.schedule_interval(self.update_timer, 1)

	def on_leave(self):


	def on_touch_down(self, touch):
		w, h = Window.system_size
		h_layout = self.ids.layout_barra_titulo.height

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
		#Si presionamos dentro de los límites del botón Salir => Salimos
		if (touch.y > h-h_layout) and touch.x < (w*0.20):
			self.salir()
		#Si presionamos dentro de los límites del Borrar => Borramos
		elif (touch.y > h-h_layout) and touch.x > (w*0.80):
			self.borrarPantalla()
		elif len(touch.ud['line'].points) > 0:
			self.send_points(ip_opponent, port_opponent+1, str(touch.ud['line'].points))

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Envio de puntos al servidor
	def send_points(self, ip, port, data):
		sock = socket.socket(socket.AF_INET,	# Internet
				socket.SOCK_DGRAM)				# UDP
		sock.sendto(data, (ip, port_opponent+1))
	
	def update_timer(self, second):
		if self.uxSeconds <= 29:
			self.uxSeconds += 1
		#self.uxSecondsStr = str(self.uxSeconds)

	def salir(self):
		utility = Utilities()
		utility.popupCancelarAceptar('Warning', '    ¿seguro que desea salir? \n se contará como una perdida', self, 'userList')
		#self.remove_screen(self)

	def borrarPantalla(self):
		#Window.clear()
		print "console >> Erasing drawing"
		self.send_points(ip_opponent, port_opponent+1, 'erase')
		self.ids.layout_dibujo.canvas.clear()
		


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
	sm = ScreenManager()
	sm.add_widget(LoginScreen(name='login'))
	TouchtracerApp().run()