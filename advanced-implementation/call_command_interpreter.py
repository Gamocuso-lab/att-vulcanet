import cmd
import json
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ClientFactory
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet import reactor

class command_interpreter_client(Protocol, cmd.Cmd):

    prompt = ""

    def __init__(self, completekey = "tab", stdin = None, stdout = None):
        super().__init__(completekey, stdin, stdout)
        self.command = dict()
        reactor.callInThread(self.interpretor)

    #----/ call commands /----

    def do_call(self, call_id):
        self.set_command("call", call_id)
        self.sendData()
        
    def do_answer(self, operator_id):
        self.set_command("answer", operator_id)
        self.sendData()

    def do_reject(self, operator_id):
        self.set_command("reject", operator_id)
        self.sendData()

    def do_hangup(self, call_id):
        self.set_command("hangup", call_id)
        self.sendData()

    def set_command(self, command, id):
        self.command = {
            "command": command,
            "id": f"{id}"
        }

    def do_quit(self):
        return True
    
    #----/ protocol logic /----

    def dataReceived(self, data):
        data = json.loads(data.decode())
        print(data['response'])

    def sendData(self):
        self.transport.write(json.dumps(self.command).encode())

    def interpretor(self):
        self.cmdloop()


class command_interpreter_factory(ClientFactory):
    """A factory for command_interpreter_client.

    A new protocol instance will be created each time we connect to the server.
    """

    def buildProtocol(self, addr):
        p = command_interpreter_client()
        p.factory = self
        return p
    
    def clientConnectionLost(self, connector, reason):
        """If client disconnected, reconnect to server."""
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        print("connection failed:", reason)
        reactor.stop()
    
if __name__ == '__main__':
    endpoint = TCP4ClientEndpoint(reactor, 'localhost', 5678)
    endpoint.connect(command_interpreter_factory())
    reactor.run()