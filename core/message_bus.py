# core/message_bus.py

class MessageBus:
    def __init__(self):
        # Each channel is just a dictionary where keys are agent names and values are lists of messages.
        self.channels = {}

    def register_agent(self, agent_name):
        if agent_name not in self.channels:
            self.channels[agent_name] = []
            print(f"MessageBus: Registered agent '{agent_name}'.")

    def send_message(self, recipient, message):
        if recipient in self.channels:
            self.channels[recipient].append(message)
        else:
            print(f"MessageBus: Agent '{recipient}' not registered.")

    def get_messages(self, agent_name):
        # Retrieve and clear messages for the agent.
        messages = self.channels.get(agent_name, [])
        self.channels[agent_name] = []
        return messages
