# agents/analysis/volume_pattern_agent.py
import json
import time
import logging
from agents.base.agent import BaseAgent

logger = logging.getLogger("VolumePatternAgent")

class VolumePatternAgent(BaseAgent):
    """
    This agent listens on the 'ProcessedDataChannel', extracts volume data
    from the transaction list, and performs a basic volume analysis.
    """
    def start(self):
        logger.info(f"[{self.name}] VolumePatternAgent starting.")
        while True:
            # Retrieve processed data from the ProcessedDataChannel
            messages = self.message_bus.get_messages("ProcessedDataChannel")
            if messages:
                for msg in messages:
                    try:
                        # Assume the message is a JSON array of transaction dictionaries
                        transactions = json.loads(msg)
                        volumes = [tx.get("volume", 0) for tx in transactions]
                        total_volume = sum(volumes)
                        logger.info(f"[{self.name}] Total volume from {len(volumes)} transactions: {total_volume}.")
                        # Flag a pattern if the total volume exceeds an arbitrary threshold (adjust as needed)
                        if total_volume > 5000:
                            logger.info(f"[{self.name}] Potential high-volume pattern detected!")
                    except Exception as e:
                        logger.error(f"[{self.name}] Error processing volume data: {e}", exc_info=True)
            time.sleep(3)
