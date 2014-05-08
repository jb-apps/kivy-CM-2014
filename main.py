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
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock
from math import sqrt
from random import random
from kivy.uix.screenmanager import ScreenManager, Screen
import threading, socket, time, re, time, json
from kivy.core.window import Window

#Builder.load_file('touchtracer.kv')
Builder.load_string("""

<LoginScreen>:
	FloatLayout:
		Label:
			font_size: root.height*0.05
			size_hint: .4,.1
			pos_hint: {'x':.3, 'y':.7}
			multiline: True
			text: 'Ingrese nombre de usuario'

		
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

<<<<<<< HEAD
<UserListScreen@GridLayout>:
	cols: 1

	Button:
		size_hint: (1, None)
		height: 50
		markup: True
		text: '[b]Jugar[/b]'
		on_press: root.play()
=======
<UserListScreen>:
	GridLayout:
<<<<<<< HEAD
		rows: 2
		spacing: 5
		BoxLayout:
            padding: '2sp'
            canvas:
                Color:
                    rgba: 1, 1, 1, .3
                Rectangle:
                    size: self.size
                    pos: self.pos
            size_hint: 1, None
            height: '45sp'
            
            Button:
            	id: back_button
                size_hint: None, 1
                width: root.width*0.20
                text: 'Atrás'
            Widget:
            BoxLayout:
                size_hint: None, 1
                width: root.width*0.5
                Label:
                    text: "Usuarios"
            Button:
            	id: play_button
                size_hint: None, 1
                width: root.width*0.20
                text: 'Play'
                on_press: root.play()
		
		BoxLayout:
			id:lst_user
			orientation: 'vertical'
			canvas:
				Color:
					rgba: 1,1,1,.6
				Rectangle:
					size: self.size
					pos: self.pos
=======
		cols: 1
		
		ListView:
			id: lst_user

		Button:
			size_hint: (1, None)
			height: 50
			markup: True
			text: '[b]Jugar[/b]'
			on_press: root.play()
>>>>>>> 0076cb0eb7bbfb4c86d69f1a28f6d17d203da94a
>>>>>>> 3fa55a63b328e8580183ec3b8a98d3784f407974

<PlayDrawerScreen>:
	Label:
		text: 'PlayDrawerScreen'

<<<<<<< HEAD
<PlayViewerScreen>:
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
			text: 'Kivy - PlayViewerScreen'
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
=======
<StatisticsScreen>:
	Label:
		text: 'StatisticsScreen'

<PlayDrawerScreen>:
	GridLayout:
		rows: 2
		spacing: 5


		BoxLayout:
			orientation: 'horizontal'
            padding: '2sp'
            canvas:
                Color:
                    rgba: 1, 1, 1, .3
                Rectangle:
                    size: self.size
                    pos: self.pos
            size_hint: 1, None
            height: '45sp'
            
            GridLayout:
            	cols:4
            	spacing: 10

	            Button:
	            	id: go_out_button
	                size_hint: None, 1
	                width: root.width*0.20
	                text: 'Salir'
	                on_press: root.salir()

				Label:
					#height: '24dp'
					text_size: self.width, None
					color: (1, 1, 1, .8)
					text: 'PlayDrawerScreen'
					width: root.width*0.40

				BoxLayout:
					pos_hint:1,1
					canvas:
						Color:
							rgba: 1, 1, 1,0.8
						Ellipse:
			                size: self.height,self.height
							pos: self.pos
						
						Color:
							rgba: 0, 0, 1, 0.7
						Ellipse:
			                size: self.height,self.height
			                pos: self.pos
							angle_start: 0
							angle_end: root.uxSeconds * 6
			                
			    Button:
	            	id: clear_button
	                size_hint: None, 1
	                width: root.width*0.20
	                pos_hint:
	                text: 'Borrar'
	                on_press: root.borrarPantalla()

		BoxLayout:
			#size:root.width,root.height*0.2
			canvas:
				Color:
					rgb: 1, 1, 1
				Rectangle:
					source: 'data/images/background.jpg'
					size: self.size
	""")
>>>>>>> 3fa55a63b328e8580183ec3b8a98d3784f407974

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
		
<<<<<<< HEAD
		list_view = ListView(adapter=self.list_adapter, size_hint=(1,.8), pos_hint={'x':0,'center_y':.5}, scrolling=True)
		self.add_widget(list_view)
		#btn = Button(text='[b]Jugar[/b]', size_hint=(1,None), height=50, markup=True)
		#btn.bind(on_press=self.play())
		#self.add_widget(btn)

	def play(self):
		print 'console >> Starting the game with',self.list_adapter.selection  # como saber quien esta seleccionado
		# Verificar si el usuario esta en otra partida 
		self.manager.current = 'playViewer'
=======
		list_view = ListView(adapter=self.list_adapter)
		layout = self.ids.lst_user
		layout.add_widget(list_view)

	def play(self):
		#print 'console >> Starting the game',self.list_adapter.selection  # como saber quien esta seleccionado
		#self.manager.current = 'playDrawer'
		#print "hola mundo"
		sm.add_widget(UserListScreen(name='playDrawer'))
		self.manager.current = 'playDrawer'
>>>>>>> 3fa55a63b328e8580183ec3b8a98d3784f407974


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
			

class PlayDrawerScreen(Screen):	
	pass

class PlayViewerScreen(Screen):

	sock_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	server_port = 5006
	uxSeconds = NumericProperty(0)
	
	def __init__(self, **kwargs):
		super(PlayViewerScreen, self).__init__(**kwargs)
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

	def salir(self):
		pass

	def borrarPantalla(self):
		#Window.clear()
		pass
		

sm = ScreenManager()
sm.add_widget(LoginScreen(name='login'))
sm.add_widget(PlayViewerScreen(name='playViewer'))
<<<<<<< HEAD
sm.add_widget(PlayDrawerScreen(name='playDrawer'))

=======
#sm.add_widget(StatisticsScreen(name='statisticsScreen'))
>>>>>>> 3fa55a63b328e8580183ec3b8a98d3784f407974

class TouchtracerApp(App):

	title = 'Touchtracer'
	icon = 'icon.png'

	def build(self):
		Clock.schedule_interval(sm.get_screen('playViewer').update_timer, 1)
		return sm

	def on_stop(self):
		sm.get_screen('playViewer').stop_server()

if __name__ == '__main__':
	TouchtracerApp().run()