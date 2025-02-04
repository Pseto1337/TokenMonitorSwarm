# agents/collection/cielo_agent.py
import asyncio
import json
import logging
from datetime import datetime
import websockets
from websockets.exceptions import ConnectionClosed

from agents.base.agent import BaseAgent
from core.config import settings

logger = logging.getLogger('CieloAgent')

class CieloAgent(BaseAgent):
    """
    Connects to the Cielo WebSocket feed using settings,
    subscribes to the feed, and forwards raw swap transaction data
    to the "RawDataChannel" on the message bus.
    """
    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.ws_url = settings.CIELO_WS_URL
        self.api_key = settings.CIELO_API_KEY
        self.filters = settings.CIELO_FILTERS

        self.websocket = None
        self.active_subscriptions = set()
        self._shutdown_event = asyncio.Event()
        logger.info("CieloAgent initialized.")

    async def _connect_with_retry(self, initial_delay: float = 1.0) -> None:
        delay = initial_delay
        attempt = 0
        while not self._shutdown_event.is_set():
            try:
                attempt += 1
                logger.info(f"Attempt {attempt} to connect to Cielo WebSocket...")
                self.websocket = await websockets.connect(
                    self.ws_url,
                    extra_headers={'X-API-KEY': self.api_key},
                    ping_interval=30,
                    ping_timeout=10,
                    close_timeout=5
                )
                await self._subscribe()
                logger.info("Successfully connected to Cielo WebSocket feed.")
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt} failed: {e}")
                logger.info(f"Retrying in {delay:.1f} seconds...")
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff

    async def _subscribe(self):
        """Subscribe to the feed using the configured filters."""
        subscription = {
            "type": "subscribe_feed",
            "filter": self.filters
        }
        await self.websocket.send(json.dumps(subscription))
        self.active_subscriptions.add('feed')
        logger.info(f"Subscribed to feed with filters: {self.filters}")

    def _process_transaction(self, data: dict):
        """
        Minimal processing: simply returns the raw data.
        Further analysis will be handled by a separate Pattern Analysis Agent.
        """
        logger.debug("Received raw transaction data for forwarding.")
        return data

    async def _handle_websocket_message(self, message: str) -> None:
        if not message.strip():
            logger.debug("Received an empty message. Skipping.")
            return
        try:
            data = json.loads(message)
            if data.get('type') == 'tx':
                transaction_data = data.get('data', {})
                if transaction_data.get('tx_type') == 'swap':
                    # Forward raw transaction data to RawDataChannel
                    raw_data = self._process_transaction(transaction_data)
                    self.message_bus.send_message("RawDataChannel", json.dumps(raw_data))
                    logger.debug("Forwarded raw transaction data to RawDataChannel.")
        except Exception as e:
            logger.error(f"Error handling websocket message: {e}", exc_info=True)

    async def _close_websocket(self) -> None:
        if not self.websocket:
            return
        try:
            for subscription in list(self.active_subscriptions):
                try:
                    await asyncio.wait_for(
                        self.websocket.send(json.dumps({"type": f"unsubscribe_{subscription}"})),
                        timeout=2.0
                    )
                    self.active_subscriptions.remove(subscription)
                except Exception as e:
                    logger.error(f"Error unsubscribing from {subscription}: {e}")
            await asyncio.sleep(0.1)
            try:
                await asyncio.wait_for(self.websocket.close(), timeout=10.0)
                logger.info("WebSocket closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        finally:
            self.websocket = None

    async def run_async(self):
        try:
            await self._connect_with_retry()
            async for message in self.websocket:
                if self._shutdown_event.is_set():
                    break
                await self._handle_websocket_message(message)
        except ConnectionClosed as e:
            logger.warning(f"WebSocket connection closed: {e}. Reconnecting...")
            self.websocket = None
            await asyncio.sleep(5)
            await self.run_async()
        except Exception as e:
            logger.error(f"Error in CieloAgent run loop: {e}", exc_info=True)
            await asyncio.sleep(5)
            await self.run_async()
        finally:
            await self._close_websocket()

    def start(self):
        """Run the asynchronous agent loop."""
        logger.info(f"[{self.name}] CieloAgent starting.")
        asyncio.run(self.run_async())
