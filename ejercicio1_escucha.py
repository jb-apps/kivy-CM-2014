import socket

#UDP_IP = "10.100.17.162"
UDP_IP = "127.0.0.1"
UDP_PORT = 5006

sock = socket.socket(socket.AF_INET, # Internet
					socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
	data, addr = sock.recvfrom(10240) # buffer size is 1024 bytes
	print "received message:", data