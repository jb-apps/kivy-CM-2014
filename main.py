# This Python file uses the following encoding: utf-8
import kivy
kivy.require('1.1.2')
from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '480')

from kivy.uix.image import Image
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
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
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
port_opponent = 5006	# puerto oponente necesario en UserListScreen
port_own = 5005			# puerto propio necesario en UserListScreen
word = 'casa'			# palabra a adivinar

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

		boxlayout = BoxLayout(orientation='horizontal', size_hint= (1, None), height='45sp', spacing='5sp')

		btnCerrar = Button(text='Cerrar')#, size_hint=(.5,.2))
		btnAceptar= Button(text='Aceptar')#, size_hint=(.5,.2))
		
		layout.add_widget(lab)
		boxlayout.add_widget(btnCerrar)
		boxlayout.add_widget(btnAceptar)

		layout.add_widget(boxlayout)

		popup = Popup(title=txt_title,content=layout,size_hint=(.8, .5))

		btnCerrar.bind(on_press=popup.dismiss)
		def go_dest(obj):
			sm.transition = SlideTransition(direction='right')
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

	def stop_server(self, sock, port):
		try:
			sock.sendto('', ('127.0.0.1', port))
			sock.close()
			# Es necesario despues de cerrar el socket intentar realizar un envio
			print "console >> Closing socket with Utilities", port
		
			sock.sendto('', ('127.0.0.1', port))
		except:
			print "console >> Server stopped with Utilities"

