# filePath = "vsftpd.log"

# Modules
from configparser import ConfigParser

# Configuration file
parser = ConfigParser()
parser.read('config.ini')

# Components for the cript
lstEvents = []
dicDownloadFailed = {}
dicDownloadFiles = {}
dicMissingFiles = {}
dicClients = {}


# Eventclass
class Event(object):
    def __init__(self, id, date, pid, client):
        self.id = id
        self.date = date
        self.pid = pid
        self.client = client

    def connect(self, mode):
        self.mode = mode

    def anonLogin(self, mode, user, status, password):
        self.mode = mode
        self.user = user
        self.status = status
        self.password = password

    def login(self, mode, user, status):
        self.mode = mode
        self.user = user
        self.status = status

    def directory(self, mode, user, status, path):
        self.mode = mode
        self.user = user
        self.status = status
        self.path = path

    def action(self, mode, user, status, path, size, speed):
        self.mode = mode
        self.user = user
        self.status = status
        self.path = path
        self.size = size
        self.speed = speed


# Function that reads the event log specified from the configuration file
def readFile():
    try:
        with open(parser.get('basic', 'path')) as file:
            eventLog = file.readlines()
            return eventLog
    except(FileNotFoundError):
        print("File not found! Please enter a valid file in the configuration file!")
        pause()
        exit(1)
    except:
        print("Something went wrong! Please contact your system administrator")
        pause()
        exit(99)


# Read every event from the configuration file and makes it a class
# Downloaded, missing and failed files are stored in a dictonairy
def readEvents():
    index = -1
    for event in readFile():
        index += 1
        try:
            event = event.split(' ')
            if event[0] != "\n":
                if event[2] == "":
                    del event[2]  # if date doesn't have 2 numbers
                date = ' '.join(event[0:5])
                pid = ' '.join(event[5:7])
                pid = pid[1:-1]
                # If event is a connection
                if event[7] == "CONNECT:":
                    mode = "connect"
                    client = event[9]
                    objEvent = Event(index, date, pid, client)
                    objEvent.connect(mode)
                    lstEvents.append(objEvent)
                    # return date + " || " +  pid + " || " +  mode + " || " +  client
                else:
                    user = event[7]
                    user = user[1:-1]
                    status = event[8]
                    mode = event[9]
                    client = event[11]
                    client = client[1:-2]

                    # Specify mode information
                    if mode == "LOGIN:":
                        mode = "login"
                        if user == "ftp":
                            password = event[14]
                            password = password[1:-2]
                            objEvent = Event(index, date, pid, client)
                            objEvent.anonLogin(mode, user, status, password)
                            lstEvents.append(objEvent)
                            # return date + " || " + pid + " || " + mode + " || " + client + " || " + user + " || " + status + " || " + mode + " || " + password
                        else:
                            objEvent = Event(index, date, pid, client)
                            objEvent.login(mode, user, status)
                            lstEvents.append(objEvent)
                            # return date + " || " +  pid + " || " +  mode + " || " +  client + " || " +  user + " || " +  status + " || " +  mode

                    elif mode == "MKDIR:":
                        mode = "mkdir"
                        path = ' '.join(event[12:])
                        objEvent = Event(index, date, pid, client)
                        objEvent.directory(mode, user, status, path)
                        lstEvents.append(objEvent)
                        # return date + " || " + pid + " || " + mode + " || " + client + " || " + user + " || " + status + " || " + mode + " || " + path
                    else:
                        positionPath = len(event) - 3
                        path = ''.join(event[12:positionPath])
                        path = path[1:-2]
                        mode = mode[0:-1]
                        speed = event[-1]
                        if path == "":
                            positionPath = len(event) - 1
                            path = ''.join(event[12:positionPath])
                            path = path[1:-2]
                            size = "unknown"
                            if dicMissingFiles.get(path):
                                missingTimes = dicMissingFiles[path] + 1
                                dicMissingFiles[path] = missingTimes
                            else:
                                dicMissingFiles[path] = 1
                        else:
                            size = ' '.join(event[-3:-1])
                            size = size[0:-7]
                        objEvent = Event(index, date, pid, client)
                        objEvent.action(mode, user, status, path, size, speed)
                        lstEvents.append(objEvent)
                        if status != "OK":
                            if dicDownloadFailed.get(path):
                                failedTimes = dicDownloadFailed[path] + 1
                                dicDownloadFailed[path] = failedTimes
                            else:
                                dicDownloadFailed[path] = 1
                        else:
                            checkDownload(path)
                            checkUserData(client, user, password, size)


        except:
            continue


