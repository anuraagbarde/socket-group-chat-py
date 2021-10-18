import socketserver
from datetime import datetime

class Message():
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message
        self.time = datetime.now()

class Group:
    def __init__(self, name):
        self.name = name
        self.users = []
        self.messages = []
    
    def add_user(self, user):
        self.users.append(user)
    
    def remove_user(self, user):
        self.users.remove(user)
    
    def add_message(self, sender, message):
        m = Message(sender, message)
        self.messages.append(m)
        self.publish(message, sender)
    
    def get_messages(self):
        return self.messages
    
    def get_users(self):
        return self.users
    
    def get_name(self):
        return self.name
    
    def get_user_names(self):
        return [user.get_name() for user in self.users]
    
    def get_user_by_name(self, name):
        for user in self.users:
            if user.get_name() == name:
                return user
        return None
    
    def publish(self, message, sender):
        for user in self.users:
            if user != sender:
                user.writer(message + "\r\n")
    
class GroupManager():
    def __init__(self):
        self.groups = dict() # {group_name: Group}

    def create_group(self, name):
        group = Group(name)
        self.add_group(group)
        return group
    
    def add_group(self, group):
        self.groups[group.get_name()] = group

    def get_group(self, name):
        return self.groups[name]

    def get_group_names(self):
        return self.groups.keys()

class ClientHandler(socketserver.StreamRequestHandler):

    def writer(self, msg):
        self.wfile.write(msg.encode('utf-8'))

    def reader(self):
        return self.rfile.readline().decode('utf-8').strip()

    def echo_msg(self, input):
        self.writer("You said:" + input[5:] + "\r\n")

    def quit_handler(self):
        self.writer("ok bye!\r\n")
        self.request.close()

    def join_group_handler(self, input):
        self.writer("Please enter the group name: ")
        group_name = self.reader()
        if group_name in self.server.group_manager.get_group_names():
            group = self.server.group_manager.get_group(group_name)
            group.add_user(self)
            self.active_group = group
            self.active_group.publish(f"{self.get_name()} as entered the chat", self)
            self.writer("You have joined the group " + group_name + "!\r\n")
            self.writer("Try the following commands:\r\n1. /send 2. /joingroup\r\n")
        else:
            self.writer("Group " + group_name + " does not exist!\r\nCreating new group and adding you to it!")
            self.active_group = self.server.group_manager.create_group(group_name)
            self.active_group.add_user(self)
            self.active_group.publish(f"{self.get_name()} as entered the chat", self)
            self.writer("You have joined the group " + group_name + "!\r\n")
            self.writer("Try the following commands:\r\n1. /send 2. /joingroup\r\n")

        self.writer("You have joined the group: " + group_name + "\r\n")

    def send_msg(self, input):
        if self.active_group is None:
            self.writer("You are not in a group!\r\n")
            return
        msg = input[5:]
        self.active_group.add_message(self, self.name + ": " + msg)
        self.writer("Message sent!\r\n")

    def input_handler(self):
        while True:
            input = self.reader()
            if input == "ping":
                self.writer("pong\r\n")
            elif input.startswith("/echo"):
                self.echo_msg(input)
            elif input == "/quit":
                self.quit_handler()
                break
            elif input.startswith("/joingroup"):
                self.join_group_handler(input)
            elif input.startswith("/send"):
                self.send_msg(input)
            else:
                self.writer("Unknown command!\r\n")
    
    def identify(self):
        self.writer("Welcome to the the chat server!\r\n")
        self.writer("Please enter your name: ")
        name = self.reader()
        self.set_name(name)
        self.writer("Hello, " + self.get_name() + "!\r\n")
        self.writer("Try the following commands:\r\n1. ping\r\n2. /echo\r\n3. /quit \r\n4. /joingroup\r\n5. /send")

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def handle(self):
        self.identify()
        self.input_handler()


class ChatServer():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start_forever(self):
        with socketserver.ThreadingTCPServer((str(self.host), self.port), ClientHandler) as server:
            server.group_manager = GroupManager()
            server.serve_forever()

if __name__ == '__main__':
    chat_server = ChatServer('localhost', 8000)
    chat_server.start_forever()