class Call_center():

    def __init__(self, queue):
        self.__queue = queue
        self.__operators = [Operator("A", None, "available", dict()), Operator("B", None, "available", dict())]

    def add_to_queue(self, call_id):
        """ Add a new call_id to the queue"""
        self.__queue.append(call_id)

    def find_operator(self, op_id):
        """ Finds the operator by id """
        for op in self.__operators:
            if op.get_op_id() == op_id:
                return op
            
    def set_operator_call(self, operator, call_id):
        """
        Sets the current operator call, changing the operator status to "ringing" 
        """
        operator.set_status("ringing")
        operator.set_call_id(call_id)
        print(f"Call {call_id} ringing for operator {operator.get_op_id()}")
    
    def verify_queue(self):
        """ 
        Verifies if the queue has a pending call and find an anvailable operator
            * Return 0 if there is a pending call but no operator available 
            * Return 1 if there is a pending call and an operator is available, furthermore sets the call to operator
            * Return 2 if there is no pending call
        """

        min_priority = None
        min_priority_op = None
        call_id = self.__queue[0]

        if len(self.__queue) > 0:
            for op in self.__operators:
                if op.get_status() == "available":
                    call_priority = op.get_priority(call_id)
                    if call_priority == 0:
                        self.set_operator_call(op, self.__queue.pop(0))
                        return 1
                    elif min_priority == None:
                        min_priority = call_priority
                        min_priority_op = op
                    elif min_priority > call_priority:
                        min_priority = call_priority
                        min_priority_op = op

            if min_priority != None:
                self.set_operator_call(min_priority_op, self.__queue.pop(0))
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
        Sets the operator status to "busy" if its "ringing"
        """
        op = self.find_operator(op_id)

        if op.get_status() == "available":
            print(f"No calls for operator {op.get_op_id()}")

        elif op.get_status() == "busy":
            print(f"Operator {op.get_op_id()} is already in Call {op.get_call_id()}")

        else:
            op.set_status("busy")
            print(f"Call {op.get_call_id()} answered by operator {op.get_op_id()}")

        return
            
    
    def reject(self, op_id):
        """
        Rejects the current operator call if his status is "ringing", removing his call_id value and modifying his status to "available" 
        """
        op = self.find_operator(op_id)

        if op.get_status() == "available":
            print(f"No calls for operator {op.get_op_id()}")

        elif op.get_status() == "busy":
            print(f"Operator {op.get_op_id()} can't reject a call in progress")

        else:
            print(f"Call {op.get_call_id()} rejected by operator {op.get_op_id()}")
            self.add_to_queue(op.get_call_id())
            op.set_status("available")
            op.add_priority(op.get_call_id())
            op.set_call_id(None)
            self.verify_queue()

    def hangup(self, call_id):
        """
        Finishes a call:
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
                        print(f"Call {op.get_call_id()} finished and operator {op.get_op_id()} available")
                    op.set_status("available")
                    op.set_call_id(None)
                    self.verify_queue()
                    break

class Operator():
    """"""

    def __init__(self, op_id, call_id, status, priority):
        self.__op_id = op_id
        self.__call_id = call_id
        self.__status = status
        self.__priority = priority

    
    def get_op_id(self):
        """ Returns operator id """
        return self.__op_id

    def set_status(self, status):
        """ Sets operator status """
        self.__status = status

    def get_status(self):
        """ Returns operator status """
        return self.__status
    
    def set_call_id(self, call_id):
        """ 
        Sets the call id the operator is on 
        """
        self.__call_id = call_id

    def get_call_id(self):
        """ Returns the call id the operator is on"""
        return self.__call_id
    
    def add_priority(self, call_id):
        if call_id in self.__priority:
            self.__priority[f'{call_id}'] += 1
        else:
            self.__priority[f'{call_id}'] = 1

    def get_priority(self, call_id):
        if call_id in self.__priority:
            return self.__priority[f'{call_id}']
        else:
            return 0
    


