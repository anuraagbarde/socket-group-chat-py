import socketserver

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
        self.writer("Try the following commands:\r\n1. ping\r\n2. /echo\r\n3. /quit \r\n4. /joingroup\r\n5. /send\r\n")

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def handle(self):
        self.identify()
        self.input_handler()