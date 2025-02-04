# main.py
import threading
import time
import sys
import asyncio

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from core.config import settings
from core.logging_setup import setup_logging
from core.message_bus import MessageBus
from agents.collection.cielo_agent import CieloAgent
from agents.analysis.data_processing_agent import DataProcessingAgent


def main():
    # Set up logging
    setup_logging(settings.LOG_LEVEL)

    # Initialize the message bus
    bus = MessageBus()

    # Register agents with the message bus
    bus.register_agent("WebSocketAgent")
    bus.register_agent("CieloAgent")
    bus.register_agent("AlertAgent")
    bus.register_agent("RawDataChannel")
    bus.register_agent("ProcessedDataChannel")

    # Instantiate the agents
    cielo_agent = CieloAgent(name="CieloAgent", message_bus=bus)

    data_processor = DataProcessingAgent(name="DataProcessingAgent", message_bus=bus)
    data_processor_thread = threading.Thread(target=data_processor.start, daemon=True)
    data_processor_thread.start()


    # Start each agent in its own thread
    cielo_thread = threading.Thread(target=cielo_agent.start, daemon=True)


    cielo_thread.start()

    # Keep the main thread alive indefinitely
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
