import json
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet.protocol import Protocol 
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import TCP4ServerEndpoint

class Call_center():
    """
    Call_center is a class that composes the logic about call operations in a call center that have operators and a waiting queue
    """

    def __init__(self, queue):
        self.__queue = queue
        self.__operators = [Operator("A", None, "available", dict()), Operator("B", None, "available", dict())]

    def add_to_queue(self, call_id):
        """ Add a new call_id to the queue"""
        self.__queue.append(call_id)

    def find_operator(self, op_id):
        """ Find the operator by id """
        for op in self.__operators:
            if op.get_op_id() == op_id:
                return op
            
    def set_operator_call(self, operator, call_id):
        """
        Set the current operator call, changing the operator status to "ringing" 
        """
        operator.set_status("ringing")
        operator.set_call_id(call_id)
        return {
            "action": "ringing",
            "call_id": call_id,
            "operator_id": operator.get_op_id()
        } # f"Call {call_id} ringing for operator {operator.get_op_id()}"
    
    def verify_queue(self):
        """ 
        Verify if the queue has a pending call and find an anvailable operator whose call_id has the lowest rejection among the others operators 
            * Return 0 if there is a pending call but no operator available 
            * Return 1 if there is a pending call and an operator is available with lowest rejection for the call_id, furthermore sets the call to operator
            * Return 2 if there is no pending call

        -> when there is more than one operator available (like A, B and C), if A recives a call and reject it, the call will be redirected to B witch has the lowest rejection on that call, ensuring that call will be answered.
        """

        if len(self.__queue) > 0:

            min_rejections = None
            min_rejections_op = None
            call_id = self.__queue[0]

            for op in self.__operators:
                if op.get_status() == "available":
                    call_rejections = op.get_rejections(call_id)
                    if call_rejections == 0:
                        return self.set_operator_call(op, self.__queue.pop(0))
                    elif min_rejections == None:
                        min_rejections = call_rejections
                        min_rejections_op = op
                    elif min_rejections > call_rejections:
                        min_rejections = call_rejections
                        min_rejections_op = op

            if min_rejections != None:
                return self.set_operator_call(min_rejections_op, self.__queue.pop(0))
            return 0
        return 2

    def call(self, call_id):
        """
        Add the call_id to queue and verify if there is an operator available in "verify_queue"

        return: reponses = [f"Call {call_id} recived", f"{message}"]

        message can be:
            -> f"Call {call_id} ringing for operator {operator_id}"
            -> f"Call {call_id} waiting in queue"
        """

        responses = []
        responses.append({
                "action": "recived",
                "call_id": call_id
            })  #f"Call {call_id} recived"
        
        self.add_to_queue(call_id)
        result = self.verify_queue()

        if result == 0:
            responses.append({
                "action": "waiting",
                "call_id": call_id
            }) # f"Call {call_id} waiting in queue"
        else:
            responses.append(result)
        
        return responses
    
    def answer(self, op_id):
        """
        Set the operator status to "busy" if its "ringing"

        return: responses = [f"{message}"]

        message can be: 
            -> f"No calls for operator {operator_id}"
            -> f"Operator {operator_id} is already in Call {call_id}"
            -> f"Call {call_id} answered by operator {operator_id}"
        """
        response = []
        op = self.find_operator(op_id)

        if op.get_status() == "available":
            response.append({
                "action": "no_calls",
                "operator_id": op.get_op_id()
            }) #f"No calls for operator {op.get_op_id()}"

        elif op.get_status() == "busy":
            response.append({
                "action": "in_call",
                "operator_id": op.get_op_id()
            }) #f"Operator {op.get_op_id()} is already in Call {op.get_call_id()}"

        else:
            op.set_status("busy")
            response.append({
                "action": "answered",
                "operator_id": op.get_op_id(),
                "call_id": op.get_call_id()
            }) # f"Call {op.get_call_id()} answered by operator {op.get_op_id()}"

        return response
            
    
    def reject(self, op_id):
        """
        Reject the current operator call if his status is "ringing", removing his call_id value, modifying his status to "available" and adding 1 into rejections dictionary for this call_id (the higher this value, the lower is the priority)

        return: response = [f"{message}"]

        message can be:
            if the operator is "available"
            -> f"No calls for operator {operator_id}"

            if the operator is already "busy"
            -> f"Operator {operator_id} can't reject a call in progress"

            if the operator is "ringing"
            -> f"Call {call_id} rejected by operator {operator_id}"
        """
        response = []
        op = self.find_operator(op_id)

        if op.get_status() == "available":
            response.append({
                "action": "no_calls",
                "operator_id": op.get_op_id(),  
            }) # f"No calls for operator {op.get_op_id()}"

        elif op.get_status() == "busy":
            response.append({
            "action": "in_call",
            "operator_id": op.get_op_id(),
            "call_id": op.get_call_id()
        }) # f"Operator {op.get_op_id()} can't reject a call in progress"

        else:
            response.append({
                "action": "reject",
                "operator_id": op.get_op_id(),
                "call_id": op.get_call_id()
            }) # f"Call {op.get_call_id()} rejected by operator {op.get_op_id()}"
            self.add_to_queue(op.get_call_id())
            op.set_status("available")
            op.add_rejection(op.get_call_id())
            op.set_call_id(None)
            result = self.verify_queue()
            response.append(result)
        
        return response

    def hangup(self, call_id):
        """
        Finish a call:
            * if the call_id is in the queue, removes it from there
            * if the call is in progress, removes call_id from operator and sets his status to "available"

        return: response = [f"{message_1}", f"{message_2}"]

        message_1 can be:
            if the call is ringing or waiting:
            -> f"Call {call_id} missed"

            if the call was answered 
            -> f"Call {call_id} finished and operator {operator_id} available"

        message_2 can be:
            if there is another call pending:
            -> f"Call {call_id} ringing for operator {operator_id}" 

            if ther is not another call pending:
            -> None
        """
        response = []

        if call_id in self.__queue:
            response.append({
                "action": "missed",
                "call_id": op.get_call_id()
            }) # f"Call {call_id} missed"
            
            i = self.__queue.index(call_id)
            self.__queue.pop(i)
        else:
            for op in self.__operators:
                if op.get_call_id() == call_id:
                    if op.get_status() == "ringing":
                        response.append({
                            "action": "missed",
                            "call_id": op.get_call_id()
                        }) # f"Call {call_id} missed"
                    else:
                        response.append({
                            "action": "finished",
                            "operator_id": op.get_op_id(),
                            "call_id": op.get_call_id()
                        }) # f"Call {call_id} finished and operator {op.get_op_id()} available"
                    op.set_status("available")
                    op.set_call_id(None)
                    result = self.verify_queue()

                    if result != 0 and result != 2:
                        response.append(result)
                
                    break
        return response
    
    def verify_ignored(self, call_id, operator_id):

        print("called")
        responses = []
        op = self.find_operator(operator_id)

        if op.get_call_id() == call_id and op.get_status() == "ringing":
            
            responses.append({
                "action": "ignored",
                "operator_id": op.get_op_id(),
                "call_id": op.get_call_id()
            }) # f"Call {call_id} ignored by operator {operator_id}"

            op.set_call_id(None)
            op.set_status("available")
            result = self.verify_queue()
            if result != 2 and result != 0:
                responses.append(result)

            return responses

