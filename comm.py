host = '127.0.0.1'
control_port = 13132
base_dir = '/home/chnlkw'

from socket import *
from threading import *
from time import *
from os import *
from struct import *

class send_file(Thread):
	def __init__(self, sock, fname):
		self.sock = sock
		self.f = file(fname, 'rb')
		self.fname = fname
		print 'sending file', sock, fname
	
	def run(self):
		try:
			data = self.f.read()
			print 'SEND DATA', data
			head = pack('Q', len(data))
			print 'send size', len(data)
			self.sock.send(head)
			self.sock.send(data)
			self.sock.recv(2)
		finally:
			#print 'ERROR : sending ', self.sock
			self.sock.close()
			self.f.close()
			print 'Send finished :', self.fname

class recv_file(Thread):
	def __init__(self, sock, fname):
		self.sock = sock
		self.f = file(fname, 'wb')
		self.fname = fname
		print 'recving file', sock, fname
	
	def run(self):
		try:
			head = self.sock.recv(8)
			size = unpack('Q', head)[0]
			print 'recv size', size
			data = ''
			while size > len(data):
				chunk = self.sock.recv(1024)
				if not chunk:
					break
				data += chunk
			self.f.write(data)
			self.sock.send('OK')
		except RuntimeError, s:
			print 'ERROR : recv thread ', self.sock, s
		finally:
			self.sock.close()
			self.f.close()
			print 'Recv finished :', self.fname

def do_port(control_sock):
	data_sock = socket(AF_INET, SOCK_STREAM)
	data_sock.bind(('', 0))
	data_sock.listen(1)
	port = data_sock.getsockname()[1]
	msg = str(port);
	print msg
	control_sock.send(msg);
	(port_sock, addr) = data_sock.accept()
	print control_sock.recv(2)
	print 'port', port, 'accepted'
	return port_sock


def do_pasv(control_sock):
	pasv_sock = socket(AF_INET, SOCK_STREAM)
	ip = pasv_sock.getsockname()[0]
	msg = control_sock.recv(100)		
	port = int(msg)
	print 'port', ip, port, 'connecting to'
	pasv_sock.connect((ip, port))
	print 'port', ip, port, 'connected', pasv_sock
	control_sock.send('OK')
	return pasv_sock

class InputErrorException(Exception):
	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg


