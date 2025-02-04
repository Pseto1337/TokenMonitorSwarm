# agents/analysis/data_processing_agent.py
import json
import time
import logging
from datetime import datetime
from agents.base.agent import BaseAgent

logger = logging.getLogger("DataProcessingAgent")


class DataProcessingAgent(BaseAgent):
    """
    This agent subscribes to the "RawDataChannel" on the message bus.
    It accumulates raw transaction data, sorts them by timestamp, and
    publishes the sorted list to the "ProcessedDataChannel" on the message bus.
    This organized list can then be used by other agents (e.g., pattern analysis).
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.raw_transactions = []  # Internal storage for raw transactions

    def start(self):
        logger.info(f"[{self.name}] DataProcessingAgent starting.")
        while True:
            # Retrieve raw messages from the RawDataChannel
            messages = self.message_bus.get_messages("RawDataChannel")
            if messages:
                for msg in messages:
                    try:
                        # Convert the JSON string to a Python dictionary
                        transaction = json.loads(msg)
                        self.raw_transactions.append(transaction)
                    except Exception as e:
                        logger.error(f"Error parsing raw message: {e}", exc_info=True)

                # Sort the internal list by the "timestamp" field
                try:
                    # Assumes each transaction dict has a "timestamp" field (as a numeric epoch)
                    self.raw_transactions.sort(key=lambda tx: tx.get("timestamp", 0))
                    logger.info(f"Accumulated and sorted {len(self.raw_transactions)} transactions by timestamp.")
                except Exception as e:
                    logger.error(f"Error sorting transactions: {e}", exc_info=True)

                # Publish the sorted list to the ProcessedDataChannel
                try:
                    sorted_data = json.dumps(self.raw_transactions)
                    self.message_bus.send_message("ProcessedDataChannel", sorted_data)
                    logger.info("Published sorted transaction data to ProcessedDataChannel.")
                except Exception as e:
                    logger.error(f"Error publishing processed data: {e}", exc_info=True)

            # Sleep for a few seconds before checking for more data
            time.sleep(5)
