from twisted.internet.protocol import connectionDone, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import failure
from enum import Enum

STATE = Enum('STATE', ['WELCOME', 'CHOOSE', 'CHAT'])


class GluonChat(LineReceiver):
    def __init__(self, users):
        self.users = users
        self.name = None
        self.peer = None
        self.state = STATE.WELCOME

    def connectionMade(self):
        self.setLineMode()
        self.sendLine(b"Welcome to Gluon-Chat!\nWhat is your name? ")

    def connectionLost(self, reason: failure.Failure = connectionDone):
        if self.name in self.users:
            del self.users[self.name]

    def rawDataReceived(self, data):
        print("Raw Data", data, str(data))
        pass

    def lineReceived(self, line):
        line_str = str(line.decode())
        if self.state is STATE.WELCOME:
            if line_str.isalpha():
                if line_str in self.users:
                    self.sendLine(b"Whoops! name already taken, please choose another name")
                    return
                if len(line_str) < 3:
                    self.sendLine(b"Whoops! invalid name, your name should have at least 3 chars")
                    return
                self.name = line_str
                self.users[self.name] = self
                self.state = STATE.CHOOSE
                peers = [peer for peer in list(self.users.keys()) if peer is not self.name]
                if len(peers) == 0:
                    self.sendLine(b"** 0 peers in the room **")
                elif len(peers) == 1:
                    message = "You can chat with the following peers"
                    self.sendLine(message.encode())
                    self.sendLine(b"--------------------------")
                    for peer in peers:
                        message = "<%s>" % peer
                        self.sendLine(message.encode())
                else:
                    peers.append("All")
                    message = "You can chat with the following peers"
                    self.sendLine(message.encode())
                    for peer in peers:
                        message = "<%s>" % peer
                        self.sendLine(message.encode())
            else:
                self.sendLine(b"Please type your name")
        elif self.state is STATE.CHOOSE:
            peers = [peer for peer in list(self.users.keys()) if peer is not self.name]
            if line_str in peers:
                self.peer = self.users[line_str]
                self.state = STATE.CHAT
                message = "*************<%s>**************" % line_str
                self.sendLine(message.encode())
            elif str(line_str).lower() == "all":
                self.peer = "ALL"
                self.state = STATE.CHAT
                self.sendLine(b"************<ALL>***************")
            else:
                if line_str == ".":
                    self.sendLine(b"xxxxxxxxxxxxxxxxxxxxxxxxx")
                    peers = [peer for peer in list(self.users.keys()) if peer is not self.name]
                    peers.append("All")
                    self.state = STATE.CHOOSE
                    message = "You can chat with the following peers"
                    self.sendLine(message.encode())
                    for peer in peers:
                        message = "<%s>" % peer
                        self.sendLine(message.encode())
                else:
                    self.sendLine(b"Whoops! unable to find your peer!")
                    peers = [peer for peer in list(self.users.keys()) if peer is not self.name]
                    peers.append("All")
                    self.state = STATE.CHOOSE
                    message = "You can chat with the following peers"
                    self.sendLine(message.encode())
                    for peer in peers:
                        message = "<%s>" % peer
                        self.sendLine(message.encode())
        elif self.state is STATE.CHAT:
            if line_str == ".":
                self.sendLine(b"xxxxxxxxxxxxxxxxxxxxxxxxx")
                peers = [peer for peer in list(self.users.keys()) if peer is not self.name]
                peers.append("All")
                self.state = STATE.CHOOSE
                message = "You can chat with the following peers"
                self.sendLine(message.encode())
                for peer in peers:
                    message = "<%s>" % peer
                    self.sendLine(message.encode())
            else:
                if self.peer == "ALL":
                    message = "<%s> %s" % (self.name, line_str)
                    for name, protocol in self.users.items():
                        if protocol != self:
                            protocol.sendLine(message.encode())
                else:
                    message = "<*%s> %s" % (self.name, line_str)
                    self.peer.sendLine(message.encode())
