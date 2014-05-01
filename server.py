import socket
import json
import MySQLdb

#conexion TCP parameter
TCP_IP = ''
TCP_PORT = 5011
BUFFER_SIZE = 1024 # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connection address:', addr

#conexion to DB
HOST = "localhost"
USER = "pract11"
PASSWD = "pract11"
DB = "pract11"

DB = MySQLdb.connect(host = HOST, user = USER, passwd = PASSWD, db = DB)

def make_response (status, data):
	dic = {}
	dic["status"] = status
	dic["data"] = data
	return json.dumps(dic)

def getIdUser(username):
	cursor = DB.cursor()
	cursor.execute("SELECT id_user FROM user WHERE username = %s" , (username,) )
	id_user = cursor.fetchone()
	if id_user:
		cursor = DB.cursor()
		cursor.execute("UPDATE user SET online = 1 WHERE username = %s" , (username,) )
		DB.commit()
		cursor.close
		return id_user[0]
	else:
		cursor.close()
		cursor = DB.cursor()
		cursor.execute("INSERT INTO user VALUES ('', %s, 0, 0)", (username,))
		cursor.close()
		DB.commit()
		id_user = getIdUser(username)
		return id_user
		
def process_action (action, data):

	if action == "INIT_SESSION":
		id_user = getIdUser(data["username"])
		print "User INIT_SESSION with id:", id_user
		conn.send(json.dumps(data)) # echo

	elif action == "":
		pass

while 1:
	data = conn.recv(BUFFER_SIZE)
	if data:
		message = json.loads(data)

		if message["action"] == "close":
			print "conexion close:", message["action"]
			conn.send(data) # echo 
			conn.close()
			conn, addr = s.accept()
		else:
			process_action(message["action"], message["data"])		
				

conn.close()