# Options
# Create breake after action
def pause():
    print("")
    input("Press any key to continue . . .")


# Check of downloaddata exits
def checkDownload(path):
    if dicDownloadFiles.get(path):
        downloadTimes = dicDownloadFiles[path] + 1
        dicDownloadFiles[path] = downloadTimes
    else:
        dicDownloadFiles[path] = 1


# Check userdata and sum the bytes
def checkUserData(client, user, password, bytes):
    if dicClients.get(client):
        exitClient = (dicClients.get(client))
        exitBytes = exitClient['bytes']
        newBytes = int(exitBytes) + int(bytes)
        exitClient['bytes'] = newBytes
    else:
        dicClients[client] = {"user": user, "password": password, "bytes": bytes}


# Load every failed file from the dictonairy and sort them.
# Then the dictonairy is sorted desc and shows the top 10
def showFailed():
    print("-----------")
    print("Top 10 failed files")
    print("-----------")
    index = 0
    sortFailedFiles = sorted(dicDownloadFailed, key=dicDownloadFailed.get, reverse=True)
    for failedFile in sortFailedFiles:
        index += 1
        print(str(index) + ": " + failedFile + " " + str(dicDownloadFailed[failedFile]) + " times ")
        if index == 10:
            break
    pause()
    menu()


# Load every succesvol downloaded file from the dictonairy and sort them.
# Then the dictonairy is sorted desc and shows the top 10
def showDownloadTop():
    print("-----------")
    print("Top 10 downloaded files")
    print("-----------")
    index = 0
    sortDownloadFiles = sorted(dicDownloadFiles, key=dicDownloadFiles.get, reverse=True)
    for downloadFile in sortDownloadFiles:
        index += 1
        print(str(index) + ": " + downloadFile + " " + str(dicDownloadFiles[downloadFile]) + " times ")
        if index == 10:
            break
    pause()
    menu()


# Load every missing file from the dictonairy.
def showMissing():
    print("-----------")
    print("Missing Files")
    print("-----------")
    for missingFile in dicMissingFiles:
        print("- " + missingFile + " " + str(dicMissingFiles[missingFile]) + " times ")
    pause()
    menu()


# Load every missing file from the dictonairy.
def showClients():
    print("-----------")
    print("Show clients")
    print("-----------")
    for client in dicClients:
        clientData = dicClients[client]
        if clientData['user'] == "ftp":
            print(client + " logged in anonymously, anonymously logged in with password '" + clientData[
                'password'] + "', and downloaded totally " + str(clientData['bytes']) + " bytes ")
        else:
            print(client + " logged in as " + clientData['user'] + ", and downloaded totally " + str(
                clientData['bytes']) + " bytes ")
    pause()
    menu()


def menu():
    print("-----------")
    print("Menu")
    print("-----------")
    print("")
    print("1) Show missing files")
    print("2) Show top 10 downloaded files")
    print("3) Show connected users")
    print("4) Show top 10 failed files")
    print("")
    print("9) Quit")
    print("Make a choice")
    while True:
        try:
            inMenu = int(input("Choice: "))
            if inMenu == 1:
                showMissing()
            elif inMenu == 2:
                showDownloadTop()
            elif inMenu == 3:
                showClients()
            elif inMenu == 4:
                showFailed()
            elif inMenu == 9:
                exit(0)
            else:
                print("Try again")
                continue
        except ValueError:
            print("Try again")


def init():
    readEvents()
    menu()


init()
