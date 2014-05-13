import socket,sys
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
		cursor.execute("INSERT INTO user VALUES ('', %s, 0, 0, 0)", (username,))
		cursor.close()
		DB.commit()
		id_user = getIdUser(username)
		return id_user

def getPunctuation(id_user):
	cursor = DB.cursor()
	cursor.execute("SELECT point FROM punctuation WHERE FK_user = %s", (id_user,))		
	punctuation = cursor.fetchall()
	ret = 0
	for point in punctuation:
		ret += point
	return ret

def getOnlineUser(id_user):
	cursor = DB.cursor()
	cursor.execute("SELECT id_user, username FROM user WHERE user.online = 1")		
	users = cursor.fetchall()
	DB.commit()
	dic = {}
	if users:
		for row in users:
			if row[0] != int(id_user):
				dic[row[1]] = getPunctuation(row[0]) 
		return dic
	else:
		return dic

def putPoint(id_user, punctuation, id_connection):
	ret = False
	try:
		cursor = DB.cursor()
		cursor.execute("INSERT INTO punctuation VALUES ('', %s, %s, %s)", (punctuation, id_user, id_connection))
		cursor.close()
		DB.commit()
		ret = True
	except Exception, e:
		ret = False

	return ret

def process_action (action, data):

	if action == "INIT_SESSION":
		id_user = getIdUser(data["username"])
		print "User INIT_SESSION with id:", id_user
		dic = {}
		if id_user:
			dic["id_user"] = id_user
			response = make_response("OK",dic)
			conn.send(response) # echo
		else:
			response = make_response("ERROR",dic)
			conn.send(response)

	elif action == "GET_ONLINE_USER":
		print "User with id_user = ", data["id_user"], "GET_ONLINE_USER"
		users = getOnlineUser(data["id_user"])
		if users:
			response = make_response("OK",users)
			conn.send(response) # echo
		else:
			response = make_response("ERROR",{})
			conn.send(response) # echo

	elif action == "PUT_POINT":
		print "User with id_user = ", data["id_user"], "PUT_POINT"
		res = putPoint(data["id_user"], data["punctuation"], data["id_connection"])
		if res:
			response = make_response("OK",{})
			conn.send(response)
		else:
			response = make_response("ERROR",{})
			conn.send(response) # echo

	elif action == "":
		pass

while 1:
	data = conn.recv(BUFFER_SIZE)
	if data:

		try:
			message = json.loads(data)

			if message["action"] == "close":
				print "conexion close:", message["action"]
				conn.send(data) # echo 
				conn.close()
				conn, addr = s.accept()
			else:
				process_action(message["action"], message["data"])

		except Exception, e:
			dic = {}
			dic["message"]=str(e)
			data = make_response("ERROR", dic)
			conn.send(data) # echo 
			conn.close()
			conn, addr = s.accept()			
				

conn.close()

