"""
Making a program that creates a chatroom that can connect to a 
surver and be visible for anyone to connect

Definitions of some important information:
IP - Loopback internet protocol
	- 127.0.0.1 is a localhost, it is a address that is used to establish
	  an IP connection to the same machine or computer being used by the end-user.


Youtube Video:
https://www.youtube.com/watch?v=3UOyky9sEQY&list=WL&index=26&ab_channel=NeuralNine 

"""


import threading
import socket

host = '127.0.0.1' #localhost
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen() #listens for incoming connection

clients = []
nicknames = []

def brodcast(message): 
	"""
	Brodcasts the message to all the users that are connected to the same server.
	"""
	for client in clients:
		client.send(message)

def handle(client): 
	"""
	This function is constantly listening for the client's response and if they cause the
	any error then the function will remove them from the list, and if they don't cause 
	any error then the function will brodcast a message.
	"""
	while True:
		try:
			msg = message = client.recv(1024)
			if msg.decode('ascii').startswith('KICK'):
				if nicknames[clients.index(client)] == 'admin':
					name_to_kick = msg.decode('ascii')[5:]
					kick_user(name_to_kick)
				else:
					client.send('Command was refused!'.encode('ascii'))
			elif msg.decode('ascii').startswith('BAN'):
				if nicknames[clients.index(client)] == 'admin':
					name_to_ban = msg.decode('ascii')[4:]
					kick_user(name_to_ban)
					with open('bans.txt', 'a') as f:
						f.write(f'{name_to_ban}\n')
					print(f'{name_to_ban} was banned!')
				else:
					client.send('Command was refused!'.encode('ascii'))
			else:
				brodcast(message)
		except: #this is where we handle if they cause any problem
			index = clients.index(client) #finding the index of the client to remove
			clients.remove(client)
			client.close()
			nickname = nicknames[index] #each client have the nickname at the same index
			brodcast(f'{nickname} left the chat!'.encode('ascii'))
			nicknames.remove(nickname)
			break

def receive():
	"""
	This is the main method for the server.
	"""
	while True:
		client, address = server.accept() 
		print(f'Connected with {str(address)}') #Prints to the server who got connected.

		client.send('NICK'.encode('ascii')) #asking the client for the nickname
		nickname = client.recv(1024).decode('ascii') #recieves the nickname of the client
		
		with open('bans.txt', 'r') as f:
			bans = f.readlines()

		if nickname + '\n' in bans:
			client.send('BAN'.encode('ascii'))
			client.close()
			continue

		if nickname == 'admin':
			client.send('PASS'.encode('ascii'))
			password = client.recv(1024).decode('ascii')

			if password != 'adminpass':
				client.send('REFUSE'.encode('ascii'))
				client.close()
				continue


		nicknames.append(nickname) #add to the list of nicknames
		clients.append(client) #add to the list of client

		print(f'Nickname of the client is {nickname}!') #prints to the server of what the name is for the client
		brodcast(f'{nickname} joined the chatroom.'.encode('ascii')) #sends message to all the users about who joined
		client.send('Connected to the server!'.encode('ascii')) #tells the user that they are connected

		thread = threading.Thread(target = handle, args = (client,)) #thread so everything works at the same time.
		thread.start()

def kick_user(name):
	if name in nicknames:
		name_index = nicknames.index(name)
		client_to_kick = clients[name_index]
		clients.remove(client_to_kick)
		client_to_kick.send('You were kicked by an admin!'.encode('ascii'))
		client_to_kick.close()
		nicknames.remove(name)
		brodcast(f'{name} was kicked by the admin!'.encode('ascii'))


print("Server is listening...")
receive()