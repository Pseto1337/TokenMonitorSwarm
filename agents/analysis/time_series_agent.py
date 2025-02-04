# agents/analysis/time_series_agent.py
import json
import time
import logging
from agents.base.agent import BaseAgent

logger = logging.getLogger("TimeSeriesAgent")

class TimeSeriesAgent(BaseAgent):
    """
    This agent listens on the 'ProcessedDataChannel', extracts timestamps from
    the sorted transaction list, and performs a very basic time-series analysis.
    """
    def start(self):
        logger.info(f"[{self.name}] TimeSeriesAgent starting.")
        while True:
            # Retrieve processed data from the ProcessedDataChannel
            messages = self.message_bus.get_messages("ProcessedDataChannel")
            if messages:
                for msg in messages:
                    try:
                        # Assume the message is a JSON array of transaction dictionaries
                        transactions = json.loads(msg)
                        timestamps = [tx.get("timestamp", 0) for tx in transactions]
                        if timestamps:
                            first = min(timestamps)
                            last = max(timestamps)
                            interval = last - first
                            logger.info(f"[{self.name}] Processed {len(timestamps)} transactions over {interval:.2f} seconds.")
                            # For example, if many transactions occurred in a short interval, flag a pattern
                            if len(timestamps) > 10 and interval < 5:
                                logger.info(f"[{self.name}] Potential time-series pattern detected!")
                        else:
                            logger.info(f"[{self.name}] No timestamps found in transactions.")
                    except Exception as e:
                        logger.error(f"[{self.name}] Error processing time series data: {e}", exc_info=True)
            time.sleep(3)