"""
	Crear listado de usuarios conectados
"""
class UserListScreen(Screen):

	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

	def __init__(self, **kwargs):
		super(UserListScreen, self).__init__(**kwargs)
		w, h = Window.system_size
		
		utilities = Utilities()

		thread = threading.Thread(target=self.receive_user)
		thread.start()
		print "console >> Waiting for user..."

		global id_user
		self.js_response = json.loads(utilities.send_message('{"action":"GET_ONLINE_USER","data":{"id_user":"'+str(id_user)+'"}}'))
		
		self.list_item_args_converter = \
			lambda row_index, obj: {'text': '[b]'+obj+'[/b] ---- Ptos: ' + str(self.js_response['data'][obj]),
                                    'size_hint_y': None,
                                    'height': h*0.2,
                                    'size_hint_x': .8,
                                    'selected_color': [.5,.5,.5,1],
                                    'deselected_color': [.4, .6, .6, 1],
                                    'markup': True}
		print self.list_item_args_converter
		
		print 'height: ' + str(self.height)
		print 'console >> Connected users', self.js_response['data']
		
		self.list_adapter = \
			ListAdapter(data=self.js_response['data'],
						args_converter=self.list_item_args_converter,
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

	def receive_user(self):
		self.sock_server.bind(('', port_own))
		print "console >> Running server to receive user"
		while 1:
			try:
				data, addr = self.sock_server.recvfrom(1024)
				if len(data) != 0:
					print "console >> Data received from", addr
					if not sm.has_screen('playViewer'): sm.add_widget(PlayViewerScreen(name='playViewer'))
					sm.transition = SlideTransition(direction='left')
					self.manager.current = 'playViewer'
				else:
					print "console >> No data received. Stopping server"
			except:
				print "console >> ERROR connecting with user"
				break
		
		print "console >> UserListScreen server stopped from receive_user function"

	def play(self):
		print 'console >> Starting the game',self.list_adapter.selection  # como saber quien esta seleccionado
		self.send_user() # enviar mensaje al oponennte para que juegue
		global drawer
		drawer = True
		if not sm.has_screen('playDrawer'): sm.add_widget(PlayDrawerScreen(name='playDrawer'))
		sm.transition = SlideTransition(direction='left')
		self.manager.current = 'playDrawer'

	def back(self):
		sm.transition = SlideTransition(direction='down')
		self.manager.current = 'login'

	def stop_server(self):
		try:
			self.sock_server.sendto('', ('127.0.0.1', port_own))
			self.sock_server.close()
			# Es necesario despues de cerrar el socket intentar realizar un envio
			print "console >> Closing socket", port_own
		
			self.sock_server.sendto('', ('127.0.0.1', port_own))
		except:
			print "console >> UserListScreen server stopped"


class LoginScreen(Screen):
	def __init__(self, **kwargs):
		super(LoginScreen, self).__init__(**kwargs)

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Gestiona el nombre de usuario al loguearse
	def user_login(self):
		username = self.ids.txt_userLogin.text
		Window.release_all_keyboards() 
		utilities = Utilities()
		if len(username) != 0:
			server_response = utilities.send_message('{"action":"INIT_SESSION", "data":{"username":"'+str(username)+'"}}')
			if server_response != '':
				js_response = json.loads(server_response)
				if js_response != '' and js_response["status"] == 'OK':
					global id_user
					id_user = js_response["data"]["id_user"]
					print 'console >> Usuario con id',id_user,'conectado'
					if not sm.has_screen('userList'): sm.add_widget(UserListScreen(name='userList'))
					sm.transition = SlideTransition(direction='up')
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
	flag = True
	uxSeconds = NumericProperty(0)
	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	#uxSecondsStr = StringProperty('')
	def __init__(self, **kwargs):
		super(PlayViewerScreen, self).__init__(**kwargs)

		# Creamos el hilo del servidor
		thread = threading.Thread(target=self.receive_points)
		thread.start()

		#Clock.schedule_interval(self.update_timer, 1)

	def on_pre_enter(self):
		self.uxSeconds = 0
		if not self.flag: self.flag = True
		#thread = threading.Thread(target=self.receive_points)
		#thread.start()

		Clock.schedule_interval(self.update_timer, 1)

	def on_enter(self):
		pass

	def on_leave(self):
		self.borrar_pantalla()				# nos aseguramos de borrar la pizarra
		if self.flag: self.flag = False 	# nos aseguramos de detener el temporizador
	'''
		Metodos auxiliares de la aplicacion
	'''
	# Recepcion de puntos del servidor
	def receive_points(self):
		print "console >> Running server... port:", port_own+10
		#time.sleep(5)
		self.sock_server.bind(('', port_own+10))
		while 1:
			try:
				data, addr = self.sock_server.recvfrom(10240)
				if len(data) != 0:
					if data == 'erase':
						self.borrar_pantalla()
						print "console >> Erasing drawing"
					elif data == 'exit':
						utilities = Utilities()
						utilities.popup('Fin de juego', 'Se ha acabado el juego')
						print "console >> End of game"
						self.flag = False		# detenemos el temporizador
						sm.transition = SlideTransition(direction='right')
						self.manager.current = 'userList'
						
						#break
					elif data[0] == ':':
						global word
						word = data[1:]
						print "console >> Try:", word
					else:
						print "console >> Data received from", addr, " - ", data
						self.draw_points(data)
				else:
					print "console >> Stopping PlayViewerScreen server"
					break
			except:
				print "console >> ERROR receiving data"
				break

	# Parar el servidor de escucha
	def stop_server(self):
		try:
			self.sock_server.sendto('', ('127.0.0.1', port_own+10))
			self.sock_server.close()
			# Es necesario despues de cerrar el socket intentar realizar un envio
			print "console >> Closing socket", port_own+10
		
			self.sock_server.sendto('', ('127.0.0.1', port_own+10))
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
		if self.uxSeconds <= 29 and self.flag:
			self.uxSeconds += 1
		else:
			print "console >> Stopping time", self.uxSeconds
			return False
		#self.uxSecondsStr = str(self.uxSeconds)

	def comprobar_palabra(self):
		t_word = str(self.ids.txt_word.text)
		print "la palabra: ", t_word
		global word
		print "console >> Comprove that", t_word,"=",word
		if t_word == '':
			pass
		elif t_word == word:
			self.ids.lab_resultado.text = 'Correcto'
			utilities = Utilities()
			utilities.popup('Enhorabuena','Has ganado el juego')

			time.sleep(1)
			self.on_leave()
			#self.score_me
		else:
			self.ids.lab_resultado.text = 'Incorrecto'

			time.sleep(1)
			self.on_leave()

	def score_me(self):
		pass

	def on_touch_up(self, touch):
		w, h = Window.system_size
		layoutInput = self.ids.layout_textInput
		h_layout = layoutInput.height
		
		#TextInput pressed dis
		# comprobamos si hemos presionado el TextInput
		if touch.y > (h-h_layout) and touch.x>w*0.20 and touch.x<w*0.7:
			#Borramos el antiguo text input
			layoutInput.clear_widgets()

			#Creamos un nuevo textInput y activamos el teclado
			newInput = TextInput(text='',multiline=False,id='txt_word',focus='True', font_size=self.height*0.05,allow_copy='True')
			# añadimos el textInput
			layoutInput.add_widget(newInput)

			print touch.pos, h_layout
		# salir pressed
		elif (touch.y > h-h_layout) and touch.x < (w*0.20):
			self.salir()
		# Comprobar palabra pressed
		elif (touch.y > h-h_layout) and touch.x > (w*0.70):
			self.comprobar_palabra()
	
	def salir(self):
		Utilities().popup('Funcion no disponible', 'En esta version del juego, solo el Drawer puede cerrar la conexion con el Viewer.')

	def borrar_pantalla(self):
		self.ids.layout_visualizador.canvas.clear()

class PlayDrawerScreen(Screen):
	flag = True
	uxSeconds = NumericProperty(0)
	#uxSecondsStr = StringProperty('')
	def __init__(self, **kwargs):
		super(PlayDrawerScreen, self).__init__(**kwargs)

		lab = Label(text=word)
		self.add_widget(lab)

		#Clock.schedule_interval(self.update_timer, 1)

	def on_pre_enter(self):
		self.uxSeconds = 0
		if not self.flag: self.flag = True
		time.sleep(1)
		self.send_points(ip_opponent, port_opponent+10, ':'+word)
	
	def on_enter(self):
		Clock.schedule_interval(self.update_timer, 1)

	def on_pre_leave(self):
		# Nos aseguramos de detener el temporizador
		self.flag = False

	def on_leave(self):
		self.send_points(ip_opponent, port_opponent+10, 'exit')
		self.borrarPantalla()

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
			self.send_points(ip_opponent, port_opponent+10, str(touch.ud['line'].points))

	'''
		Metodos auxiliares de la aplicacion
	'''
	# Envio de puntos al servidor
	def send_points(self, ip, port, data):
		sock = socket.socket(socket.AF_INET,	# Internet
				socket.SOCK_DGRAM)				# UDP
		sock.sendto(data, (ip, port_opponent+10))
	
	def update_timer(self, second):
		if self.uxSeconds <= 29 and self.flag:
			self.uxSeconds += 1
		elif self.uxSeconds > 29:
			Utilities().popup('Tiempo agotado','Se ha agotado el tiempo')
			sm.transition = SlideTransition(direction='right')
			self.manager.current = 'userList'
			print "console >> Stopping time", self.uxSeconds
			return False
		else:
			sm.transition = SlideTransition(direction='right')
			self.manager.current = 'userList'
			print "console >> Stopping time", self.uxSeconds
			return False
		#self.uxSecondsStr = str(self.uxSeconds)

	def salir(self):
		utility = Utilities()
		utility.popupCancelarAceptar('Warning', '    ¿seguro que desea salir? \n se contará como una perdida', self, 'userList')
		#self.remove_screen(self)

	def borrarPantalla(self):
		#Window.clear()
		print "console >> Erasing drawing"
		self.send_points(ip_opponent, port_opponent+10, 'erase')
		self.ids.layout_dibujo.canvas.clear()

class TouchtracerApp(App):

	title = 'Touchtracer'
	icon = 'icon.png'

	def build(self):
		return sm

	def on_stop(self):
		# Paramos el servidor si no somos dibujantes
		print 'console >>', len(sm.screens), 'screens to close'
		global drawer
		if not drawer and sm.has_screen('playViewer'): sm.get_screen('playViewer').stop_server()
		if sm.has_screen('userList'):
			sm.get_screen('userList').stop_server()

if __name__ == '__main__':
	sm = ScreenManager()
	sm.add_widget(LoginScreen(name='login'))
	TouchtracerApp().run()