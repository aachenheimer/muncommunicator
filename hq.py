from socket import *
from msvcrt import *
import selectors
import os
import json
import sys

selector = selectors.DefaultSelector()

PORTHOME = 7998 #opposite of clients
PORTHOST = 7999
NUMROOMS = 5
DEFAULTIP = '127.0.0.1'

roomsJSON = open("rooms.json", "r")
rooms = json.load(roomsJSON)
roomsJSON.close()

NUMROOMS = len(rooms.keys())

configJSON = open("configHost.json", "r")
config = json.load(configJSON)
configJSON.close()

PORTHOME = config["portHome"]
PORTHOST = config["portHost"]
DEFAULTIP = config["ip"]

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
            currentString = ""
            onMessage = True
            continue
        elif currentChar == "\"" and onMessage == True:
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

def acceptSocket(receiveSocket):
    incomingSocketfd, addr = receiveSocketfd.accept()
    print("\nAddress : %s\n"%addr[0])
    incomingSocketfd.setblocking(True)
    incomingMsg = (incomingSocketfd.recv(1024)).decode()
    print("\nReceived connection from %s!\n" %ipToRoom(addr[0]))
    if incomingMsg[0] != "%" and incomingMsg[0] != "@":
        print("Message : \"%s\""%incomingMsg)
    elif incomingMsg[0] == "@":
        print("Sending room data - \"%s\""%incomingMsg)
        sendRoomsFile(incomingSocketfd, addr[0])
    else:
        registerRoom(incomingMsg, addr[0])
    incomingSocketfd.close()
    
def registerRoom(data, ip):
    print("\nRegistering room data - \"%s\"\n"%data)
    parsedData = []
    currentString = ""
    for currentChar in data:
        if currentChar == "%":
            if currentString == "":
                continue
            parsedData.append(currentString)
            currentString = ""
        else:
            currentString += currentChar
    #print(parsedData)
    roomsJSON = open("rooms.json", "r")
    rooms = json.load(roomsJSON)
    roomsJSON.close()
    #parsedData[1] == room , parsedData[0] == name
    #print("\nparsedData[1] = %s\nparsedData[0] = %s\n"%(parsedData[1],parsedData[0]))
    rooms[parsedData[1]]["name"] = parsedData[0]
    rooms[parsedData[1]]["ip"] = ip

    roomsNew = json.dumps(rooms)
    roomsJSON = open("rooms.json", "w")
    roomsJSON.write(roomsNew)
    roomsJSON.close()

def sendRoomsFile(socketfd, ip):
    print("\nSending room data to %s...\n"%ipToRoom(ip))
    roomsJSON = open("rooms.json", "r")
    rooms = json.load(roomsJSON)
    roomsJSON.close()
    
    socketfd.send((json.dumps(rooms)).encode())

def roomToIP(room):
    if room not in rooms.keys():
        return "null"
    
    return rooms[room]["ip"]

def ipToRoom(ip):
    for room in rooms.keys():
         if rooms[room]["ip"] == ip:
              return room
    print("\nCould not find which room this is!\n")
    return "null"

def sendmsg(msg, room):
    ip = roomToIP(room.upper())
    if ip == "null":
        print("\nInvalid IP / Room!\n")
        return 1
    print("\n\nConnecting to room %s on IP %s" %(room, ip))
    sendSocketfd = socket(AF_INET, SOCK_STREAM)
    try:
        sendSocketfd.connect((ip, PORTHOST))
    except:
        print("\nERROR : Host refused!\n")
        return 1
    sendSocketfd.send(msg.encode())
    print("\nSent!\n")
    sendSocketfd.close()

def writeRoomsReadable():
    print()
    roomsJSON = open("rooms.json", "r")
    rooms = json.load(roomsJSON)
    for currentEntry in rooms.keys():
        print("%s - %s"%(currentEntry, rooms[currentEntry]["name"]))

receiveSocketfd = socket(AF_INET, SOCK_STREAM)
receiveSocketfd.setblocking(False)
receiveSocketfd.bind((DEFAULTIP, PORTHOME))
receiveSocketfd.listen(NUMROOMS)
selector.register(receiveSocketfd, selectors.EVENT_READ, acceptSocket)

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
    if choice == "":
        continue

    parsedInput = parseInput(choice)

    if parsedInput[0].upper() == "HELP":
         print("\nsendmsg *\"msg\" *room")
         print("This sends a message (wrapped in quotes) to the requested room")
         print("\nlist")
         print("This lists out all of the rooms and their respective names")
    elif parsedInput[0].upper() == "SENDMSG":
        if len(parsedInput) < 3:
            print("\nERROR : Not enough arguments!\n")
            continue
        sendmsg(parsedInput[1], parsedInput[2])
    elif parsedInput[0].upper() == "LIST":
        writeRoomsReadable()

    elif parsedInput[0].upper() == "EXIT":
        print("\nCredit : Andrew DeRose\nThanks!\n")
        exit()
    else:
        print("\nUnrecognized command : \"%s\"\n" %choice)










