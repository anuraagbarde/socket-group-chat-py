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
