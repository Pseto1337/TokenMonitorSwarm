import logging
import time
from decimal import Decimal
from datetime import datetime
from agents.base.agent import BaseAgent


class TypeValidationAgent(BaseAgent):
    """
    Specialized agent focused on deep type validation of transaction data.
    This agent ensures all data fields not only exist but contain valid,
    properly formatted values appropriate for their intended use.
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)

    def start(self):
        self.logger.info(f"[{self.name}] TypeValidationAgent starting.")
        while True:
            # Receive messages that passed integrity validation
            messages = self.message_bus.get_messages("IntegrityChannel")
            if messages:
                for msg in messages:
                    if self._validate_types(msg):
                        self.message_bus.send_message("TypeValidationChannel", msg)
            time.sleep(1)

    def _validate_types(self, transaction):
        """
        Performs detailed type validation on transaction fields.
        Each field is checked against its expected format and value range.
        """
        try:
            # Validate timestamp
            timestamp = transaction['timestamp']
            if isinstance(timestamp, str):
                try:
                    # Convert string timestamp to datetime
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    self.logger.warning(f"Invalid timestamp format: {timestamp}")
                    return False
            elif isinstance(timestamp, (int, float)):
                try:
                    # Check if timestamp is a valid epoch
                    datetime.fromtimestamp(timestamp)
                except ValueError:
                    self.logger.warning(f"Invalid timestamp value: {timestamp}")
                    return False

            # Validate token address
            if not self._is_valid_address(transaction['token_address']):
                return False

            # Validate transaction value
            if not self._is_valid_numeric(transaction['value']):
                return False

            return True

        except Exception as e:
            self.logger.error(f"Type validation failed: {e}")
            return False

    def _is_valid_address(self, address):
        """Validates cryptocurrency address format."""
        if not isinstance(address, str):
            self.logger.warning(f"Address must be string, got {type(address)}")
            return False

        # Basic address format validation
        if not address.startswith(('0x', 'sol:')):
            self.logger.warning(f"Invalid address format: {address}")
            return False

        # Check address length based on chain
        if address.startswith('0x') and len(address) != 42:
            self.logger.warning(f"Invalid Ethereum address length: {address}")
            return False

        return True

    def _is_valid_numeric(self, value):
        """Validates numeric values ensuring they're proper amounts."""
        if not isinstance(value, (int, float, Decimal)):
            self.logger.warning(f"Value must be numeric, got {type(value)}")
            return False

        # Ensure value is positive
        if value < 0:
            self.logger.warning(f"Value cannot be negative: {value}")
            return False

        return True