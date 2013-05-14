from comm import *

class client_thread(Thread) :
	def __init__(self, sock):
		self.sock = sock
		self.mode = ''
		self.data_sock = ''
		chdir(base_dir)

	def run(self):
		print 'running...'
		try :
			while 1:
				msg = self.sock.recv(4)
				if msg == '':
					raise RuntimeError('socket connection broken')
				print 'recv', msg

				try:
					cmd = str(msg).split()[0]
					msg += self.sock.recv(100)	
					arg = msg.split()
					if cmd == 'PORT' :
						self.data_sock = socket(AF_INET, SOCK_STREAM)
						ip = self.sock.getsockname()[0]
						print arg, msg
						port = int(msg[4:])
						print 'port', ip, port, 'connecting'
						self.data_sock.connect((ip, port))
						print 'port', ip, port, 'connected', self.data_sock
						self.mode = 'port'
					elif cmd == 'PASV':
						self.data_sock = do_port(self.sock)
						self.mode = 'pasv'
					elif cmd == 'get' :
						data_sock = self.data_sock
						if len(arg) != 2:
							raise InputErrorException("Invalid GET command")
						fname = arg[1]
						f = file(fname, 'rb')
						print 'get', arg[0], arg[1]
						t = send_file(data_sock, fname)
						t.run()
					elif cmd == 'put' :
						data_sock = self.data_sock
						if len(arg) != 2:
							raise InputErrorException("Invalid GET command")
						fname = arg[1]
						f = file(fname, 'wb')
						print 'get', arg[0], arg[1]
						t = recv_file(data_sock, fname)
						t.run()	
					elif cmd == 'pwd' :
						msg = str(getcwd())
						self.sock.send(msg)
						msg = self.sock.recv(1000)
					elif cmd == 'dir' :
						msg = str(listdir('.'))
						self.sock.send(msg)
						msg = self.sock.recv(1000)
					elif cmd == 'cd' :
						chdir(' '.join(arg[1:]))
					elif cmd == 'quit' :
						print 'quit'
						break
					else:
						raise InputErrorException(msg)
					self.sock.send('OK.')
				except InputErrorException, s:
					print "ERROR INPUT: ", s.msg
				except OSError, s:
					self.sock.send(str(s))	
		except RuntimeError, s:
			print 'ERROR : ', s
		finally:
			self.sock.close()
			print 'thread client closed'

try:
	s = socket(AF_INET, SOCK_STREAM)
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind((gethostname(), control_port))

	s.listen(5)
	
	l = []
	while 1:
		(c, addr) = s.accept()
		print 'accept ', c, addr
		l.append(client_thread(c))
		l[-1].run()

finally:
	s.close()
