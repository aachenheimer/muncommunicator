from socket import *
import os
import selectors
import json
import sys
from msvcrt import *

selector = selectors.DefaultSelector()

#py2exe for executable file
#msvcrt for input

PORTHOME = 7999 #change in config file
PORTHOST = 7998
NUMROOMS = 5 #change later obv i forget how many rooms there are / read from json file
DEFAULTIP = '127.0.0.1' #set later to W003 ip / whatever is in the config file

#store in a dictionary why not
#makes set value function better n easier

#TODO
#send messages ability DONE
#change config file ability DONE
#update (make a command called update) W003 what your committee name and room number is
#share a master file from W003
#make the W003 program lol...
#make input nonblocking DONE
#make a command to list which room belongs to which committee and an additional parameter to list their ips

roomsJSON = open("rooms.json", "r")
rooms = json.load(roomsJSON)
roomsJSON.close()

NUMROOMS = len(rooms.keys())

configJSON = open("config.json", "r")
config = json.load(configJSON)
configJSON.close()

PORTHOME = config["portHome"]
PORTHOST = config["portHost"]
DEFAULTIP = config["ip"]


def setValues(valueToSet, value):
    if valueToSet != "ip" and valueToSet != "port" and valueToSet != "name" and valueToSet != "room":
        return 0
    configJSON = open("config.json", "r")
    config = json.load(configJSON)
    configJSON.close()
    
    config[valueToSet] = value
    configNew = json.dumps(config)
    configJSON = open("config.json", "w")
    configJSON.write(configNew)
    configJSON.close()

def writeConfigFile():
    print()
    configJSON = open("config.json", "r")
    config = json.load(configJSON)
    for currentEntry in config.keys():
        print("%s - %s" %(currentEntry, config[currentEntry]))
        
def roomsReload():
    roomsJSON = open("rooms.json", "r")
    rooms = json.load(roomsJSON)
    roomsJSON.close()

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
            #print("TESTING : ENTERING MESSAGE")
            currentString = ""
            onMessage = True
            continue
        elif currentChar == "\"" and onMessage == True:
            #print("TESTING : REACHED END OF MESSAGE")
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
        return 0
    
    if input[1].upper() == "SENDMSG":
        print("\nSend text messages to W003 or other rooms")
        print("sendmsg \"message\" -destination")
        print("You must wrap your message in quotes")
        print("Example : \nsendmsg \"hello world!\"\n")
        return 0
            
    elif input[1].upper() == "CONFIG":
        print("\nOpens the config menu")
        print("Used to change port, default send ip, name, and room configuation\n")
        return 0

    elif input[1].upper() == "EXIT":
        print("\nExits the program without throwing an error\n")
        return 0
        
def config():
    while True:
        print("\nWelcome to the config menu\nType \'exit\' to return to default menu")
        choice = ""
        while True:
            events = selector.select(0)
            for key in events:
                callback = key[0].data
                callback(receiveSocketfd)

            if kbhit():
                char = getch()
                c = ord(char)
                if c != 13 and c != 8:
                    try:
                        choice += char.decode()
                        sys.stdout.write(char.decode())
                        sys.stdout.flush()
                    except:
                        continue
                elif c == 8 and len(choice) > 0:
                    choice = choice[:len(choice)-1]
                    #print("\b\b",end='')
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()

                else:
                    break
        #print("\n%s\n"%choice)
        if choice == "":
            continue

        parsedInput = parseInput(choice)

        if parsedInput[0].upper() == "EXIT":
            print("Returning to main terminal\n")
            return 0
            
        elif parsedInput[0].upper() == "HELP":
            print("\n\nOPTIONS:\n-room\n-name\n-ip (of W003)\n-portHome (incoming)\n-portHost (outgoing)")
            print("-reload\nreloads room data\n")
            print("-set *valueToSet *value\nchanges requested value\n")
            print("-view\nviews the config file\n")
            
        elif parsedInput[0].upper() == "RELOAD":
            roomsReload()
            print()
            
        elif parsedInput[0].upper() == "SET":
            if len(parsedInput) < 3:
                print("\nERROR : Not enough arguments!\n")
                continue
            else:
                setValues(parsedInput[1], parsedInput[2])
        
        elif parsedInput[0].upper() == "VIEW":
            writeConfigFile()
	

def sendmsg(msg, room="W003"):
    ip = roomToIP(room.upper())
    if room == "null":
        print("\nInvalid IP / Room!\n")
        return 1
    print("Connecting to room %s on IP %s" %(room, ip))
    #doesnt need to be registered under selectors because its very briefly established
    #also this can be blocking b/c we can wait to send the message
    sendSocketfd = socket(AF_INET, SOCK_STREAM)
    try:
        sendSocketfd.connect((ip, PORTHOST)) #ok so basically only one port; outgoing and incoming. just switch it up
    except:
        print("\nERROR : Host refused!\n")
        return 1
    sendSocketfd.send(msg.encode())
    sendSocketfd.close()
    
def roomToIP(room):
    if room not in rooms.keys():
        return "null"
    
    return rooms[room]["ip"]

def acceptSocket(receiveSocket):
    #also doesnt need to be registered under selectors b/c again, very briefly established
    incomingSocketfd, addr = receiveSocket.accept()
    incomingSocketfd.setblocking(True)
    incomingMsg = incomingSocketfd.recv(1024)
    print("\nReceived connection from %s" %addr[0])
    print("Received msg : %s\n\a" %incomingMsg.decode())
    incomingSocketfd.close()

receiveSocketfd = socket(AF_INET, SOCK_STREAM) #FOR RECEIVING MESSAGES FROM OTHER ROOMS
receiveSocketfd.setblocking(False)
receiveSocketfd.bind(('127.0.0.1', PORTHOME))
receiveSocketfd.listen(NUMROOMS)
selector.register(receiveSocketfd, selectors.EVENT_READ, acceptSocket)

#setValues("ip", "192.168.50.173")

while True:
    choice = ""
    print("Type \'help\' for more options")
    while True:
        events = selector.select(0)
        for key in events:
            callback = key[0].data
            callback(receiveSocketfd)

        if kbhit():
            char = getch()
            c = ord(char)
            if c != 13 and c != 8:
                try:
                    choice += char.decode()
                    sys.stdout.write(char.decode())
                    sys.stdout.flush()
                except:
                    continue
            elif c == 8 and len(choice) > 0:
                choice = choice[:len(choice)-1]
                #print("\b ",end='')
                sys.stdout.write("\b \b")
                sys.stdout.flush()

            else:
                break

    #choice = input("Type \'help\' for more options\n>")

    #print("\n%s\n"%choice)
    
    if choice == "":
        continue

    parsedInput = parseInput(choice)
    #print("TESTING : ", parsedInput)

    if parsedInput[0].upper() == "HELP":
    #    os.system('cls')
        help(parsedInput)

    elif parsedInput[0].upper() == "EXIT":
    #    os.system('cls')
        print("\nCredit : Andrew DeRose\nThanks!\n")
        exit()
        
    elif parsedInput[0].upper() == "SENDMSG":
    #   os.system('cls')
        if len(parsedInput) > 2:
            sendmsg(parsedInput[1], parsedInput[2])
        elif len(parsedInput) == 2:
            sendmsg(parsedInput[1])
        else:
            print("\nERROR : Please attach a message!\n")

    elif parsedInput[0].upper() == "CONFIG":
    #   os.system('cls')
        config()
        
    else:
        print("\nUnrecognized command : \"%s\"\n" %choice)
