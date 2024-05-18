

class Messages:
    def __init__(self):
        self.system_messages = []
        self.new_messages = []
        self.user_messages = ["Hello"]

    def add_system(self, message):
        self.new_messages.append(message)

    def add_user(self, message):
        self.user_messages.append(message)

    def get_latest(self):
        output = []
        for message in self.new_messages:
            #self.system_messages.append(message)
            output.append(message)
        output = "\n".join(output)
        self.system_messages.append(output)
        self.new_messages = []

        return output

    def get_formatted(self):
        output = []
        for user, system in zip(self.user_messages, self.system_messages):
            output.append({"user": user, "assistant": system})

        return output
