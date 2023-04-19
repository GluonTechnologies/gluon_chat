from twisted.internet import reactor

from chat import GluonChatFactory

reactor.listenTCP(5000, GluonChatFactory())
reactor.run()