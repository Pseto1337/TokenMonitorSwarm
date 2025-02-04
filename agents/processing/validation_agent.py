import logging
import time
from agents.base.agent import BaseAgent


class DataValidationAgent(BaseAgent):
    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)

    def start(self):
        self.logger.info(f"[{self.name}] DataValidationAgent starting.")
        while True:
            # Get messages from RawDataChannel
            messages = self.message_bus.get_messages("RawDataChannel")
            if messages:
                for msg in messages:
                    if self._validate_transaction(msg):
                        self.message_bus.send_message("ValidationChannel", msg)
            time.sleep(1)

    def _validate_transaction(self, transaction):
        try:
            # Basic validation checks
            required_fields = ['timestamp', 'value', 'token_address']
            return all(field in transaction for field in required_fields)
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False