# agents/collection/websocket_agent.py
import time
import random
import json
from agents.base.agent import BaseAgent


class WebSocketAgent(BaseAgent):
    def start(self):
        print(f"[{self.name}] WebSocket Agent starting.")
        # Simulate receiving real-time token data
        while True:
            # Create a simulated token transaction message
            message_data = {
                "token": "ABC",
                "price": round(random.uniform(0.5, 2.0), 2),
                "volume": random.randint(100, 1000),
                "timestamp": time.time()
            }
            # Convert the data to a JSON string (mimicking raw WebSocket messages)
            message_json = json.dumps(message_data)
            print(f"[{self.name}] Received data: {message_json}")

            # Send the message to the Data Processor Agent via the message bus
            self.message_bus.send_message("DataProcessor", message_json)

            # Wait a bit before simulating the next message
            time.sleep(2)
