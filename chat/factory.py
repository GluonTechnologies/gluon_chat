from twisted.internet.interfaces import IAddress
from twisted.internet.protocol import Factory

from chat import GluonChat


class GluonChatFactory(Factory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr: IAddress):
        return GluonChat(self.users)
