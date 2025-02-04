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
from agents.processing.validation_agent import DataValidationAgent
from agents.validation.data_integrity_agent import DataIntegrityAgent
from agents.validation.type_validation_agent import TypeValidationAgent
from agents.validation.value_range_agent import ValueRangeAgent
from agents.patterns.wallet_behavior_agent import WalletBehaviorAgent
from agents.patterns.trading_volume_agent import TradingVolumeAgent
from agents.patterns.smart_position_agent import SmartPositionAgent



def main():
    # Set up logging
    setup_logging(settings.LOG_LEVEL)

    # Initialize the message bus
    bus = MessageBus()

    # Register agents with the message bus
    bus.register_agent("CieloAgent")
    bus.register_agent("AlertAgent")
    bus.register_agent("RawDataChannel")
    bus.register_agent("ProcessedDataChannel")
    bus.register_agent("ValidationChannel")
    bus.register_agent("DataValidationAgent")
    bus.register_agent("IntegrityChannel")
    bus.register_agent("TypeValidationChannel")
    bus.register_agent("RangeValidationChannel")
    bus.register_agent("PatternChannel")
    bus.register_agent("VolumePatternChannel")
    bus.register_agent("PositionPatternChannel")


    # Instantiate the agents
    cielo_agent = CieloAgent(name="CieloAgent", message_bus=bus)

    # Data processing and validation agents
    data_processor = DataProcessingAgent(name="DataProcessingAgent", message_bus=bus)
    data_validator = DataValidationAgent(name="DataValidationAgent", message_bus=bus)

    # Create threads for each agent
    cielo_thread = threading.Thread(target=cielo_agent.start, daemon=True)
    data_processor_thread = threading.Thread(target=data_processor.start, daemon=True)
    data_validator_thread = threading.Thread(target=data_validator.start, daemon=True)
    data_integrity_agent = DataIntegrityAgent(name="DataIntegrityAgent", message_bus=bus)
    data_integrity_thread = threading.Thread(target=data_integrity_agent.start, daemon=True)
    type_validator = TypeValidationAgent(name="TypeValidationAgent", message_bus=bus)
    type_validator_thread = threading.Thread(target=type_validator.start, daemon=True)
    value_range_validator = ValueRangeAgent(name="ValueRangeAgent", message_bus=bus)
    value_range_thread = threading.Thread(target=value_range_validator.start, daemon=True)
    wallet_behavior_agent = WalletBehaviorAgent(name="WalletBehaviorAgent", message_bus=bus)
    wallet_behavior_thread = threading.Thread(target=wallet_behavior_agent.start, daemon=True)
    volume_agent = TradingVolumeAgent(name="TradingVolumeAgent", message_bus=bus)
    volume_thread = threading.Thread(target=volume_agent.start, daemon=True)
    position_agent = SmartPositionAgent(name="SmartPositionAgent", message_bus=bus)
    position_thread = threading.Thread(target=position_agent.start, daemon=True)


    # Start all agent threads
    cielo_thread.start()
    data_processor_thread.start()
    data_validator_thread.start()
    data_integrity_thread.start()
    type_validator_thread.start()
    value_range_thread.start()
    wallet_behavior_thread.start()
    volume_thread.start()
    position_thread.start()


    # Start each agent in its own thread
    cielo_thread = threading.Thread(target=cielo_agent.start, daemon=True)


    cielo_thread.start()

    # Keep the main thread alive indefinitely
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
