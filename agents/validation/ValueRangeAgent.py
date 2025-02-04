import logging
import time
from decimal import Decimal
from datetime import datetime, timedelta
from agents.base.agent import BaseAgent


class ValueRangeAgent(BaseAgent):
    """
    Specialized agent that validates if transaction values fall within
    expected ranges and patterns. This helps identify unusual or potentially
    problematic transactions early in the processing pipeline.
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)
        # Define baseline thresholds for different validation checks
        self.thresholds = {
            'min_transaction_value': 0.000001,  # Minimum meaningful transaction
            'max_transaction_value': 1000000000,  # Upper limit for single transaction
            'max_time_future': 300,  # Maximum seconds into future for timestamps
            'max_time_past': 86400,  # Maximum seconds into past (24 hours)
        }

    def start(self):
        self.logger.info(f"[{self.name}] ValueRangeAgent starting.")
        while True:
            # Get messages that passed type validation
            messages = self.message_bus.get_messages("TypeValidationChannel")
            if messages:
                for msg in messages:
                    if self._validate_ranges(msg):
                        self.message_bus.send_message("RangeValidationChannel", msg)
            time.sleep(1)

    def _validate_ranges(self, transaction):
        """
        Checks if transaction values fall within acceptable ranges.
        """
        try:
            # Validate transaction value range
            if not self._check_value_range(transaction['value']):
                return False

            # Validate timestamp is within reasonable range
            if not self._check_timestamp_range(transaction['timestamp']):
                return False

            # Add any additional range checks specific to your needs

            return True

        except Exception as e:
            self.logger.error(f"Range validation failed: {e}")
            return False

    def _check_value_range(self, value: float) -> bool:
        """
        Validates if a transaction value falls within acceptable ranges.
        Helps catch unusually small or large transactions that might indicate
        issues or require special handling.
        """
        try:
            if value < self.thresholds['min_transaction_value']:
                self.logger.warning(f"Transaction value too small: {value}")
                return False

            if value > self.thresholds['max_transaction_value']:
                self.logger.warning(f"Transaction value too large: {value}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Value range check failed: {e}")
            return False

    def _check_timestamp_range(self, timestamp) -> bool:
        """
        Validates if a timestamp is within a reasonable range.
        Prevents processing of transactions too far in the past or future.
        """
        try:
            # Convert timestamp to datetime if it's numeric
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

            current_time = datetime.now()

            # Check if timestamp is too far in the future
            if timestamp > current_time + timedelta(seconds=self.thresholds['max_time_future']):
                self.logger.warning(f"Timestamp too far in future: {timestamp}")
                return False

            # Check if timestamp is too far in the past
            if timestamp < current_time - timedelta(seconds=self.thresholds['max_time_past']):
                self.logger.warning(f"Timestamp too far in past: {timestamp}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Timestamp range check failed: {e}")
            return False