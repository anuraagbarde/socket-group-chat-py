import socketserver
from view import ClientHandler
from model import GroupManager

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