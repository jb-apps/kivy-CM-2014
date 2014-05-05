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
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.listview import ListView
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock
from math import sqrt
from random import random
from kivy.uix.screenmanager import ScreenManager, Screen
import threading, socket, time, re, time, json

#Builder.load_file('touchtracer.kv')

Builder.load_string("""
<LoginScreen>:
	FloatLayout:
		Label:
			font_size: root.height*0.05
			size_hint: .4,.1
			pos_hint: {'x':.3, 'y':.7}
			text: 'Username'
		
		TextInput:
			id: txt_userLogin
			font_size: root.height*0.05
			text:''
			size_hint:.6,.1
			pos_hint: {'x':.2, 'y':.6}
			multiline: False

		Button:
	        font_size: root.height*0.05
	        pos_hint: {'x':.3, 'y':.48}
	        size_hint: .4,.1
	        text: "Aceptar"
			on_press: root.user_login()

<UserListScreen>:

<PlayViewerScreen>:
	Label:
		text: 'PlayViewerScreen'

<PlayDrawerScreen>:
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
			text: 'Kivy - PlayDrawerScreen'
			valign: 'middle'

	FloatLayout:
		canvas:
			Color:
				rgb: 1, 1, 1
			Ellipse:
				size: 60, 60
				pos: 260, 420
			
			Color:
				rgb: 0, 0, 1
			Ellipse:
				size: 60, 60
				angle_start: 0
				angle_end: root.uxSeconds * 6
				pos: 260, 420

			Color:
				rgb: 0, 0, 0
			Ellipse:
				size: 40, 40
				pos: 270, 430

""")

sm = ScreenManager()
id_user = -1 			# lo inicilizamos a un indice no valido en la BD

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


class UserListScreen(Screen):
	def __init__(self, **kwargs):
		super(UserListScreen, self).__init__(**kwargs)
		# Crear listado de usuarios conectados
		utilities = Utilities()
		global id_user
		js_response = json.loads(utilities.send_message('{"action":"GET_ONLINE_USER","data":{"id_user":"'+str(id_user)+'"}}'))
		#list_view = ListView(
        #    item_strings=[str(str(key) + ', ' + str(value)) for key, value in js_response['data'].iteritems()])
		list_adapter = ListAdapter(
			data=[str(str(key) + ', ' + str(value)) for key, value in js_response['data'].iteritems()],
			selection_mode='multiple',
			cls=Label)
		list_adapter.bind(on_selection_change=self.selected_user)
		list_view = ListView(adapter=list_adapter)
		self.add_widget(list_view)
		#self.add_widget(Button(text="Jugar"))

	def selected_user(self):
		print 'Se ha seleccionado un usuario'


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
	pass

class PlayDrawerScreen(Screen):

	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	server_port = 5006
	uxSeconds = NumericProperty(0)
	
	def __init__(self, **kwargs):
		super(PlayDrawerScreen, self).__init__(**kwargs)
		# Creamos el hilo del servidor
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
		self.uxSeconds = int(time.strftime('%S', time.localtime()))

sm = ScreenManager()
sm.add_widget(LoginScreen(name='login'))
sm.add_widget(PlayDrawerScreen(name='playDrawer'))
sm.add_widget(PlayViewerScreen(name='playViewer'))

class TouchtracerApp(App):

	title = 'Touchtracer'
	icon = 'icon.png'

	def build(self):
		Clock.schedule_interval(sm.get_screen('playDrawer').update_timer, 1)
		return sm

	def on_stop(self):
		sm.get_screen('playDrawer').stop_server()

if __name__ == '__main__':
	TouchtracerApp().run()