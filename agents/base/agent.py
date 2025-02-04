# agents/base/agent.py
import time

class BaseAgent:
    def __init__(self, name, message_bus):
        self.name = name
        self.message_bus = message_bus

    def start(self):
        print(f"[{self.name}] Agent starting.")
        # This is where the agent’s main loop would go.
        while True:
            self.process_messages()
            time.sleep(1)  # Pause for 1 second between cycles

    def process_messages(self):
        # Check for messages on the bus intended for this agent.
        messages = self.message_bus.get_messages(self.name)
        for msg in messages:
            print(f"[{self.name}] Received message: {msg}")
