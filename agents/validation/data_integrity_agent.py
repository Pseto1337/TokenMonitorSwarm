import logging
import time
from agents.base.agent import BaseAgent


class DataIntegrityAgent(BaseAgent):
    """
    Specialized agent that focuses solely on checking data structure integrity.
    Validates that all required fields are present and properly formatted.
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)

    def start(self):
        self.logger.info(f"[{self.name}] DataIntegrityAgent starting.")
        while True:
            messages = self.message_bus.get_messages("RawDataChannel")
            if messages:
                for msg in messages:
                    if self._check_data_integrity(msg):
                        self.message_bus.send_message("IntegrityChannel", msg)
            time.sleep(1)

    def _check_data_integrity(self, transaction):
        """Check if transaction data has all required fields with correct structure."""
        try:
            required_structure = {
                'timestamp': (str, int, float),  # Accepts multiple possible types
                'token_address': str,
                'value': (int, float),
                'transaction_hash': str
            }

            # Check all required fields exist and have correct type
            for field, expected_type in required_structure.items():
                if field not in transaction:
                    self.logger.warning(f"Missing required field: {field}")
                    return False

                if not isinstance(transaction[field], expected_type):
                    self.logger.warning(
                        f"Invalid type for {field}: expected {expected_type}, got {type(transaction[field])}")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Data integrity check failed: {e}")
            return False