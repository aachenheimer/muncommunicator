from socket import *
import os
import selectors
import json

selector = selectors.DefaultSelector()

PORT = 7999 #change in config file
NUMROOMS = 5 #change later obv i forget how many rooms there are / read from json file
DEFAULTIP = '127.0.0.1' #set later to W003 ip / whatever is in the config file

#store in a dictionary why not
#makes set value function better n easier

#TODO
#send messages ability
#change config file ability
#update (make a command called update) W003 what your committee name and room number is
#share a master file from W003
#make the W003 program lol...
#make input nonblocking
#make a command to list which room belongs to which committee and an additional parameter to list their ips

def setValues():
	configFile = open("config.txt", "r")
	#for currentLine

	configFile.close()



def parseInput(rawString):
	parsedText = []
	currentString = ""
	onMessage = False
	for currentChar in rawString:
		#print("%c " %currentChar, end = '')
		if currentChar == " " and onMessage == False:
			if currentString != "":
				parsedText.append(currentString)
			currentString = ""
			continue
		elif currentChar == "\"" and onMessage == False:
			print("TESTING : ENTERING MESSAGE")
			currentString = ""
			onMessage = True
			continue
		elif currentChar == "\"" and onMessage == True:
			print("TESTING : REACHED END OF MESSAGE")
			parsedText.append(currentString)
			currentString = ""
			onMessage = False
			continue
		currentString += currentChar
		#print("appended char \'%c\'" %currentChar, end = '')
		#print("")
	if currentString != "":
		parsedText.append(currentString)
	
	return parsedText

def help(input):
	if len(input) == 1:
		print("\nsendmsg : sends a message, by default to W003")
		print("config : opens config menu")
		print("exit : exits the program")
		print("type \'help\' followed by the name of the command you want more information on\n")
	else:
		if input[1].upper() == "SENDMSG":
			print("\nSend text messages to W003 or other rooms")
			print("sendmsg \"message\" -destination\n")
			
		elif input[1].upper() == "CONFIG":
			print("\nOpens the config menu")
			print("Used to change port, default send ip, name, and room configuation\n")

		elif input[1].upper() == "EXIT":
			print("\nExits the program without throwing an error\n")

def sendmsg(msg, ip=DEFAULTIP):
	#change the parameter to be the room you want to send it to
	#doesnt need to be registered under selectors because its very briefly established
	#also this can be blocking b/c we can wait to send the message
	sendSocketfd = socket(AF_INET, SOCK_STREAM)
	sendSocketfd.connect((ip, PORT))

def acceptSocket(receiveSocket):
	#also doesnt need to be registered under selectors b/c again, very briefly established
	incomingSocketfd, addr = receiveSocket.accept()
	incomingMsg = incomingSocketfd.recv(1024)
	print("\nReceived connection from %s" %addr[0])
	print("Received msg : %s\n\a" %incomingMsg.decode())
	incomingSocketfd.close()

receiveSocketfd = socket(AF_INET, SOCK_STREAM) #FOR RECEIVING MESSAGES FROM OTHER ROOMS
receiveSocketfd.setblocking(False)
receiveSocketfd.bind(('127.0.0.1', PORT))
receiveSocketfd.listen(NUMROOMS)
selector.register(receiveSocketfd, selectors.EVENT_READ, acceptSocket)

while True:
	events = selector.select(0)
	for key in events:
		callback = key[0].data
		callback(receiveSocketfd)

	choice = input("Type \'help\' for more options\n>")

	#print("TESTING %s" %choice)
	
	parsedInput = parseInput(choice)
	#print("TESTING : ", parsedInput)

	if parsedInput[0].upper() == "HELP":
	#	os.system('cls')
		help(parsedInput)

	if parsedInput[0].upper() == "EXIT":
	#	os.system('cls')
		print("\nCredit : Andrew DeRose\nThanks!\n")
		exit()

	else:
		print("\nUnrecognized command : \"%s\"\n" %choice)
		
