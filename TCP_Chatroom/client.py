import threading
import socket

nickname = input("Choose a nickname: ")

if nickname == 'admin':
	password = input("Enter password for admin controls: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5555))

stop_thread = False

def receive():
	"""
	Recieve from the server
	"""
	while True:
		global stop_thread
		if stop_thread:
			break
		try:
			message = client.recv(1024).decode('ascii')
			if message == "NICK":
				client.send(nickname.encode('ascii'))
				next_message = client.recv(1024).decode('ascii')
				if next_message == 'PASS':
					client.send(password.encode('ascii'))
					if client.recv(1024).decode('ascii') == 'REFUSE':
						print("Connection was refused! Wrong password")
						stop_thread = True
				elif next_message == 'BAN':
					print('connection refused because you are banned!')
					client.close()
					stop_thread = True
			else:
				print(message)
		except:
			print("An error occurred!")
			client.close()
			break

def write():
	"""
	Function is always watiting for the new message
	"""
	while True:	
		if stop_thread:
			break
		message = f'{nickname}: {input("")}'
		if message[len(nickname)+2:].startswith('/'):
			if nickname == 'admin':
				if message[len(nickname)+2:].startswith('/kick'):
					client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('ascii'))
				if message[len(nickname)+2:].startswith('/ban'):
					client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
			else:
				print("Command can only be executed by the admin!")
		else:
			client.send(message.encode('ascii'))

receive_thread = threading.Thread(target = receive)
receive_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()