class Operator():
    """"""

    def __init__(self, op_id, call_id, status, rejections):
        self.__op_id = op_id
        self.__call_id = call_id
        self.__status = status
        self.__rejections = rejections

    
    def get_op_id(self):
        """ Return operator id """
        return self.__op_id

    def set_status(self, status):
        """ Set operator status """
        self.__status = status

    def get_status(self):
        """Return  operator status """
        return self.__status
    
    def set_call_id(self, call_id):
        """ Set the call id the operator is on """
        self.__call_id = call_id

    def get_call_id(self):
        """ Return the call id the operator is on"""
        return self.__call_id
    
    def add_rejection(self, call_id):
        if call_id in self.__rejections:
            self.__rejections[f'{call_id}'] += 1
        else:
            self.__rejections[f'{call_id}'] = 1

    def get_rejections(self, call_id):
        if call_id in self.__rejections:
            return self.__rejections[f'{call_id}']
        else:
            return 0
    
class call_center_server(Protocol):

    def connectionMade(self):
        self.call_center = Call_center([])

    def dataReceived(self, data):
        data = json.loads(data.decode())
        command = data["command"]
        id = data["id"]
        responses = []

        if command == "call":
            responses = self.call_center.call(id)
        elif command == "answer":
            responses = self.call_center.answer(id)
        elif command == "reject":
            responses = self.call_center.reject(id)
        elif command == "hangup":
            responses = self.call_center.hangup(id)

        resp = self.generate_response(responses)
        self.sendResponse(resp)

    def sendResponse(self, data):
        print(data)
        self.transport.write(json.dumps(data).encode())

    def generate_response(self, responses):
        resp = []
        for obj in responses:
            action = obj["action"]

            if action == "recived":
                resp.append(f"Call {obj['call_id']} recived")
            elif action == "ringing":
                resp.append(f"Call {obj['call_id']} ringing for operator {obj['operator_id']}")
                self.time_out(obj['call_id'], obj['operator_id'])
            elif action == "waiting":
                resp.append(f"Call {obj['call_id']} waiting in queue")
            elif action == "reject":
                resp.append(f"Call {obj['call_id']} rejected by operator {obj['operator_id']}")
            elif action == "answered":
                resp.append(f"Call {obj['call_id']} answered by operator {obj['operator_id']}")
            elif action == "missed":
                resp.append(f"Call {obj['call_id']} missed")
            elif action == "finished":
                resp.append(f"Call {obj['call_id']} finished and operator {obj['operator_id']} available")
            elif action == "no_calls":
                resp.append(f"No calls for operator {obj['operator_id']}")
            elif action == "in_call":
                resp.append(f"Operator {obj['operator_id']} is already in Call {obj['call_id']}")
            elif action == "ignored":
                resp.append(f"Call {obj['call_id']} ignored by operator {obj['operator_id']}")

        return {"response": "\n".join(resp)}

    def time_out(self, call_id, operator_id):
        
        d = task.deferLater(reactor, 10, self.call_center.verify_ignored, call_id, operator_id)

        d.addCallback(self.ignored_result)

    def ignored_result(self, result):
        print(result)
        response = self.generate_response(result)
        self.sendResponse(response)

class call_center_factory(ServerFactory):

    def buildProtocol(self, addr):
        return call_center_server()


if __name__ == '__main__':
    endpoint = TCP4ServerEndpoint(reactor, 5678)
    endpoint.listen(call_center_factory())
    reactor.run()

