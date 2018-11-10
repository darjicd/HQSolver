import json
import requests
import sys
import urllib
from config import login_header, readFromConfig
from shutil import get_terminal_size

from autobahn.twisted.websocket import connectWS
from twisted.internet import reactor, ssl

from game import GameFactory
import ssl
# Used to fix an issue with urllib extraction #
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

class Launcher(object):
    def __init__(self):
        self.api_shows = readFromConfig("API", "shows_now")
        self.debug = readFromConfig("General", "debug_mode")
        self.server_ip = readFromConfig("General", "server_ip")

    def launchSolver(self):

        print(" HQ Solver ".center(get_terminal_size()[0], "="))

        if self.showAlive():
            socketURL = self.getSocketURL()

            proto = socketURL.split('://')[0]
            server = socketURL.split('://')[1].split("/")[0]
            server_dir = socketURL.replace(proto + '://' + server, "")

            if proto == "http":
                self.socketURL = "ws://" + server + ":80" + server_dir
            elif proto == "https":
                self.socketURL = "wss://" + server + ":443" + server_dir
            else:
                self.socketURL = socketURL

            factory = GameFactory(self.socketURL, headers=login_header)
            factory.setProtocolOptions(autoPingInterval=5, autoPingTimeout=5, autoPingSize=20)

            if factory.isSecure:
                contextFactory = ssl.ClientContextFactory()
            else:
                contextFactory = None

            connectWS(factory, contextFactory)
            reactor.run()
        else:
            print(''.center(get_terminal_size()[0], '='))
            sys.exit(0)

    def showAlive(self):
        """ Checks if show is live """

        request = requests.get(self.server_ip + self.api_shows, headers=login_header)
        main_url = "https://api-quiz.hype.space/shows/now?type="
        main_urldata = str(urllib.request.urlopen(main_url).read())
        main_urldata = main_urldata.replace("b'", "")
        main_urldata = main_urldata.replace("'", "")
        main_urldata = main_urldata.replace('\\n', '\n')
        responseJSON = json.loads(main_urldata)
        try:
            if responseJSON["active"]:
                print("Show is now live!".center(get_terminal_size()[0]))
                return True
            else:
                print("Show isn't live!".center(get_terminal_size()[0]))
                return False
        except:
            print ("Server response failed. Please visit https://api-quiz.hype.space/shows/now?type= to validate your connection.")

    def getSocketURL(self):

        main_url = "https://api-quiz.hype.space/shows/now?type="
        main_urldata = str(urllib.request.urlopen(main_url).read())
        main_urldata = main_urldata.replace("b'", "")
        main_urldata = main_urldata.replace("'", "")
        main_urldata = main_urldata.replace('\\n', '\n')
        responseJSON = json.loads(main_urldata)

        try:
            broadcastJSON = json.loads(main_urldata)["broadcast"]

            socketURL = broadcastJSON["socketUrl"]
            return socketURL
        except:
            return False


if __name__ == "__main__":
    Launcher().launchSolver()
