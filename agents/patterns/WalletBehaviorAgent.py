import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from agents.base.agent import BaseAgent


class WalletBehaviorAgent(BaseAgent):
    """
    Specialized agent that analyzes wallet behavior patterns in token transactions.
    This agent tracks how wallets interact with tokens over time to identify
    significant patterns like accumulation, distribution, or wash trading.
    """

    def __init__(self, name, message_bus):
        super().__init__(name, message_bus)
        self.logger = logging.getLogger(self.name)
        # Track wallet activities over time
        self.wallet_history = defaultdict(list)
        # Time window for pattern analysis (in seconds)
        self.analysis_window = 3600  # 1 hour

    def start(self):
        self.logger.info(f"[{self.name}] WalletBehaviorAgent starting.")
        while True:
            # Get messages that passed range validation
            messages = self.message_bus.get_messages("RangeValidationChannel")
            if messages:
                for msg in messages:
                    self._update_wallet_history(msg)
                    patterns = self._analyze_wallet_patterns(msg['wallet_address'])
                    if patterns:
                        # Add pattern information to the transaction
                        msg['detected_patterns'] = patterns
                        self.message_bus.send_message("PatternChannel", msg)
            time.sleep(1)

    def _update_wallet_history(self, transaction):
        """
        Updates the history of wallet activities, maintaining a time-windowed record
        of transactions for each wallet.
        """
        wallet = transaction['wallet_address']
        current_time = datetime.now()

        # Add new transaction to wallet history
        self.wallet_history[wallet].append({
            'timestamp': current_time,
            'value': transaction['value'],
            'type': transaction.get('transaction_type', 'unknown')
        })

        # Remove old transactions outside our analysis window
        cutoff_time = current_time - timedelta(seconds=self.analysis_window)
        self.wallet_history[wallet] = [
            tx for tx in self.wallet_history[wallet]
            if tx['timestamp'] > cutoff_time
        ]

    def _analyze_wallet_patterns(self, wallet_address):
        """
        Analyzes the transaction history of a wallet to identify behavior patterns.
        Returns a list of detected patterns with their confidence levels.
        """
        patterns = []
        history = self.wallet_history[wallet_address]

        if not history:
            return patterns

        # Calculate key metrics
        transaction_count = len(history)
        total_value = sum(tx['value'] for tx in history)
        avg_value = total_value / transaction_count if transaction_count > 0 else 0

        # Pattern: High Frequency Trading
        if self._detect_high_frequency(history):
            patterns.append({
                'type': 'high_frequency_trading',
                'confidence': 0.85,
                'details': {
                    'transaction_count': transaction_count,
                    'timeframe': f"{self.analysis_window} seconds"
                }
            })

        # Pattern: Large Position Accumulation
        if self._detect_accumulation(history):
            patterns.append({
                'type': 'accumulation',
                'confidence': 0.75,
                'details': {
                    'total_value': total_value,
                    'avg_value': avg_value
                }
            })

        # Pattern: Distribution
        if self._detect_distribution(history):
            patterns.append({
                'type': 'distribution',
                'confidence': 0.80,
                'details': {
                    'transaction_pattern': 'multiple_small_sells'
                }
            })

        return patterns

    def _detect_high_frequency(self, history):
        """Detects if wallet is engaging in high-frequency trading."""
        if len(history) < 5:
            return False

        # Calculate average time between transactions
        timestamps = [tx['timestamp'] for tx in history]
        time_diffs = []
        for i in range(1, len(timestamps)):
            diff = (timestamps[i] - timestamps[i - 1]).total_seconds()
            time_diffs.append(diff)

        avg_time_between = sum(time_diffs) / len(time_diffs)
        return avg_time_between < 60  # Less than 1 minute between trades

    def _detect_accumulation(self, history):
        """Detects if wallet is accumulating a position."""
        if len(history) < 3:
            return False

        # Look for increasing position size
        buy_count = sum(1 for tx in history if tx.get('type') == 'buy')
        total_transactions = len(history)

        return buy_count / total_transactions > 0.8  # 80% of transactions are buys

    def _detect_distribution(self, history):
        """Detects if wallet is distributing tokens."""
        if len(history) < 3:
            return False

        # Look for multiple small sell transactions
        sell_count = sum(1 for tx in history if tx.get('type') == 'sell')
        total_transactions = len(history)

        return sell_count / total_transactions > 0.8  # 80% of transactions are sells