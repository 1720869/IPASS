# filePath = "vsftpd.log"

# Modules
from configparser import ConfigParser

# Configuration file
parser = ConfigParser()
parser.read('config.ini')

# Default variables
error = 0
errorMessage = ""

# Function for handleling errors
def checkError():
    global error
    global errorMessage

    if error == 1:
        errorMessage = "Bestand niet gevonden"
        return True
    else:
        return False

# Function that reads the event log specified in the configuration file
def readFile():
    global error
    try:
        with open(parser.get('basic', 'path')) as file:
            eventLog = file.readlines()
            eventLog = [x.strip() for x in eventLog]
            return eventLog
    except(FileNotFoundError):
        error = 1


def checkEventlog(eventLog):
    if checkError():
        print(errorMessage)
    else:
        event = {}
        for events in eventLog:
            # events = events.split(" ")
            event['datum'] = ' '.join(events[0:6])
            event['pid'] = ''.join(events[7])
            event['pid'] = event['pid'][0:len(event['pid'])-1]
            print(events)

checkEventlog(readFile())