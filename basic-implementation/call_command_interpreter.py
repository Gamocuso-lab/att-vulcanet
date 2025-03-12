import cmd
from call_center_queue import Call_center

class Call_command_interpreter(cmd.Cmd):
    prompt="(call-center)"

    def __init__(self, completekey = "tab", stdin = None, stdout = None):
        super().__init__(completekey, stdin, stdout)
        self.call_center = Call_center([])

    "----/ call commands /----"

    def do_call(self, call_id):
        self.call_center.call(call_id)

    def do_answer(self, operator_id):
        self.call_center.answer(operator_id)

    def do_reject(self, operator_id):
        self.call_center.reject(operator_id)

    def do_hangup(self, call_id):
        self.call_center.hangup(call_id)

    def do_quit(self):
        return True
    
if  __name__ == '__main__':
    Call_command_interpreter().cmdloop()