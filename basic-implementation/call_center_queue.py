class call_center():

    def __init__(self, queue):
        self.__queue = queue
        self.__operators = [operator("A", None, "available"), operator("B", None, "available")]

    def add_to_queue(self, call_id):
        """ Add a new call_id to the queue"""
        self.__queue.append(call_id)

    def find_operator(self, op_id):
        """ Find the operator by id """
        for op in self.__operators:
            if op.get_id() == op_id:
                return op
    
    def verify_queue(self):
        """ 
        Verifies if the queue has a pending call and find an anvailable operator
            * Return 0 if there is a pending call but no operator available 
            * Return 1 if there is a pending call and an operator is available
            * Retorn 2 if there is no pending call
        """
        if len(self.__queue) > 0:
            for op in self.__operators:
                if op.get_status() == "available":
                    op.set_status("ringing")
                    op.set_call_id(self.__queue.pop(0))
                    print(f"Call {op.get_call_id()} ringing for operator {op.get_id()}")
                    return 1
            return 0
        return 2

    def call(self, call_id):
        """
        Add the call_id to queue and verify if there is an operator available in "verify_queue"
        """
        print(f"Call {call_id} recived")
        self.add_to_queue(call_id)
        result = self.verify_queue()

        if result == 0:
            print(f"Call {call_id} waiting in queue")
    
    def answer(self, op_id):
        """
        Set the operator status to "busy" if its "ringing"
        """
        op = self.find_operator(op_id)

        if op.get_status() == "available":
            print(f"No calls for operator {op.get_id()}")

        elif op.get_status() == "busy":
            print(f"Operator {op.get_id()} is already in Call {op.get_call_id()}")

        else:
            op.set_status("busy")
            print(f"Call {op.get_call_id()} answered by operator {op.get_id()}")

        return
            
    
    def reject(self, op_id):
        """
        Reject the current operator call if his status is "ringing", removing his call_id value and modifying his status to "available" 
        """
        op = self.find_operator(op_id)

        if op.get_status() == "available":
            print(f"No calls for operator {op.get_id()}")

        elif op.get_status() == "busy":
            print(f"Operator {op.get_id()} can't reject a call in progress")

        else:
            op.set_status("available")
            print(f"Call {op.get_call_id()} rejected by operator {op.get_id()}")
            op.set_call_id(None)
            self.verify_queue()

    def hangup(self, call_id):
        """
        Finish a call:
            * if the call_id is in the queue, removes it from there
            * if the call is in progress, removes call_id from operator and sets his status to "available"
        """
        if call_id in self.__queue:
            print(f"Call {call_id} missed")
            i = self.__queue.index(call_id)
            self.__queue.pop(i)
        else:
            for op in self.__operators:
                if op.get_call_id() == call_id:
                    if op.get_status() == "ringing":
                        print(f"Call {call_id} missed")
                    else:
                        print(f"Call {op.get_call_id()} finished and operator {op.get_id()} available")
                    op.set_status("available")
                    op.set_call_id(None)
                    self.verify_queue()
                    break

class operator():

    def __init__(self, id, call_id, status):
        self.__id = id
        self.__call_id = call_id
        self.__status = status

    
    def get_id(self):
        """ Return operator id """
        return self.__id

    def set_status(self, status):
        """ Set operator status """
        self.__status = status

    def get_status(self):
        """ Return operator status """
        return self.__status
    
    def set_call_id(self, call_id):
        """ Set the call id the operator is on """
        self.__call_id = call_id

    def get_call_id(self):
        """ Return the call id the operator is on"""
        return self.__call_id
    


