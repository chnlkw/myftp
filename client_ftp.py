from comm import *
mode = 'PORT'
def create_data_sock(control_sock):
	if mode == 'PORT':
		control_sock.send('PORT');
		return do_port(control_sock)
	elif mode == 'PASV':
		control_sock.send('PASV ');
		return do_pasv(control_sock)
	else:
		raise RuntimeError("Invalid data connection mode")

sock = socket(AF_INET, SOCK_STREAM)

sock.connect((host, control_port))
while 1:
	try:
		s = raw_input()
		arg = str(s).split()
		cmd = arg[0]
		if cmd == 'get':
			if len(arg) != 3:
				raise InputErrorException("Invalid get arguments")
			fname = arg[2]
			f = file(fname,'wb')
			data_sock = create_data_sock(sock)
			sock.send('get '+arg[1])
			t = recv_file(data_sock, fname)
			t.run()
		elif cmd == 'put':
			if len(arg) != 3:
				raise InputErrorException("Invalid get arguments")
			fname = arg[2]
			f = file(fname,'rb')
			data_sock = create_data_sock(sock)
			sock.send('put '+arg[1])
			t = send_file(data_sock, fname)
			t.run()
		elif cmd == 'pwd':
			sock.send('pwd   ')
			msg = sock.recv(1000)
			print msg
			sock.send('FIN')
		elif cmd == 'dir' :
			sock.send('dir   ')
			msg = sock.recv(1000)
			print eval(msg)
			sock.send('FIN')
		elif cmd == 'cd' :
			sock.send(s+'   ')
		elif cmd == 'quit' :
			sock.send('quit  ')
			break;
		elif cmd == '?' :
			print '''Commands:
		get %server_file %client_file
		put %server_file %client_file
		pwd
		dir
		cd %directory
		quit
		?'''
		else:
			raise InputErrorException('unknown command '+cmd)
		msg = sock.recv(1000)
		print msg
	except InputErrorException, s:
		print "ERROR INPUT: ", s.msg
sock.close()
